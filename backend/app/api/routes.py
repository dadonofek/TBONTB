"""
API route handlers
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uuid
from datetime import datetime

from app.models.scenario import (
    BuyingScenarioInput,
    InvestmentScenarioInput,
    ComparisonInput,
    ForecastParams
)
from app.models.results import (
    SimulationResponse,
    ResultsResponse,
    SimulationStatus,
    ErrorResponse
)
from app.services.simulation import SimulationService
from app.core.config import settings

router = APIRouter()

# ============================================================================
# Simulation Endpoints
# ============================================================================

@router.post(
    "/simulate/buying",
    response_model=ResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Run buying scenario simulation",
    description="Simulate buying an apartment with mortgage and property appreciation"
)
async def simulate_buying(input_data: BuyingScenarioInput):
    """
    Run a buying scenario simulation.

    Returns complete results including:
    - Property value projections
    - Mortgage amortization
    - Maintenance costs
    - Net equity over time
    """
    try:
        # Run simulation
        results = SimulationService.run_buying_scenario(input_data)

        # Wrap in ResultsResponse
        response = ResultsResponse(
            simulation_id=str(uuid.uuid4()),
            status=SimulationStatus.COMPLETED,
            created_at=datetime.now(),
            completed_at=datetime.now(),
            buying_results=results,
            simulation_params={"buying": input_data.model_dump()}
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )


@router.post(
    "/simulate/investment",
    response_model=ResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Run investment scenario simulation",
    description="Simulate direct investment with monthly contributions"
)
async def simulate_investment(input_data: InvestmentScenarioInput):
    """
    Run an investment scenario simulation.

    Returns complete results including:
    - Investment value projections (taxed and untaxed)
    - Total returns
    - Annualized performance
    """
    try:
        # Run simulation
        results = SimulationService.run_investment_scenario(input_data)

        # Wrap in ResultsResponse
        response = ResultsResponse(
            simulation_id=str(uuid.uuid4()),
            status=SimulationStatus.COMPLETED,
            created_at=datetime.now(),
            completed_at=datetime.now(),
            investment_results=results,
            simulation_params={"investment": input_data.model_dump()}
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )


@router.post(
    "/simulate/compare",
    response_model=ResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare multiple scenarios",
    description="Run and compare buying and/or investment scenarios side-by-side"
)
async def simulate_compare(input_data: ComparisonInput):
    """
    Run multiple scenarios and compare results.

    Can compare:
    - Buying vs Investment
    - Multiple configurations
    """
    try:
        results = SimulationService.run_comparison(input_data)
        return results

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}"
        )


# ============================================================================
# Parameters & Utilities
# ============================================================================

@router.get(
    "/parameters/defaults",
    response_model=Dict[str, Any],
    summary="Get default parameters",
    description="Retrieve default simulation parameters and recommended values"
)
async def get_default_parameters():
    """
    Get default simulation parameters.

    Useful for populating forms with sensible defaults.
    """
    return {
        "simulation_years": settings.DEFAULT_SIMULATION_YEARS,
        "n_simulations": settings.DEFAULT_N_SIMULATIONS,
        "stocks_tax_rate": settings.DEFAULT_STOCKS_TAX_RATE,
        "forecast_params": {
            "stocks": {
                "mu": 0.078,
                "sigma": 0.15,
                "description": "S&P 500 historical parameters"
            },
            "real_estate": {
                "mu": 0.054,
                "sigma": 0.052,
                "description": "Real estate historical parameters"
            }
        },
        "mortgage_types": [
            "fixed",
            "prime",
            "linked",
            "adjustable",
            "adjustablelinked"
        ],
        "limits": {
            "max_simulations": settings.MAX_N_SIMULATIONS,
            "max_years": 50,
            "min_years": 1
        }
    }


@router.post(
    "/mortgage/preview",
    response_model=Dict[str, Any],
    summary="Preview mortgage payments",
    description="Calculate mortgage amortization schedule without running full simulation"
)
async def preview_mortgage(mortgage_params: Dict[str, Dict[str, Any]]):
    """
    Preview mortgage payment schedule.

    Returns:
    - Monthly payment amount
    - Total interest to be paid
    - Amortization schedule (first year sample)
    """
    try:
        from mortgage_calc import mortgage_factory

        mortgage = mortgage_factory(mortgage_params)

        # Get first year of payments as sample
        sample_schedule = mortgage.amortization_schedule[:12]

        return {
            "total_loan_value": mortgage.total_loan_value,
            "monthly_payment_first_year": [
                int(entry["total_payment"].replace(",", ""))
                for entry in sample_schedule
            ],
            "average_monthly_payment": sum(
                int(entry["total_payment"].replace(",", ""))
                for entry in sample_schedule
            ) / len(sample_schedule),
            "total_interest_year_1": sum(
                int(entry["interest_payment"].replace(",", ""))
                for entry in sample_schedule
            ),
            "schedule_sample": sample_schedule
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mortgage calculation failed: {str(e)}"
        )


# ============================================================================
# Health & Info
# ============================================================================

@router.get(
    "/info",
    summary="API information",
    description="Get API version and capabilities"
)
async def get_api_info():
    """Get API information and capabilities"""
    return {
        "name": "TBONTB API",
        "version": "1.0.0",
        "description": "Financial simulation API for comparing buying vs investing scenarios",
        "endpoints": {
            "simulations": [
                "/api/v1/simulate/buying",
                "/api/v1/simulate/investment",
                "/api/v1/simulate/compare"
            ],
            "utilities": [
                "/api/v1/parameters/defaults",
                "/api/v1/mortgage/preview"
            ]
        },
        "features": [
            "Monte Carlo simulations",
            "Multi-track mortgage calculator",
            "Property value forecasting",
            "Investment portfolio simulation",
            "Scenario comparison"
        ]
    }
