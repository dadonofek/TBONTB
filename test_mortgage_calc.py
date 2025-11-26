import unittest
from mortgage_calc import (
    FixedUnlinked, PrimeUnlinked, LinkedFixed, MultiTrackMortgage,
    AdjustableUnlinked, AdjustableLinked, mortgage_factory
)

# Helper function for parsing payment strings
def parse_payment(value_str):
    return int(value_str.replace(",", ""))

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

        # AdjustableUnlinked
        self.adjustable_unlinked_fixed_period = 5  # years
        self.adjustable_unlinked_initial_rate = 3
        self.adjustable_unlinked_reference_index = [3.5, 4.0, 4.5]  # Example index values
        self.adjustable_unlinked_mortgage = AdjustableUnlinked(
            principal=self.principal,
            term_years=self.term_years,
            fixed_period=self.adjustable_unlinked_fixed_period, # Changed fixed_period_years to fixed_period
            initial_interest_rate=self.adjustable_unlinked_initial_rate,
            reference_index=self.adjustable_unlinked_reference_index
        )

        # AdjustableLinked
        self.adjustable_linked_fixed_period = 5  # years
        self.adjustable_linked_initial_rate = 3
        self.adjustable_linked_reference_index = [3.5, 4.0, 4.5]  # Example index values
        self.adjustable_linked_mortgage = AdjustableLinked(
            principal=self.principal,
            term_years=self.term_years,
            fixed_period=self.adjustable_linked_fixed_period, # Changed fixed_period_years to fixed_period
            initial_interest_rate=self.adjustable_linked_initial_rate,
            reference_index=self.adjustable_linked_reference_index,
            cpi_list=self.cpi_list  # Using the same constant CPI list for baseline
        )

        # MultiTrackMortgage with all five tracks
        self.multi = MultiTrackMortgage(
            fixed=self.fixed_mortgage,
            prime=self.prime_mortgage,
            linked=self.linked_mortgage,
            adjustable_unlinked=self.adjustable_unlinked_mortgage,
            adjustable_linked=self.adjustable_linked_mortgage
        )

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
        total_schedule = self.multi.amortization_schedule # Corrected to access attribute
        # The aggregated schedule length should equal the maximum number of periods among tracks.
        self.assertEqual(len(total_schedule), self.months)

        # Iterate over all periods and verify that, for each period, the total_payment
        # equals the sum of all individual track payments.
        for i in range(self.months):
            expected_sum_of_payments = (
                parse_payment(self.fixed_mortgage.amortization_schedule[i]["total_payment"]) +
                parse_payment(self.prime_mortgage.amortization_schedule[i]["total_payment"]) +
                parse_payment(self.linked_mortgage.amortization_schedule[i]["total_payment"]) +
                parse_payment(self.adjustable_unlinked_mortgage.amortization_schedule[i]["total_payment"]) +
                parse_payment(self.adjustable_linked_mortgage.amortization_schedule[i]["total_payment"])
            )
            actual_total_payment = parse_payment(total_schedule[i]["total_payment"])
            self.assertEqual(actual_total_payment, expected_sum_of_payments,
                             msg=f"Mismatch at period {i + 1}: sum of individual payments != total aggregated payment")

    def test_adjustable_unlinked_schedule(self):
        schedule = self.adjustable_unlinked_mortgage.calc_amortization_schedule()
        # Verify schedule length
        self.assertEqual(len(schedule), self.months)
        # Check first period entry contains expected keys.
        expected_keys = {"period", "total_payment", "interest_payment", "principal_payment", "remaining_balance", "current_interest_rate"}
        self.assertTrue(expected_keys.issubset(schedule[0].keys()))

    def test_adjustable_linked_schedule(self):
        schedule = self.adjustable_linked_mortgage.calc_amortization_schedule()
        # Verify schedule length
        self.assertEqual(len(schedule), self.months)
        # Check first period entry contains expected keys.
        expected_keys = {"period", "total_payment", "interest_payment", "principal_payment", "remaining_balance", "current_interest_rate"}
        self.assertTrue(expected_keys.issubset(schedule[0].keys()))

    def test_zero_interest_fixed_unlinked(self):
        principal = 100000
        term_years = 10
        term_months = term_years * 12
        mortgage = FixedUnlinked(principal=principal, term_years=term_years, interest_rate=0)
        schedule = mortgage.calc_amortization_schedule()

        expected_principal_payment = principal / term_months
        for entry in schedule:
            self.assertEqual(parse_payment(entry["interest_payment"]), 0)
            self.assertEqual(parse_payment(entry["principal_payment"]), round(expected_principal_payment)) # Round due to potential float precision
            self.assertEqual(parse_payment(entry["total_payment"]), round(expected_principal_payment))

    def test_zero_interest_prime_unlinked(self):
        principal = 100000
        term_years = 10
        term_months = term_years * 12
        mortgage = PrimeUnlinked(principal=principal, term_years=term_years, prime_rate_list=[0]*term_months, spread=0)
        schedule = mortgage.calc_amortization_schedule()

        expected_principal_payment = principal / term_months
        for entry in schedule:
            self.assertEqual(parse_payment(entry["interest_payment"]), 0)
            # Allow for small differences due to how _calc_monthly_payment might handle exact zero rate with float division
            self.assertAlmostEqual(parse_payment(entry["principal_payment"]), expected_principal_payment, delta=1)
            self.assertAlmostEqual(parse_payment(entry["total_payment"]), expected_principal_payment, delta=1)

    def test_zero_principal_fixed_unlinked(self):
        mortgage = FixedUnlinked(principal=0, term_years=10, interest_rate=5)
        schedule = mortgage.calc_amortization_schedule()
        for entry in schedule:
            self.assertEqual(parse_payment(entry["total_payment"]), 0)
            self.assertEqual(parse_payment(entry["interest_payment"]), 0)
            self.assertEqual(parse_payment(entry["principal_payment"]), 0)
            self.assertEqual(parse_payment(entry["remaining_balance"]), 0)

    def test_zero_principal_prime_unlinked(self):
        term_months = 10 * 12
        mortgage = PrimeUnlinked(principal=0, term_years=10, prime_rate_list=[5]*term_months, spread=0)
        schedule = mortgage.calc_amortization_schedule()
        for entry in schedule:
            self.assertEqual(parse_payment(entry["total_payment"]), 0)
            self.assertEqual(parse_payment(entry["interest_payment"]), 0)
            self.assertEqual(parse_payment(entry["principal_payment"]), 0)
            self.assertEqual(parse_payment(entry["remaining_balance"]), 0)

    def test_zero_principal_linked_fixed(self):
        term_months = 10 * 12
        mortgage = LinkedFixed(principal=0, term_years=10, real_interest_rate=3, cpi_list=[100]*term_months)
        schedule = mortgage.calc_amortization_schedule()
        for entry in schedule:
            self.assertEqual(parse_payment(entry["total_payment"]), 0)
            self.assertEqual(parse_payment(entry["interest_payment"]), 0)
            self.assertEqual(parse_payment(entry["principal_payment"]), 0)
            self.assertEqual(parse_payment(entry["remaining_balance"]), 0)

    def test_zero_principal_adjustable_unlinked(self):
        mortgage = AdjustableUnlinked(principal=0, term_years=10, initial_interest_rate=3, reference_index=[3.5,4], fixed_period=5)
        schedule = mortgage.calc_amortization_schedule()
        for entry in schedule:
            self.assertEqual(parse_payment(entry["total_payment"]), 0)
            self.assertEqual(parse_payment(entry["interest_payment"]), 0)
            self.assertEqual(parse_payment(entry["principal_payment"]), 0)
            self.assertEqual(parse_payment(entry["remaining_balance"]), 0)

    def test_zero_principal_adjustable_linked(self):
        term_months = 10 * 12
        mortgage = AdjustableLinked(principal=0, term_years=10, initial_interest_rate=3, reference_index=[3.5,4], fixed_period=5, cpi_list=[100]*term_months)
        schedule = mortgage.calc_amortization_schedule()
        for entry in schedule:
            self.assertEqual(parse_payment(entry["total_payment"]), 0)
            self.assertEqual(parse_payment(entry["interest_payment"]), 0)
            self.assertEqual(parse_payment(entry["principal_payment"]), 0)
            self.assertEqual(parse_payment(entry["remaining_balance"]), 0)

    def test_short_term_fixed_unlinked(self):
        principal = 12000
        term_years = 1
        mortgage = FixedUnlinked(principal=principal, term_years=term_years, interest_rate=5)
        schedule = mortgage.calc_amortization_schedule()
        self.assertEqual(len(schedule), 12)
        # Check first payment (example assertions, can be more specific if exact values are pre-calculated)
        self.assertGreater(parse_payment(schedule[0]["total_payment"]), principal / 12)
        # Check last payment
        self.assertEqual(parse_payment(schedule[-1]["remaining_balance"]), 0)
        # Check that total principal paid equals initial principal
        total_principal_paid = sum(parse_payment(entry["principal_payment"]) for entry in schedule)
        self.assertAlmostEqual(total_principal_paid, principal, delta=10) # Increased delta for sum of potential errors

    def test_short_term_prime_unlinked(self):
        principal = 12000
        term_years = 1
        term_months = term_years * 12
        # Example prime rate list for a short term, can be varied
        prime_rate_list = [5.0] * term_months 
        mortgage = PrimeUnlinked(principal=principal, term_years=term_years, prime_rate_list=prime_rate_list, spread=0)
        schedule = mortgage.calc_amortization_schedule()
        self.assertEqual(len(schedule), 12)
        # Check first payment
        self.assertGreater(parse_payment(schedule[0]["total_payment"]), principal / 12)
        # Check last payment
        self.assertEqual(parse_payment(schedule[-1]["remaining_balance"]), 0)
        # Check that total principal paid equals initial principal
        total_principal_paid = sum(parse_payment(entry["principal_payment"]) for entry in schedule)
        self.assertAlmostEqual(total_principal_paid, principal, delta=10) # Increased delta for sum of potential errors

    def test_cpi_effect_on_linked_fixed(self):
        principal = 100000
        term_years = 10
        term_months = term_years * 12
        real_interest_rate = 3

        # Scenario 1: No Inflation
        cpi_list_no_inflation = [100] * term_months
        lf_no_inflation = LinkedFixed(principal=principal, term_years=term_years, 
                                      real_interest_rate=real_interest_rate, cpi_list=cpi_list_no_inflation)
        schedule_lf_no_inflation = lf_no_inflation.calc_amortization_schedule()

        fu_comparison = FixedUnlinked(principal=principal, term_years=term_years, interest_rate=real_interest_rate)
        schedule_fu_comparison = fu_comparison.calc_amortization_schedule()

        # Compare first month's total payment
        self.assertEqual(parse_payment(schedule_lf_no_inflation[0]["total_payment"]),
                         parse_payment(schedule_fu_comparison[0]["total_payment"]))
        # Assert final remaining balance is close to zero for no-inflation case
        self.assertAlmostEqual(parse_payment(schedule_lf_no_inflation[-1]["remaining_balance"]), 0, delta=50)


        # Scenario 2: With Inflation (2% annual)
        cpi_list_with_inflation = [100] * term_months
        annual_inflation = 0.02
        for year in range(term_years):
            for month_in_year in range(12):
                month_index = year * 12 + month_in_year
                if year == 0 and month_in_year == 0: # Baseline CPI
                    cpi_list_with_inflation[month_index] = 100
                elif month_in_year == 0: # Start of a new year, apply annual inflation to previous year's start
                     # Apply annual inflation based on the CPI at the start of the previous year
                    cpi_list_with_inflation[month_index] = cpi_list_with_inflation[(year-1)*12] * (1 + annual_inflation)
                else: # Carry over CPI from previous month within the same year
                    cpi_list_with_inflation[month_index] = cpi_list_with_inflation[month_index-1]
        # Distribute annual increase somewhat evenly for smoother monthly CPI if needed, or keep stepped.
        # For simplicity, using stepped annual increase for this test.
        # A more realistic monthly CPI would be (1+annual_inflation)**(1/12) applied monthly.
        # Let's use a simple stepped annual increase for the test.
        current_cpi = 100
        for i in range(term_months):
            if i > 0 and i % 12 == 0: # Apply annual inflation at the start of each year
                current_cpi *= (1 + annual_inflation)
            cpi_list_with_inflation[i] = current_cpi


        lf_with_inflation = LinkedFixed(principal=principal, term_years=term_years,
                                        real_interest_rate=real_interest_rate, cpi_list=cpi_list_with_inflation)
        schedule_lf_with_inflation = lf_with_inflation.calc_amortization_schedule()

        # Assert that total payment after inflation has taken effect is higher
        # (e.g. check payment at month 25, index 24, after two years of inflation)
        if term_months > 24: 
            payment_no_inflation_month25 = parse_payment(schedule_lf_no_inflation[24]["total_payment"])
            payment_with_inflation_month25 = parse_payment(schedule_lf_with_inflation[24]["total_payment"])
            self.assertGreater(payment_with_inflation_month25, payment_no_inflation_month25)
        
        # Assert final remaining balance is close to zero for with-inflation case
        self.assertAlmostEqual(parse_payment(schedule_lf_with_inflation[-1]["remaining_balance"]), 0, delta=50)


    def test_cpi_effect_on_adjustable_linked(self):
        principal = 100000
        term_years = 10
        term_months = term_years * 12
        initial_rate = 3
        reference_index = [3.5, 4.0] 
        fixed_period = 5

        # Scenario 1: No Inflation
        cpi_list_no_inflation = [100] * term_months
        al_no_inflation = AdjustableLinked(principal=principal, term_years=term_years, 
                                           initial_interest_rate=initial_rate, reference_index=reference_index,
                                           fixed_period=fixed_period, cpi_list=cpi_list_no_inflation)
        schedule_al_no_inflation = al_no_inflation.calc_amortization_schedule()

        au_comparison = AdjustableUnlinked(principal=principal, term_years=term_years,
                                           initial_interest_rate=initial_rate, reference_index=reference_index,
                                           fixed_period=fixed_period)
        schedule_au_comparison = au_comparison.calc_amortization_schedule()

        # Compare first month's total payment
        self.assertEqual(parse_payment(schedule_al_no_inflation[0]["total_payment"]),
                         parse_payment(schedule_au_comparison[0]["total_payment"]))
        # Assert final remaining balance is close to zero for no-inflation case
        self.assertAlmostEqual(parse_payment(schedule_al_no_inflation[-1]["remaining_balance"]), 0, delta=50)


        # Scenario 2: With Inflation (2% annual)
        cpi_list_with_inflation = [100] * term_months
        annual_inflation = 0.02
        current_cpi = 100
        for i in range(term_months):
            if i > 0 and i % 12 == 0:
                current_cpi *= (1 + annual_inflation)
            cpi_list_with_inflation[i] = current_cpi
            
        al_with_inflation = AdjustableLinked(principal=principal, term_years=term_years,
                                             initial_interest_rate=initial_rate, reference_index=reference_index,
                                             fixed_period=fixed_period, cpi_list=cpi_list_with_inflation)
        schedule_al_with_inflation = al_with_inflation.calc_amortization_schedule()

        # Assert that total payment after inflation has taken effect is higher
        # (e.g. check payment at month 25, index 24, after two years of inflation)
        if term_months > 24:
            payment_no_inflation_month25 = parse_payment(schedule_al_no_inflation[24]["total_payment"])
            payment_with_inflation_month25 = parse_payment(schedule_al_with_inflation[24]["total_payment"])
            self.assertGreater(payment_with_inflation_month25, payment_no_inflation_month25)

        # Assert final remaining balance is close to zero for with-inflation case
        self.assertAlmostEqual(parse_payment(schedule_al_with_inflation[-1]["remaining_balance"]), 0, delta=50)


