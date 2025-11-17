"""
Simulation service layer - wraps existing simulation code
"""

import sys
from pathlib import Path
import numpy as np
from typing import Dict, Any
import uuid
from datetime import datetime

# Add backend directory to Python path to import existing modules
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from functions import simulate_investment, simulate_buying_scenario, simulate_property_value
from mortgage_calc import mortgage_factory
from app.models.scenario import (
    BuyingScenarioInput,
    InvestmentScenarioInput,
    ComparisonInput
)
from app.models.results import (
    BuyingScenarioResults,
    InvestmentScenarioResults,
    ScenarioSummary,
    SimulationResponse,
    SimulationStatus,
    ResultsResponse
)

class SimulationService:
    """Service for running financial simulations"""

    @staticmethod
    def _calculate_percentiles(data: np.ndarray) -> Dict[str, float]:
        """Calculate key percentiles from simulation data"""
        return {
            "median": float(np.percentile(data, 50)),
            "p10": float(np.percentile(data, 10)),
            "p90": float(np.percentile(data, 90)),
            "mean": float(np.mean(data)),
            "std": float(np.std(data))
        }

    @staticmethod
    def _sample_paths(paths: np.ndarray, max_paths: int = 100) -> list:
        """Sample simulation paths to reduce response size"""
        n_paths = paths.shape[1] if len(paths.shape) > 1 else 1
        if n_paths <= max_paths:
            return paths.tolist()

        # Randomly sample paths
        indices = np.random.choice(n_paths, max_paths, replace=False)
        return paths[:, indices].tolist()

    @staticmethod
    def run_buying_scenario(input_data: BuyingScenarioInput) -> BuyingScenarioResults:
        """
        Run buying scenario simulation

        Args:
            input_data: Validated buying scenario input

        Returns:
            BuyingScenarioResults with simulation outcomes
        """
        # Convert Pydantic models to dict for existing code
        mortgage_params = {
            name: params.model_dump()
            for name, params in input_data.mortgage_params.items()
        }

        # Create mortgage object
        mortgage = mortgage_factory(mortgage_params)

        # Validate financing
        total_loan = mortgage.total_loan_value
        if total_loan + input_data.down_payment != input_data.apartment_price:
            raise ValueError(
                f"Financing mismatch: loan ({total_loan}) + down_payment "
                f"({input_data.down_payment}) != apartment_price ({input_data.apartment_price})"
            )

        # Simulate property value
        property_value_paths = simulate_property_value(
            apartment_price=input_data.apartment_price,
            years=input_data.simulation_years,
            forecast_params=input_data.forecast_params.model_dump(),
            n_sim=input_data.n_sim
        )

        # Run buying simulation
        buying_results = simulate_buying_scenario(
            property_value_paths=property_value_paths,
            mortgage=mortgage,
            years=input_data.simulation_years,
            maintenance_cost_rate=input_data.maintenance_cost_rate,
            fixed_maintenance_cost=input_data.fixed_maintenance_cost
        )

        # Calculate summary statistics
        final_values = buying_results['net_equity']
        final_property_values = buying_results['final_property_value']
        maintenance_costs = buying_results['total_maintenance_cost']

        summary = ScenarioSummary(
            scenario_type="buying",
            final_value_median=float(np.percentile(final_values, 50)),
            final_value_pessimistic=float(np.percentile(final_values, 10)),
            final_value_optimistic=float(np.percentile(final_values, 90)),
            total_invested=input_data.apartment_price,
            total_return=float(np.percentile(final_values, 50)) - input_data.apartment_price,
            annualized_return=(
                (float(np.percentile(final_values, 50)) / input_data.apartment_price) **
                (1 / input_data.simulation_years) - 1
            ) * 100
        )

        # Prepare results
        results = BuyingScenarioResults(
            summary=summary,
            final_property_value=SimulationService._calculate_percentiles(final_property_values),
            remaining_mortgage=float(buying_results['remaining_mortgage']),
            total_maintenance_cost=SimulationService._calculate_percentiles(maintenance_costs),
            net_equity=SimulationService._calculate_percentiles(final_values),
            monthly_mortgage_balance=buying_results['monthly_mortgage_balance'].tolist(),
            monthly_principal_paid=buying_results['monthly_principal_paid'].tolist(),
            monthly_interest_paid=buying_results['monthly_interest_paid'].tolist(),
            property_value_paths=SimulationService._sample_paths(property_value_paths),
            net_equity_paths=SimulationService._sample_paths(buying_results['monthly_net_equity'])
        )

        return results

    @staticmethod
    def run_investment_scenario(input_data: InvestmentScenarioInput) -> InvestmentScenarioResults:
        """
        Run investment scenario simulation

        Args:
            input_data: Validated investment scenario input

        Returns:
            InvestmentScenarioResults with simulation outcomes
        """
        # Run investment simulation
        investment_results = simulate_investment(
            initial_fortune=input_data.profile.savings,
            years=input_data.simulation_years,
            tax_rate=input_data.tax_rate,
            transaction_fee=input_data.transaction_fee,
            percentace_management_fee=input_data.percentage_management_fee,
            ILS_management_fee=input_data.ILS_management_fee,
            initial_already_invested=input_data.initial_already_invested,
            contributions_schedule=input_data.profile.monthly_free_income,
            forecast_params=input_data.forecast_params.model_dump(),
            n_sim=input_data.n_sim
        )

        # Extract final values
        paths_untaxed = investment_results['final_investment_paths_untaxed']
        paths_taxed = investment_results['final_investment_paths_taxed']

        final_untaxed = paths_untaxed[-1, :]
        final_taxed = paths_taxed[-1, :]

        # Calculate total invested
        total_invested = input_data.profile.savings + sum(
            sum(year) for year in input_data.profile.monthly_free_income
        )

        summary = ScenarioSummary(
            scenario_type="investment",
            final_value_median=float(np.percentile(final_taxed, 50)),
            final_value_pessimistic=float(np.percentile(final_taxed, 10)),
            final_value_optimistic=float(np.percentile(final_taxed, 90)),
            total_invested=total_invested,
            total_return=float(np.percentile(final_taxed, 50)) - total_invested,
            annualized_return=(
                (float(np.percentile(final_taxed, 50)) / total_invested) **
                (1 / input_data.simulation_years) - 1
            ) * 100
        )

        results = InvestmentScenarioResults(
            summary=summary,
            final_value_untaxed=SimulationService._calculate_percentiles(final_untaxed),
            final_value_taxed=SimulationService._calculate_percentiles(final_taxed),
            investment_paths_untaxed=SimulationService._sample_paths(paths_untaxed),
            investment_paths_taxed=SimulationService._sample_paths(paths_taxed)
        )

        return results

    @staticmethod
    def run_comparison(input_data: ComparisonInput) -> ResultsResponse:
        """
        Run comparison of multiple scenarios

        Args:
            input_data: Comparison input with multiple scenarios

        Returns:
            ResultsResponse with all scenario results
        """
        simulation_id = str(uuid.uuid4())
        created_at = datetime.now()

        buying_results = None
        investment_results = None

        if input_data.buying_scenario:
            buying_results = SimulationService.run_buying_scenario(input_data.buying_scenario)

        if input_data.investment_scenario:
            investment_results = SimulationService.run_investment_scenario(input_data.investment_scenario)

        response = ResultsResponse(
            simulation_id=simulation_id,
            status=SimulationStatus.COMPLETED,
            created_at=created_at,
            completed_at=datetime.now(),
            buying_results=buying_results,
            investment_results=investment_results,
            simulation_params={
                "buying": input_data.buying_scenario.model_dump() if input_data.buying_scenario else None,
                "investment": input_data.investment_scenario.model_dump() if input_data.investment_scenario else None
            }
        )

        return response
