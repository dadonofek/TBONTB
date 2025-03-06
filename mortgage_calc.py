'''
this calculator assumes a "SHPITZER" return system: the monthly return is fixed under fixed conditions.
'''

import humanize
from abc import ABC, abstractmethod

class BaseMortgage(ABC):
    """Base class for all mortgage types."""
    @abstractmethod
    def __init__(self, principal, term_years):
        self.principal = principal               # Principal amount in ILS
        self.term_years = term_years             # Loan term in years
        self.term_months = term_years * 12
        self.amortization_schedule = None

    def _calc_monthly_payment(self, interest_rate, principal=None, term_months=None):
        if principal is None:
            principal = self.principal
        if term_months is None:
            term_months = self.term_months
        n = term_months
        monthly_rate = interest_rate / 12 / 100
        payment = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
        return payment

    def get_total_remaining_liabilities(self, current_period):
        """Calculate total remaining liabilities (sum of future payments) from the given period onward."""
        if self.amortization_schedule is None:
            raise ValueError("Amortization schedule is not generated. Please call _calc_amortization_schedule() first.")
        remaining_payments = sum(entry["payment"] for entry in self.amortization_schedule if entry["period"] >= current_period)
        return remaining_payments

    def get_total_interest_paid(self):
        """Calculate the total interest paid over the loan term."""
        if self.amortization_schedule is None:
            raise ValueError("Amortization schedule is not generated. Please call _calc_amortization_schedule() first.")
        total_interest = sum(entry["interest"] for entry in self.amortization_schedule)
        return total_interest

    def _calc_amortization_schedule(self):
        """Return the amortization schedule with principal and interest breakdown per period."""
        raise NotImplementedError("Subclasses should implement this method.")


class FixedUnlinked(BaseMortgage):
    """Fixed-interest unlinked mortgage (constant interest rate, no CPI linkage)."""
    def __init__(self, principal, term_years, interest_rate):
        super().__init__(principal, term_years)
        self.interest_rate = interest_rate

    def _calc_FixedUnlinked_monthly_payment(self):
        """Calculate fixed monthly payment using the standard mortgage formula."""
        payment = self._calc_monthly_payment(interest_rate=self.interest_rate)
        return payment

    def _calc_amortization_schedule(self):
        """Generate the amortization schedule as a list of payment details per month."""
        schedule = []
        monthly_payment = self._calc_FixedUnlinked_monthly_payment()
        monthly_rate = self.interest_rate / 12 / 100
        remaining_balance = self.principal

        for period in range(1, self.term_months + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment

            schedule.append({
                "period": humanize.intcomma(int(period)),
                "payment": humanize.intcomma(int(monthly_payment)),
                "interest": humanize.intcomma(int(interest_payment)),
                "principal": humanize.intcomma(int(principal_payment)),
                "remaining_balance": humanize.intcomma(int(remaining_balance)),
                "current_interest_rate": humanize.intcomma(int(self.interest_rate))
            })
        self.amortization_schedule = schedule
        return schedule


class Prime(BaseMortgage):
    """Prime-linked variable mortgage using a list of prime rates for each period."""
    def __init__(self, principal, term_years, prime_rate_list, spread):
        super().__init__(principal, term_years)
        self.spread = spread
        self.prime_rate_list = prime_rate_list  # List of prime rates for each month

    def _calc_Prime_monthly_payment(self, current_balance, current_period=1):
        remaining_term = self.term_months - (current_period - 1)
        current_prime_rate = self.prime_rate_list[current_period - 1]
        current_interest_rate = (current_prime_rate + self.spread)
        return self._calc_monthly_payment(interest_rate=current_interest_rate,
                                            principal=current_balance,
                                            term_months=remaining_term)

    def _calc_amortization_schedule(self):
        schedule = []
        current_balance = self.principal
        n = self.term_months

        for period in range(1, n + 1):
            payment = self._calc_Prime_monthly_payment(current_balance=current_balance, current_period=period)
            current_prime_rate = self.prime_rate_list[period - 1]
            current_interest_rate = current_prime_rate + self.spread
            monthly_rate = current_interest_rate / 12

            interest_payment = current_balance * monthly_rate / 100
            principal_payment = payment - interest_payment
            current_balance -= principal_payment

            schedule.append({
                "period": humanize.intcomma(int(period)),
                "payment": humanize.intcomma(int(payment)),
                "interest": humanize.intcomma(int(interest_payment)),
                "principal": humanize.intcomma(int(principal_payment)),
                "remaining_balance": humanize.intcomma(int(current_balance)),
                "current_interest_rate": humanize.intcomma(int(current_interest_rate))
            })
        self.amortization_schedule = schedule
        return schedule


class Adjustable(BaseMortgage):
    """5-Year Adjustable (Mishtana) mortgage (fixed for a period then adjustable)."""
    def __init__(self, principal, term_years, initial_interest_rate, margin, fixed_period = 5):
        super().__init__(principal, term_years)
        self.initial_interest_rate = initial_interest_rate  # Interest rate for the initial fixed period
        self.margin = margin                # Fixed margin added to the benchmark rate after fixed period
        self.fixed_period = fixed_period    # Period (in years) for the fixed rate phase


class MultiTrackMortgage:
    """
    Composite mortgage that aggregates different mortgage tracks.
    Each track is an instance of a Mortgage subclass.
    """
    def __init__(self, **mortgage_tracks):
        # Example usage: MultiTrackMortgage(fixed=FixedUnlinked(...), prime=Prime(...), ...)
        self.mortgage_tracks = mortgage_tracks

    def calc_total_monthly_payment(self):
        """Aggregate monthly payments from all tracks."""
        return sum(track._calc_monthly_payment() for track in self.mortgage_tracks.values())


if __name__ == "__main__":
    principal = 1000000
    term_years = 30

    fixed = FixedUnlinked(principal=principal,
                          term_years=term_years,
                          interest_rate=5)

    prime_rate_list = [5.5] * (term_years * 12)
    prime = Prime(principal=principal,
                  term_years=term_years,
                  prime_rate_list = prime_rate_list,
                  spread=-0.5)

    print(fixed._calc_amortization_schedule())
    print(prime._calc_amortization_schedule())
    print(fixed.amortization_schedule == prime.amortization_schedule)
