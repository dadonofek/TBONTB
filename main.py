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
import datetime
from dataclasses import dataclass
from typing import List
import humanize  # For human-friendly number formatting
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from functions import simulate_investment, simulate_buying_scenario
from forecasting import simulate_gbm, plot_forecast

# === Global Constants / Input Parameters ===
PLOT_RESULTS = True
N_SIM = 10000

# User financial details
USER_FREE_INCOME = 10000  # Monthly income in ILS
USER_SAVINGS = 500000  # Current savings in ILS
USER_DEBT = 0  # Existing debt in ILS

# Apartment purchase details (for buying scenario)
APARTMENT_PRICE = 1800000  # Purchase price in ILS
DOWN_PAYMENT = 500000  # Down payment in ILS
MORTGAGE_RATE = 4.0  # Annual mortgage interest rate (in percent)
MORTGAGE_TERM = 30  # Mortgage term in years

# Renting details (for renting scenario)
MONTHLY_RENT = 5000  # Monthly rent in ILS

# Investment details (for renting and direct investment scenarios)
EXPECTED_RETURN = 9.6  # Expected annual return (in percent)
TRANSACTION_FEES = 0.07 # in % per transaction
PR_MANEGEMENT_FEE = 0.1 # in % per year
ILS_MANEGEMENT_FEE = 15 # in % per month
FURTUNE_INVESTED = True

# Simulation settings
SIMULATION_START_DATE = datetime.date.today()
SIMULATION_YEARS = 30  # Duration of simulation in years
STOCKS_TAX_RATE = 25  # Tax rate on investment gains (in percent)

# Additional parameters for property simulation
YEARLY_VALUE_INCREASE_RATE = 4.3  # Annual property appreciation (in percent)
MAINTENANCE_COST_RATE = 0.0  # Maintenance cost rate (% of property value)
FIXED_MAINTENANCE_COST = 10000  # Fixed annual maintenance cost in ILS


# === Classes ===

@dataclass
class FinancialProfile:
    """Stores personal financial data."""
    monthly_income: float
    savings: float
    debt: float


@dataclass
class Scenario:
    """Base class for a financial scenario."""
    name: str

    def simulate(self, profile: FinancialProfile):
        raise NotImplementedError("Simulation method not implemented.")

    def print_results(self):
        raise NotImplementedError("Simulation method not implemented.")


@dataclass
class BuyingScenario(Scenario):
    """Simulation scenario for buying an apartment."""
    apartment_price: float
    down_payment: float
    mortgage_rate: float
    mortgage_term: int

    def print_results(self):
        print("=== Buying Scenario Results ===")
        print(f"Apartment Purchase Price: {humanize.intcomma(self.apartment_price)} ILS")
        print(f"Down Payment: {humanize.intcomma(self.down_payment)} ILS")
        print(f"Mortgage Loan: {humanize.intcomma(self.apartment_price - self.down_payment)} ILS")
        print(f"Final Property Value after {SIMULATION_YEARS} years: {humanize.intcomma(round(self.results['final_property_value']))} ILS")
        print(f"Remaining Mortgage Balance: {humanize.intcomma(round(self.results['remaining_mortgage']))} ILS")
        print(f"Total Mortgage Payments Made: {humanize.intcomma(round(self.results['total_mortgage_payments']))} ILS")
        print(f"Total Interest Paid: {humanize.intcomma(round(self.results['total_interest_paid']))} ILS")
        print(f"Total Maintenance Costs: {humanize.intcomma(round(self.results['total_maintenance_cost']))} ILS")
        print(f"Net Equity (Final Value - Mortgage - Maintenance): {humanize.intcomma(round(self.results['net_equity']))} ILS")
        print("=" * 40)

    def simulate(self, profile: FinancialProfile):
        print(f"\nSimulating {self.name} (Buying):")
        self.results = simulate_buying_scenario(
            apartment_price=self.apartment_price,
            down_payment=self.down_payment,
            mortgage_rate=self.mortgage_rate,
            mortgage_term=self.mortgage_term,
            years=SIMULATION_YEARS,
            maintenance_cost_rate=MAINTENANCE_COST_RATE,
            fixed_maintenance_cost=FIXED_MAINTENANCE_COST,
            yearly_value_increase_rate=YEARLY_VALUE_INCREASE_RATE
        )
        self.print_results()
        # Return all detailed data for plotting
        return {
            'yearly_mortgage_balance': self.results['yearly_mortgage_balance'],
            'yearly_principal_paid': self.results['yearly_principal_paid'],
            'yearly_interest_paid': self.results['yearly_interest_paid'],
            'yearly_property_value': self.results['yearly_property_value'],
            'yearly_maintenance_cost': self.results['yearly_maintenance_cost']
        }


