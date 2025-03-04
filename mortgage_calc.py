


class BaseMortgage:
    """Base class for all mortgage types."""
    def __init__(self, amount: float, term_years: int):
        self.amount = amount            # Principal amount in ILS
        self.term_years = term_years    # Loan term in years

    def get_monthly_payment(self):
        """Placeholder for monthly payment calculation."""
        raise NotImplementedError("Subclasses should implement this method.")

    def get_total_remaining_liabilities(self, current_period: int):
        """Return the total remaining liabilities (principal + interest) from the current period to the end."""
        raise NotImplementedError("Subclasses should implement this method.")

    def get_total_interest_paid(self):
        """Return the total interest paid over the full term of the mortgage."""
        raise NotImplementedError("Subclasses should implement this method.")

    def get_amortization_schedule(self):
        """Return the amortization schedule with principal and interest breakdown per period."""
        raise NotImplementedError("Subclasses should implement this method.")


class FixedUnlinked(BaseMortgage):
    """Fixed-interest unlinked mortgage (constant interest rate, no CPI linkage)."""
    def __init__(self, amount: float, term_years: int, interest_rate: float):
        super().__init__(amount, term_years)
        self.interest_rate = interest_rate  # Annual fixed interest rate (as a decimal, e.g., 0.05 for 5%)

    def get_monthly_payment(self):
        """Calculate fixed monthly payment using the standard mortgage formula."""
        n = self.term_years * 12
        monthly_rate = self.interest_rate / 12
        payment = self.amount * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
        return payment

    def get_amortization_schedule(self):
        """Generate the amortization schedule as a list of payment details per month."""
        schedule = []
        monthly_payment = self.get_monthly_payment()
        monthly_rate = self.interest_rate / 12
        remaining_balance = self.amount
        n = self.term_years * 12

        for period in range(1, n + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment

            # Adjust final period to account for rounding errors.
            if period == n:
                principal_payment = remaining_balance
                monthly_payment = interest_payment + principal_payment
                remaining_balance = 0.0
            else:
                remaining_balance -= principal_payment

            schedule.append({
                "period": period,
                "payment": monthly_payment,
                "interest": interest_payment,
                "principal": principal_payment,
                "remaining_balance": remaining_balance
            })
        return schedule

    def get_total_interest_paid(self):
        """Calculate the total interest paid over the loan term."""
        schedule = self.get_amortization_schedule()
        total_interest = sum(entry["interest"] for entry in schedule)
        return total_interest

    def get_total_remaining_liabilities(self, current_period: int):
        """Calculate total remaining liabilities (sum of future payments) from the given period onward."""
        schedule = self.get_amortization_schedule()
        remaining_payments = sum(entry["payment"] for entry in schedule if entry["period"] >= current_period)
        return remaining_payments


class Prime(BaseMortgage):
    """Prime-linked variable mortgage (rate tied to the Bank of Israel's prime rate)."""
    def __init__(self, amount: float, term_years: int, prime_rate: float, spread: float):
        super().__init__(amount, term_years)
        self.prime_rate = prime_rate    # Bank of Israel's prime rate
        self.spread = spread            # Adjustment (e.g., -0.5 for "Prime – 0.5%")


class CPI(BaseMortgage):
    """CPI-linked (Madad) mortgage (principal adjusted for inflation)."""
    def __init__(self, amount: float, term_years: int, interest_rate: float, inflation_rate: float):
        super().__init__(amount, term_years)
        self.interest_rate = interest_rate  # Base interest rate
        self.inflation_rate = inflation_rate  # Expected inflation rate for indexation


class Adjustable(BaseMortgage):
    """5-Year Adjustable (Mishtana) mortgage (fixed for a period then adjustable)."""
    def __init__(self, amount: float, term_years: int, initial_interest_rate: float, margin: float, fixed_period: int = 5):
        super().__init__(amount, term_years)
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

    def get_total_monthly_payment(self):
        """Aggregate monthly payments from all tracks."""
        return sum(track.get_monthly_payment() for track in self.mortgage_tracks.values())