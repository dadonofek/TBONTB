"""
Integrated Financial Simulation Engine
========================================

This simulation compares three financial strategies over a multi‐year period:
  1. Buying an Apartment:
     - Purchases a property with a down payment and a mortgage.
     - Simulates mortgage amortization, property appreciation, and annual maintenance costs.
     - Computes final net equity and additional yearly details:
         • Mortgage balance over time.
         • Annual principal and interest paid.
         • Property value over time.
         • Cumulative maintenance costs.

  2. Renting and Investing:
     - Pays a fixed monthly rent.
     - Invests the surplus (monthly income minus rent) with monthly compounding.
     - Records investment value growth, cumulative deposits, and earnings.
     - Also tracks cumulative rent payments.

  3. Direct Investment:
     - Invests the full monthly income (plus initial savings) with monthly compounding.
     - Records portfolio growth, cumulative deposits and earnings.
     - Shows the final tax-adjusted value.
"""

# === Imports ===
import numpy as np
import datetime
from dataclasses import dataclass
from typing import List
import humanize  # For human-friendly number formatting
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from functions import simulate_investment, simulate_buying_scenario, plot_paths, simulate_property_value
from mortgage_calc import mortgage_factory

# Simulation settings
SIMULATION_START_DATE = datetime.date.today()
SIMULATION_YEARS = 30  # Duration of simulation in years
PLOT_RESULTS = True
N_SIM = 10000

STOCKS_TAX_RATE = 25  # Tax rate on investment gains (in percent)

# === Classes ===

@dataclass
class FinancialProfile:
    """Stores personal financial data."""
    monthly_free_income: list
    savings: int


@dataclass
class Scenario:
    """Base class for a financial scenario."""
    name: str
    profile: FinancialProfile

    def simulate(self):
        raise NotImplementedError("Simulation method not implemented.")

    def print_results(self):
        raise NotImplementedError("Simulation method not implemented.")


