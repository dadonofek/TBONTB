import unittest
from mortgage_calc import FixedUnlinked, PrimeUnlinked, LinkedFixed, MultiTrackMortgage

class TestMortgageCalc(unittest.TestCase):

    def setUp(self):
        # Use a constant principal and term for tests.
        self.principal = 1000000
        self.term_years = 30


        self.months = self.term_years * 12

        # FixedUnlinked: constant 5% interest
        self.fixed_rate = 5
        self.fixed_mortgage = FixedUnlinked(principal=self.principal,
                                            term_years=self.term_years,
                                            interest_rate=self.fixed_rate)

        # PrimeUnlinked: prime rate list with constant value and a spread of -0.5%
        self.prime_rate_list = [5.5] * self.months
        self.spread = -0.5
        self.prime_mortgage = PrimeUnlinked(principal=self.principal,
                                            term_years=self.term_years,
                                            prime_rate_list=self.prime_rate_list,
                                            spread=self.spread)

        # LinkedFixed: real rate mortgage with a constant CPI (baseline) so no effective inflation change.
        self.real_interest_rate = 5
        self.cpi_list = [100] * self.months  # constant CPI baseline
        self.linked_mortgage = LinkedFixed(principal=self.principal,
                                           term_years=self.term_years,
                                           real_interest_rate=self.real_interest_rate,
                                           cpi_list=self.cpi_list)

        # MultiTrackMortgage with two tracks (fixed and prime)
        self.multi = MultiTrackMortgage(fixed=self.fixed_mortgage, prime=self.prime_mortgage)

    def test_fixed_mortgage_schedule(self):
        schedule = self.fixed_mortgage.calc_amortization_schedule()
        # Verify schedule length
        self.assertEqual(len(schedule), self.months)
        # Check first period entry contains expected keys.
        expected_keys = {"period", "total_payment", "interest_payment", "principal_payment", "remaining_balance", "current_interest_rate"}
        self.assertTrue(expected_keys.issubset(schedule[0].keys()))

    def test_linked_mortgage_schedule(self):
        schedule = self.linked_mortgage.calc_amortization_schedule()
        self.assertEqual(len(schedule), self.months)
        expected_keys = {"period", "total_payment", "interest_payment", "principal_payment", "remaining_balance", "current_interest_rate"}
        self.assertTrue(expected_keys.issubset(schedule[0].keys()))

    def test_multi_track_schedule(self):
        total_schedule = self.multi.calc_total_amortization_schedule()
        # The aggregated schedule length should equal the maximum number of periods among tracks.
        self.assertEqual(len(total_schedule), self.months)

        # Iterate over all periods and verify that, for each period, the total_payment
        # equals the sum of the fixed and prime payments.
        for i in range(self.months):
            print(f'month = {i}')
            fixed_payment = int(self.fixed_mortgage.amortization_schedule[i]["total_payment"].replace(",", ""))
            prime_payment = int(self.prime_mortgage.amortization_schedule[i]["total_payment"].replace(",", ""))
            total_payment = int(total_schedule[i]["total_payment"].replace(",", ""))
            self.assertEqual(total_payment, fixed_payment + prime_payment,
                             msg=f"Mismatch at period {i + 1}: fixed ({fixed_payment}) + prime ({prime_payment}) != total ({total_payment})")

if __name__ == "__main__":
    unittest.main()