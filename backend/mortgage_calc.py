'''
this calculator assumes a "SHPITZER" return system: the monthly return is fixed under fixed conditions.
'''

import numpy as np
import humanize
from abc import ABC, abstractmethod

class BaseMortgage(ABC):
    """Base class for all mortgage types."""
    @abstractmethod
    def __init__(self, principal, term_years):
        self.total_loan_value = principal
        self.principal = principal               # Principal amount in ILS
        self.term_years = term_years             # Loan term in years
        self.term_months = term_years * 12
        self.amortization_schedule = None

    def _calc_monthly_payment(self, interest_rate, principal, term_months):
        '''
        this method is the core logic of the calculator.
        it implements the annuity formula for a series of payments, a basic formula in finance.
        '''
        n = term_months
        mr = interest_rate / 12 / 100 # monthly interest rate
        payment = principal * (mr * (1 + mr) ** n) / ((1 + mr) ** n - 1)
        return payment

    def get_total_remaining_liabilities(self, current_period):
        """Calculate total remaining liabilities (sum of future payments) from the given period onward."""
        if self.amortization_schedule is None:
            raise ValueError("Amortization schedule is not generated. Please call calc_amortization_schedule() first.")
        remaining_payments = sum(entry["payment"] for entry in self.amortization_schedule if entry["period"] >= current_period)
        return remaining_payments

    def get_total_interest_paid(self, current_period):
        """Calculate the total interest paid over the loan term."""
        if self.amortization_schedule is None:
            raise ValueError("Amortization schedule is not generated. Please call calc_amortization_schedule() first.")
        total_interest = sum(entry["interest"] for entry in self.amortization_schedule  if entry["period"] >= current_period)
        return total_interest

    def get_payment_list(self):
        return [int(period['total_payment'].replace(",", "")) for period in self.amortization_schedule]

    def calc_amortization_schedule(self):
        """
        Template method to calculate the full amortization schedule.
        Loops over each period and delegates period-specific parameter calculations.

        first pay according to current balance, then calc remaining principal
        """
        schedule = []
        current_balance = self.principal

        for period in range(1, self.term_months + 1):
            remaining_term = self.term_months - period + 1
            period_interest_rate = self._get_period_interest_rate(period)  # child class specific
            monthly_payment = self._calc_monthly_payment(period_interest_rate, current_balance, remaining_term)
            # Compute interest and principal parts
            monthly_rate = period_interest_rate / 12 / 100
            interest_payment = current_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            # Update the balance (subclasses can override _update_balance if needed)
            new_balance = self._update_balance(current_balance, principal_payment, period)

            # Record details for this period
            schedule.append({
                "period": period,
                "total_payment": humanize.intcomma(int(monthly_payment)),
                "interest_payment": humanize.intcomma(int(interest_payment)),
                "principal_payment": humanize.intcomma(int(principal_payment)),
                "remaining_balance": humanize.intcomma(int(new_balance)),
                "current_interest_rate": humanize.intcomma(int(period_interest_rate)),
            })
            current_balance = new_balance

        self.amortization_schedule = schedule
        return schedule

    @abstractmethod
    def _get_period_interest_rate(self, period):
        """
        Abstract method to return period-specific parameters.
        Expected to return a dict, e.g.: {"interest_rate": ...}
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def _update_balance(self, current_balance, principal_payment, period):
        """
        Default balance update: simply subtract the principal payment.
        Subclasses may override if needed.
        """
        return current_balance - principal_payment


class FixedUnlinked(BaseMortgage):
    """Fixed-interest unlinked mortgage (constant interest rate, no CPI linkage)."""
    def __init__(self, principal, term_years, interest_rate):
        super().__init__(principal, term_years)
        self.interest_rate = interest_rate

    def _get_period_interest_rate(self, period):
        return self.interest_rate


class PrimeUnlinked(BaseMortgage):
    """Prime-linked variable mortgage using a list of prime rates for each period."""
    def __init__(self, principal, term_years, prime_rate_list, spread):
        super().__init__(principal, term_years)
        self.spread = spread
        self.prime_rate_list = prime_rate_list  # List of prime rates for each month

    def _get_period_interest_rate(self, period):
        current_prime_rate = self.prime_rate_list[period - 1]
        return current_prime_rate + self.spread


class LinkedFixed(BaseMortgage):
    """
    CPI-linked mortgage that uses the base schedule loop.
    The monthly payment is computed using the fixed real interest rate,
    and the remaining balance is updated by converting the real balance
    to nominal terms using the current CPI relative to a baseline.
    """

    def __init__(self, principal, term_years, real_interest_rate, cpi_list):
        super().__init__(principal, term_years)
        self.real_interest_rate = real_interest_rate  # Fixed real annual interest rate (percent)
        self.cpi_list = cpi_list  # List of CPI rise values for each month
        self.real_balance = principal  # Track the balance in real terms

    def _get_period_interest_rate(self, period):
        return self.real_interest_rate

    def _update_balance(self, current_balance, principal_payment, period):
        """
        first pay to reduce principal a then apply cpi rise on the remaining principal
        """
        self.real_balance -= principal_payment
        inflation_factor = self.cpi_list[period - 1] / 100
        return self.real_balance * (1 + inflation_factor)


class AdjustableUnlinked(BaseMortgage):
    """5-Year Adjustable (Mishtana) mortgage: fixed for a period then adjustable."""
    def __init__(self, principal, term_years, initial_interest_rate, reference_index, fixed_period=5):
        super().__init__(principal, term_years)
        self.initial_interest_rate = initial_interest_rate  # Rate for the initial fixed period
        self.fixed_period = fixed_period  # Fixed period length in years
        self.reference_index = reference_index  # List of rates for each adjustment period after the fixed phase

    def _get_period_interest_rate(self, period):
        if period <= self.fixed_period * 12:
            return self.initial_interest_rate
        else:
            adjustment_offset = period - (self.fixed_period * 12)
            block = (adjustment_offset - 1) // (self.fixed_period * 12)
            if block < len(self.reference_index):
                return self.reference_index[block]
            else:
                return self.reference_index[-1]


class Adjustablelinked(BaseMortgage):
    """5-Year Adjustable (Mishtana) mortgage: fixed for a period then adjustable."""
    def __init__(self, principal, term_years, initial_interest_rate, reference_index, real_balance, cpi_list, fixed_period=5):
        super().__init__(principal, term_years)
        self.initial_interest_rate = initial_interest_rate  # Rate for the initial fixed period
        self.fixed_period = fixed_period  # Fixed period length in years
        self.reference_index = reference_index  # List of rates for each adjustment period after the fixed phase
        self.real_balance = real_balance
        self.cpi_list = cpi_list

    def _get_period_interest_rate(self, period):
        if period <= self.fixed_period * 12:
            return self.initial_interest_rate
        else:
            adjustment_offset = period - (self.fixed_period * 12)
            block = (adjustment_offset - 1) // (self.fixed_period * 12)
            if block < len(self.reference_index):
                return self.reference_index[block]
            else:
                return self.reference_index[-1]


    def _update_balance(self, current_balance, principal_payment, period):
        """
        first pay to reduce principal a then apply cpi rise on the remaining principal
        """
        self.real_balance -= principal_payment
        inflation_factor = self.cpi_list[period - 1] / 100
        return self.real_balance * (1 + inflation_factor)


class MultiTrackMortgage:
    """
    Composite mortgage that aggregates multiple mortgage tracks.
    It allows you to view each individual amortization schedule as well as a combined total schedule.
    """
    def __init__(self, **mortgage_tracks):
        """
        Initialize with named mortgage tracks.
        For example:
            multi = MultiTrackMortgage(fixed=fixed_mortgage, prime=prime_mortgage)
        """
        self.mortgage_tracks = mortgage_tracks
        self.calc_total_loan_value()
        self.calc_amortization_schedule()

    def calc_total_loan_value(self):
        self.total_loan_value = 0
        for name, track in self.mortgage_tracks.items():
            self.total_loan_value += track.total_loan_value

    def calc_individual_schedules(self):
        """
        Calculate the amortization schedule for each individual mortgage track.
        """
        for name, track in self.mortgage_tracks.items():
            track.calc_amortization_schedule()

    def calc_amortization_schedule(self):
        """
        Aggregate the individual amortization schedules into one total schedule.
        For each period (as found in any track), sum numeric values for keys except 'period'
        and 'current_interest_rate'. If a track has ended by a given period, it is ignored.
        """
        self.calc_individual_schedules()
        aggregated = {}
        ignored_keys = ["period", "current_interest_rate"]

        # Iterate over each track's schedule.
        for track in self.mortgage_tracks.values():
            for entry in track.amortization_schedule:
                # Convert the humanized 'period' string back to an integer.
                period = entry["period"]
                if period not in aggregated:
                    # Initialize an entry for this period.
                    aggregated[period] = {"period": period}
                    # Set initial sums for every key except 'period' and 'current_interest_rate'
                    for key in entry:
                        if key not in ignored_keys:
                            aggregated[period][key] = 0

                # Sum up values from this entry (ignoring 'current_interest_rate')
                for key, value in entry.items():
                    if key in ignored_keys:
                        continue
                    aggregated[period][key] += int(value.replace(",", ""))

        # Build a sorted list of aggregated entries.
        total_schedule = []
        for period in sorted(aggregated.keys()):
            entry = aggregated[period]
            # Humanize the period number.
            entry["period"] = humanize.intcomma(entry["period"])
            # Optionally humanize other numeric values.
            for key in entry:
                if key != "period":
                    entry[key] = humanize.intcomma(entry[key])
            total_schedule.append(entry)

        self.amortization_schedule = total_schedule
        return total_schedule

    def get_track_schedule(self, track_name):
        """
        Retrieve the amortization schedule for a specific mortgage track.
        """
        if track_name in self.mortgage_tracks:
            return self.mortgage_tracks[track_name].amortization_schedule
        else:
            raise ValueError(f"Track '{track_name}' not found.")

    def get_total_remaining_liabilities(self, current_period):
        """
        Calculate total remaining liabilities (sum of future payments) across all tracks.
        """
        total_liabilities = 0
        for track in self.mortgage_tracks.values():
            total_liabilities += track.get_total_remaining_liabilities(current_period)
        return total_liabilities

    def get_total_interest_paid(self, current_period):
        """
        Calculate the total interest paid over the loan term across all tracks.
        """
        total_interest = 0
        for track in self.mortgage_tracks.values():
            total_interest += track.get_total_interest_paid(current_period)
        return total_interest

    def get_payment_list(self):
        track_lists = [track.get_payment_list() for track in self.mortgage_tracks.values()]
        return [sum(monthly) for monthly in zip(*track_lists)]



def mortgage_factory(mortgage_params):
    """Builds a MultiTrackMortgage from a dictionary of mortgage parameters.
    Each key in mortgage_params is a track name and its value is a dict with parameters.
    Expected keys in the parameter dict include:
        - type: 'fixed', 'prime', 'linked', 'adjustable', or 'adjustablelinked'
        - principal: loan principal
        - term_years: loan term in years
        - interest_rate: annual interest rate (in percent)
    For 'prime' type, also include 'spread'.
    """
    MORTGAGE_TYPES = {
        'fixed': FixedUnlinked,
        'prime': PrimeUnlinked,
        'linked': LinkedFixed,
        'adjustable': AdjustableUnlinked,
        'adjustablelinked': Adjustablelinked
    }

    mortgage_tracks = {}
    for name, params in mortgage_params.items():
        m_type = params.get("type", "").lower()
        mortgage_class = MORTGAGE_TYPES.get(m_type)
        if not mortgage_class:
            print(f"Unknown mortgage type for {name}.")
            continue

        # Remove 'type' from parameters
        init_params = {k: v for k, v in params.items() if k != "type"}

        # Handle special case for 'prime' to generate prime_rate_list if needed
        if m_type == "prime":
            term = init_params["term_years"]
            interest = init_params["interest_rate"]
            init_params["prime_rate_list"] = [interest] * (term * 12)
            del init_params["interest_rate"]

        try:
            track = mortgage_class(**init_params)
        except Exception as e:
            print(f"Error creating mortgage track {name}: {e}")
            continue

        mortgage_tracks[name] = track
    return MultiTrackMortgage(**mortgage_tracks)

if __name__ == "__main__":
    # Simple test for mortgage_factory
    mortgage_params = {
        "fixed_mortgage": {
            "type": "fixed",
            "principal": 800000,
            "term_years": 30,
            "interest_rate": 4.0
        },
        "prime_mortgage": {
            "type": "prime",
            "principal": 800000,
            "term_years": 30,
            "interest_rate": 4.5,
            "spread": -0.5
        }
    }

    multi_mortgage = mortgage_factory(mortgage_params)
    for name, track in multi_mortgage.mortgage_tracks.items():
        print(f"Amortization schedule for {name}:")
        schedule = track.calc_amortization_schedule()
        # Print only the first 3 periods for brevity
        print(schedule[:3])