@dataclass
class BuyingScenario(Scenario):
    """Simulation scenario for buying an apartment."""
    apartment_price: float
    down_payment: float
    mortgage_params: dict
    forecast_params: dict
    n_sim: int
    simulation_years: int
    maintenance_cost_rate: float
    fixed_maintenance_cost: int

    def __post_init__(self):
        self.mortgage = mortgage_factory(self.mortgage_params)

        if self.mortgage.total_loan_value + self.down_payment != self.apartment_price:
            raise ValueError(f"Inconsistent financing for the apartment:\n"
                             f"{self.apartment_price = }\n{self.down_payment = }\n{self.apartment_price = }")
        for i, payment in enumerate(self.mortgage.get_payment_list()):
            if payment > self.profile.monthly_free_income[i//12][1%12]:
                raise ValueError(f'monthly free income is less than mortgage payment')



    def print_results(self):  # TODO: fix.
        print("=== Buying Scenario Results ===")
        print(f"Apartment Purchase Price: {humanize.intcomma(self.apartment_price)} ILS")
        print(f"Down Payment: {humanize.intcomma(self.down_payment)} ILS")
        print(f"Mortgage Loan: {humanize.intcomma(self.apartment_price - self.down_payment)} ILS")
        print(f"Final Property Value after {self.simulation_years} years: {humanize.intcomma(round(self.results['final_property_value']))} ILS")
        print(f"Remaining Mortgage Balance: {humanize.intcomma(round(self.results['remaining_mortgage']))} ILS")
        total_principal_payed = sum(self.results['monthly_principal_paid'])
        print(f"Total Principal Paid: {humanize.intcomma(round(total_principal_payed))} ILS")
        total_interest_paid = sum(self.results['monthly_interest_paid'])
        print(f"Total Interest Paid: {humanize.intcomma(round(total_interest_paid))} ILS")
        print(f"Total Mortgage Payments Made: {humanize.intcomma(round(total_principal_payed + total_interest_paid))} ILS")
        print(f"Total Maintenance Costs: {humanize.intcomma(round(self.results['total_maintenance_cost']))} ILS")
        print(f"Net Equity (Final Value - Mortgage - Maintenance): {humanize.intcomma(round(self.results['net_equity']))} ILS")
        print("=" * 40)

    def simulate(self):
        print(f"\nSimulating {self.name} (Buying):")

        property_value = simulate_property_value(
            apartment_price=self.apartment_price,
            years=self.simulation_years,
            forecast_params={'mu': 0.05, 'sigma': 0.05},
            n_sim=self.n_sim
        )
        self.results = {'property_value_paths': property_value}

        buying_results = simulate_buying_scenario(
            property_value_paths=property_value,
            mortgage=self.mortgage,
            years=self.simulation_years,
            maintenance_cost_rate=self.maintenance_cost_rate,
            fixed_maintenance_cost=self.fixed_maintenance_cost
        )
        self.results.update(buying_results)

        free_income = np.array(self.profile.monthly_free_income) - np.array(self.results['monthly_maintenance'][1:, 0]).reshape(30, 12) - np.array(self.mortgage.get_payment_list()).reshape(30, 12)
        # TODO: invest free income
        # self.print_results()
        return self.results


@dataclass
class InvestmentScenario(Scenario):
    """Simulation scenario for direct investment of full income."""
    tax_rate: float
    transaction_fee: float
    percentage_management_fee: float
    ILS_management_fee: float
    initial_already_invested: bool
    forecast_params: dict
    n_sim: int
    simulation_years: int

    def print_results(self):
        print("=== Direct Investment Scenario Results ===")
        print(f"Monthly Investment (Full Income): {humanize.intcomma(np.mean(self.profile.monthly_free_income))} ILS")
        # Compute average final balance from the Monte Carlo paths
        avg_final_balance_untaxed = np.percentile(self.results['final_investment_paths_untaxed'][-1, :], 50)
        print(f"Average Final Investment Value (Untaxed): {humanize.intcomma(round(avg_final_balance_untaxed))} ILS")
        avg_final_balance_taxed = np.percentile(self.results['final_investment_paths_taxed'][-1, :], 50)
        print(f"Average Final Investment Value (taxed): {humanize.intcomma(round(avg_final_balance_taxed))} ILS")
        print("=" * 40)

    def simulate(self):
        print(f"\nSimulating {self.name} (Direct Investment):")

        self.results = simulate_investment(
            initial_fortune=self.profile.savings,
            years=self.simulation_years,
            tax_rate=self.tax_rate,
            transaction_fee=self.transaction_fee,
            percentace_management_fee=self.percentage_management_fee,
            ILS_management_fee=self.ILS_management_fee,
            initial_already_invested=self.initial_already_invested,
            contributions_schedule=self.profile.monthly_free_income,
            forecast_params=self.forecast_params,
            n_sim=self.n_sim
        )
        self.print_results()
        return self.results


@dataclass
# class RentingScenario(Scenario):
#     """Simulation scenario for renting and investing the surplus."""
#     monthly_rent: float
#     expected_investment_return: float  # in percent
#
#     def print_results(self):
#         print("=== Renting Scenario Results ===")
#         print(f"Monthly Rent: {humanize.intcomma(self.monthly_rent)} ILS")
#         print(f"Monthly Surplus Invested: {humanize.intcomma(self.monthly_surplus)} ILS")
#         # Compute average final balance from the Monte Carlo paths
#         final_balances = [path[-1] for path in self.results['paths']]
#         avg_final_balance = sum(final_balances) / len(final_balances)
#         print(f"Average Final Investment Value (Untaxed): {humanize.intcomma(round(avg_final_balance))} ILS")
#         print("=" * 40)
#
#     def simulate(self):
#         print(f"\nSimulating {self.name} (Renting):")
#         self.monthly_surplus = profile.monthly_free_income - self.monthly_rent
#         if self.monthly_surplus < 0:
#             print("Warning: Monthly rent exceeds monthly income. No surplus available for investment.")
#             self.monthly_surplus = 0
#         self.results = simulate_investment(
#             initial_fortune=profile.savings,
#             monthly_contribution=self.monthly_surplus,
#             years=SIMULATION_YEARS,
#             tax_rate=STOCKS_TAX_RATE,
#             n_sim=N_SIM
#         )
#         cumulative_rent = [self.monthly_rent * 12 * i for i in range(1, SIMULATION_YEARS + 1)]
#         self.print_results()
#         return {
#             'final_investment_paths': self.results['paths'],
#             'cumulative_rent': cumulative_rent
#         }


@dataclass
class SimulationEngine:
    """Core engine to run the financial simulation."""
    profile: FinancialProfile
    scenarios: List[Scenario]
    start_date: datetime.date
    years: int

    def run(self):
        print("Starting Financial Simulation...\n")
        all_results = {}
        for scenario in self.scenarios:
            print(f"--- Scenario: {scenario.name} ---")
            data = scenario.simulate()
            all_results[scenario.name] = data

        if PLOT_RESULTS:
            self.plot_results(all_results)

        print("\nSimulation Complete.")

    def plot_results(self, all_results):
        # Combined Plotting for all Scenarios in one page
        years_axis = list(range(1, self.years + 1))
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                "Buying Scenario Data",
                "Renting and Investing Scenario Data",
                "Direct Investment Scenario Data"
            )
        )

        # Buying Scenario traces
        if all_results.get("Buying Apartment"):
            investment_data_untaxed = all_results["Buying Apartment"]['monthly_net_equity']
            forecast_traces = plot_paths(investment_data_untaxed, self.years, bins=1000, return_traces=True)
            for trace in forecast_traces:
                fig.add_trace(trace, row=1, col=1)
            y_upper = max(max(trace['y']) for trace in forecast_traces if trace.__class__.__name__ == 'Scatter') * 1.1
            fig.update_yaxes(range=[0, y_upper], row=1, col=1)

        # Renting & Investing Scenario traces
        # if all_results.get("Renting and Investing"):
        #     renting_data = all_results["Renting and Investing"]
        #     fig.add_trace(go.Scatter(x=years_axis, y=renting_data['yearly_investment_value'],
        #                              mode='lines+markers', name="Investment Value", hovertemplate='%{y}'),
        #                   row=2, col=1)
        #     fig.add_trace(go.Scatter(x=years_axis, y=renting_data['yearly_deposits'],
        #                              mode='lines+markers', name="Deposits", hovertemplate='%{y}'),
        #                   row=2, col=1)
        #     fig.add_trace(go.Scatter(x=years_axis, y=renting_data['yearly_earnings'],
        #                              mode='lines+markers', name="Earnings", hovertemplate='%{y}'),
        #                   row=2, col=1)
        #     fig.add_trace(go.Scatter(x=years_axis, y=renting_data['cumulative_rent'],
        #                              mode='lines+markers', name="Cumulative Rent", hovertemplate='%{y}'),
        #                   row=2, col=1)

        # Direct Investment Scenario traces
        if all_results.get("Direct Investment"):
            investment_data_untaxed = all_results["Direct Investment"]['final_investment_paths_untaxed']  # taxed is not plotted
            forecast_traces = plot_paths(investment_data_untaxed, self.years, bins=1000, return_traces=True)
            for trace in forecast_traces:
                fig.add_trace(trace, row=3, col=1)
            y_upper = max(max(trace['y']) for trace in forecast_traces if trace.__class__.__name__ == 'Scatter')*1.1
            fig.update_yaxes(range=[0, y_upper], row=3, col=1)

        fig.update_layout(height=900, title_text="Financial Simulation Scenarios")
        fig.show()