if __name__ == "__main__":
    unittest.main()

class TestMortgageFactory(unittest.TestCase):

    def test_mortgage_factory_valid_types(self):
        mortgage_params = {
            "fixed_test_track": {
                "type": "fixed", "principal": 100000, "term_years": 10, "interest_rate": 3
            },
            "prime_test_track": {
                "type": "prime", "principal": 100000, "term_years": 10, "interest_rate": 3, "spread": -0.2
            },
            "linked_test_track": {
                "type": "linked", "principal": 100000, "term_years": 10, "real_interest_rate": 2.5, "cpi_list": [100]*120
            },
            "adjustable_test_track": {
                "type": "adjustable", "principal": 100000, "term_years": 10, "initial_interest_rate": 2,
                "reference_index": [2.5, 3], "fixed_period": 5 # Changed fixed_period_years to fixed_period
            },
            "adjustablelinked_test_track": {
                "type": "adjustablelinked", "principal": 100000, "term_years": 10, "initial_interest_rate": 2,
                "reference_index": [2.5, 3], "fixed_period": 5, "cpi_list": [100]*120 # real_balance removed
            }
        }
        multi_mortgage = mortgage_factory(mortgage_params)
        self.assertIsInstance(multi_mortgage, MultiTrackMortgage)
        self.assertEqual(len(multi_mortgage.mortgage_tracks), 5)
        self.assertIsInstance(multi_mortgage.mortgage_tracks['fixed_test_track'], FixedUnlinked)
        self.assertIsInstance(multi_mortgage.mortgage_tracks['prime_test_track'], PrimeUnlinked)
        self.assertIsInstance(multi_mortgage.mortgage_tracks['linked_test_track'], LinkedFixed)
        self.assertIsInstance(multi_mortgage.mortgage_tracks['adjustable_test_track'], AdjustableUnlinked)
        self.assertIsInstance(multi_mortgage.mortgage_tracks['adjustablelinked_test_track'], AdjustableLinked)

    def test_mortgage_factory_invalid_type(self):
        mortgage_params = {
            "invalid_track": {"type": "nonexistenttype", "principal": 10000, "term_years": 5, "interest_rate": 3}
        }
        multi_mortgage = mortgage_factory(mortgage_params)
        self.assertEqual(len(multi_mortgage.mortgage_tracks), 0)

    def test_mortgage_factory_missing_params(self):
        mortgage_params = {
            "missing_param_track": {"type": "fixed", "principal": 10000, "term_years": 5} # Missing interest_rate
        }
        multi_mortgage = mortgage_factory(mortgage_params)
        # Based on current factory implementation, it might create the track with default/missing params leading to error later,
        # or skip. If it skips, count should be 0. If it tries and fails internally, it might still add a faulty track or None.
        # Assuming skipping or error during track creation results in no track.
        self.assertEqual(len(multi_mortgage.mortgage_tracks), 0)