@dataclass
class RentingScenario(Scenario):
    """Simulation scenario for renting and investing the surplus."""
    monthly_rent: float
    expected_investment_return: float  # in percent

    def print_results(self):
        print("=== Renting Scenario Results ===")
        print(f"Monthly Rent: {humanize.intcomma(self.monthly_rent)} ILS")
        print(f"Monthly Surplus Invested: {humanize.intcomma(self.monthly_surplus)} ILS")
        # Compute average final balance from the Monte Carlo paths
        final_balances = [path[-1] for path in self.results['paths']]
        avg_final_balance = sum(final_balances) / len(final_balances)
        print(f"Average Final Investment Value (Untaxed): {humanize.intcomma(round(avg_final_balance))} ILS")
        print("=" * 40)

    def simulate(self, profile: FinancialProfile):
        print(f"\nSimulating {self.name} (Renting):")
        self.monthly_surplus = profile.monthly_income - self.monthly_rent
        if self.monthly_surplus < 0:
            print("Warning: Monthly rent exceeds monthly income. No surplus available for investment.")
            self.monthly_surplus = 0
        self.results = simulate_investment(
            initial_fortune=profile.savings,
            monthly_contribution=self.monthly_surplus,
            years=SIMULATION_YEARS,
            tax_rate=STOCKS_TAX_RATE,
            n_sim=N_SIM
        )
        cumulative_rent = [self.monthly_rent * 12 * i for i in range(1, SIMULATION_YEARS + 1)]
        self.print_results()
        return {
            'final_investment_paths': self.results['paths'],
            'cumulative_rent': cumulative_rent
        }