# === Main Execution ===

def main():
    # Initialize the financial profile from constants
    USER_FREE_INCOME = [[10000] * 12 for _ in range(SIMULATION_YEARS)]  # in ILS for every simulation month
    USER_SAVINGS = 500000  # Current savings in ILS

    user_profile = FinancialProfile(
        monthly_free_income=USER_FREE_INCOME,
        savings=USER_SAVINGS,
    )

    # Initialize scenarios

    # buying scenario details
    APARTMENT_PRICE = 1800000  # Purchase price in ILS
    DOWN_PAYMENT = 500000  # Down payment in ILS
    MAINTENANCE_COST_RATE = 0.0  # Maintenance cost rate (% of property value)
    FIXED_MAINTENANCE_COST = 10000  # Fixed annual maintenance cost in ILS
    APT_FORECAST_PARAMS = {'mu': 0.054, 'sigma': 0.052}
    mortgage_params = {
        "fixed_mortgage": {
            "type": "fixed",
            "principal": 650000,
            "term_years": 30,
            "interest_rate": 4.0
        },
        "prime_mortgage": {
            "type": "prime",
            "principal": 650000,
            "term_years": 30,
            "interest_rate": 4.5,
            "spread": -0.5
        }
    }

    buying = BuyingScenario(
        name="Buying Apartment",
        profile=user_profile,
        apartment_price=APARTMENT_PRICE,
        down_payment=DOWN_PAYMENT,
        mortgage_params=mortgage_params,
        maintenance_cost_rate=MAINTENANCE_COST_RATE,
        fixed_maintenance_cost=FIXED_MAINTENANCE_COST,
        forecast_params=APT_FORECAST_PARAMS,
        n_sim = N_SIM,
        simulation_years = SIMULATION_YEARS
    )

    # Investment details
    TRANSACTION_FEES = 0.07  # in % per transaction
    PR_MANEGEMENT_FEE = 0.1  # in % per year
    ILS_MANEGEMENT_FEE = 15  # in % per month
    FURTUNE_INVESTED = True
    STOCKS_FORECAST_PARAMS = {'mu': 0.078, 'sigma': 0.15}

    investment = InvestmentScenario(
        name="Direct Investment",
        profile=user_profile,
        tax_rate=STOCKS_TAX_RATE,
        transaction_fee=TRANSACTION_FEES,
        percentage_management_fee=PR_MANEGEMENT_FEE,
        ILS_management_fee=ILS_MANEGEMENT_FEE,
        initial_already_invested=FURTUNE_INVESTED,
        forecast_params=STOCKS_FORECAST_PARAMS,
        n_sim=N_SIM,
        simulation_years=SIMULATION_YEARS
    )

    # Renting details (for renting scenario)
    MONTHLY_RENT = 5000  # Monthly rent in ILS

    # renting = RentingScenario(
    #     name="Renting and Investing",
    #     monthly_rent=MONTHLY_RENT,
    #     expected_investment_return=EXPECTED_RETURN
    # )

    # Create and run the simulation engine with all scenarios
    engine = SimulationEngine(
        profile=user_profile,
        scenarios=[buying, investment],
        start_date=SIMULATION_START_DATE,
        years=SIMULATION_YEARS
    )
    engine.run()


if __name__ == "__main__":
    main()









    # Additional parameters for property simulation