@dataclass
class InvestmentScenario(Scenario):
    """Simulation scenario for direct investment of full income."""
    expected_return: float  # in percent

    def print_results(self, profile):
        print("=== Direct Investment Scenario Results ===")
        print(f"Monthly Investment (Full Income): {humanize.intcomma(profile.monthly_income)} ILS")
        # Compute average final balance from the Monte Carlo paths
        final_balances = [path[-1] for path in self.results['paths']]
        avg_final_balance = sum(final_balances) / len(final_balances)
        print(f"Average Final Investment Value (Untaxed): {humanize.intcomma(round(avg_final_balance))} ILS")
        print("=" * 40)

    def simulate(self, profile: FinancialProfile):
        print(f"\nSimulating {self.name} (Direct Investment):")
        self.results = simulate_investment(
            initial_fortune=profile.savings,
            monthly_contribution=profile.monthly_income,
            years=SIMULATION_YEARS,
            tax_rate=STOCKS_TAX_RATE,
            transaction_fee=TRANSACTION_FEES,
            percentace_management_fee=PR_MANEGEMENT_FEE,
            ILS_management_fee=ILS_MANEGEMENT_FEE,
            initial_already_invested=FURTUNE_INVESTED,
            n_sim=N_SIM
        )
        # self.print_results(profile)
        return {
            'final_investment_paths': self.results
        }


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
            data = scenario.simulate(self.profile)
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
            buying_data = all_results["Buying Apartment"]
            fig.add_trace(go.Scatter(x=years_axis, y=buying_data['yearly_mortgage_balance'],
                                     mode='lines+markers', name="Mortgage Balance", hovertemplate='%{y}'),
                          row=1, col=1)
            fig.add_trace(go.Scatter(x=years_axis, y=buying_data['yearly_principal_paid'],
                                     mode='lines+markers', name="Principal Paid", hovertemplate='%{y}'),
                          row=1, col=1)
            fig.add_trace(go.Scatter(x=years_axis, y=buying_data['yearly_interest_paid'],
                                     mode='lines+markers', name="Interest Paid", hovertemplate='%{y}'),
                          row=1, col=1)
            fig.add_trace(go.Scatter(x=years_axis, y=buying_data['yearly_property_value'],
                                     mode='lines+markers', name="Property Value", hovertemplate='%{y}'),
                          row=1, col=1)
            fig.add_trace(go.Scatter(x=years_axis, y=buying_data['yearly_maintenance_cost'],
                                     mode='lines+markers', name="Maintenance Costs", hovertemplate='%{y}'),
                          row=1, col=1)

        # Renting & Investing Scenario traces
        if all_results.get("Renting and Investing"):
            renting_data = all_results["Renting and Investing"]
            fig.add_trace(go.Scatter(x=years_axis, y=renting_data['yearly_investment_value'],
                                     mode='lines+markers', name="Investment Value", hovertemplate='%{y}'),
                          row=2, col=1)
            fig.add_trace(go.Scatter(x=years_axis, y=renting_data['yearly_deposits'],
                                     mode='lines+markers', name="Deposits", hovertemplate='%{y}'),
                          row=2, col=1)
            fig.add_trace(go.Scatter(x=years_axis, y=renting_data['yearly_earnings'],
                                     mode='lines+markers', name="Earnings", hovertemplate='%{y}'),
                          row=2, col=1)
            fig.add_trace(go.Scatter(x=years_axis, y=renting_data['cumulative_rent'],
                                     mode='lines+markers', name="Cumulative Rent", hovertemplate='%{y}'),
                          row=2, col=1)

        # Direct Investment Scenario traces
        if all_results.get("Direct Investment"):
            investment_data = all_results["Direct Investment"]['final_investment_paths']
            forecast_traces = plot_forecast(investment_data, self.years, bins=1000, return_traces=True)
            for trace in forecast_traces:
                fig.add_trace(trace, row=3, col=1)
            y_upper = max(max(trace['y']) for trace in forecast_traces if trace.__class__.__name__ == 'Scatter')*1.1
            fig.update_yaxes(range=[0, y_upper], row=3, col=1)

        fig.update_layout(height=900, title_text="Financial Simulation Scenarios")
        fig.show()

# === Main Execution ===

def main():
    # Initialize the financial profile from constants
    profile = FinancialProfile(
        monthly_income=USER_FREE_INCOME,
        savings=USER_SAVINGS,
        debt=USER_DEBT
    )

    # Initialize scenarios
    buying = BuyingScenario(
        name="Buying Apartment",
        apartment_price=APARTMENT_PRICE,
        down_payment=DOWN_PAYMENT,
        mortgage_rate=MORTGAGE_RATE,
        mortgage_term=MORTGAGE_TERM
    )

    # renting = RentingScenario(
    #     name="Renting and Investing",
    #     monthly_rent=MONTHLY_RENT,
    #     expected_investment_return=EXPECTED_RETURN
    # )

    investment = InvestmentScenario(
        name="Direct Investment",
        expected_return=EXPECTED_RETURN
    )

    # Create and run the simulation engine with all scenarios
    engine = SimulationEngine(
        profile=profile,
        scenarios=[buying, investment],
        start_date=SIMULATION_START_DATE,
        years=SIMULATION_YEARS
    )
    engine.run()


if __name__ == "__main__":
    main()

