"""
Pydantic models for scenario inputs
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from datetime import datetime

class ForecastParams(BaseModel):
    """Parameters for GBM forecasting"""
    mu: float = Field(..., description="Annual drift/expected return (e.g., 0.07 for 7%)", ge=-1, le=2)
    sigma: float = Field(..., description="Annual volatility (e.g., 0.15 for 15%)", ge=0, le=2)

class MortgageTrackParams(BaseModel):
    """Parameters for a single mortgage track"""
    type: str = Field(..., description="Mortgage type: fixed, prime, linked, adjustable, adjustablelinked")
    principal: float = Field(..., description="Loan principal amount", gt=0)
    term_years: int = Field(..., description="Loan term in years", ge=1, le=50)
    interest_rate: Optional[float] = Field(None, description="Annual interest rate in percent", ge=0, le=100)
    spread: Optional[float] = Field(None, description="Spread over prime rate (for prime type)")

    @field_validator('type')
    @classmethod
    def validate_mortgage_type(cls, v):
        valid_types = ['fixed', 'prime', 'linked', 'adjustable', 'adjustablelinked']
        if v.lower() not in valid_types:
            raise ValueError(f"Mortgage type must be one of {valid_types}")
        return v.lower()

class FinancialProfileInput(BaseModel):
    """User's financial profile"""
    monthly_free_income: List[List[float]] = Field(
        ...,
        description="Monthly free income for each year (nested list: years x 12 months)"
    )
    savings: float = Field(..., description="Current savings/initial capital", ge=0)

    @field_validator('monthly_free_income')
    @classmethod
    def validate_income_structure(cls, v):
        if not v or len(v) == 0:
            raise ValueError("monthly_free_income must have at least one year")
        for year_idx, year in enumerate(v):
            if len(year) != 12:
                raise ValueError(f"Year {year_idx} must have exactly 12 months")
        return v

class BuyingScenarioInput(BaseModel):
    """Input for buying apartment scenario simulation"""
    profile: FinancialProfileInput
    apartment_price: float = Field(..., description="Apartment purchase price", gt=0)
    down_payment: float = Field(..., description="Down payment amount", ge=0)
    mortgage_params: Dict[str, MortgageTrackParams] = Field(
        ...,
        description="Mortgage tracks configuration (e.g., {'fixed': {...}, 'prime': {...}})"
    )
    maintenance_cost_rate: float = Field(
        default=0.0,
        description="Annual maintenance cost as % of property value",
        ge=0,
        le=100
    )
    fixed_maintenance_cost: float = Field(
        default=0.0,
        description="Fixed annual maintenance cost in currency",
        ge=0
    )
    forecast_params: ForecastParams
    simulation_years: int = Field(default=30, description="Simulation duration in years", ge=1, le=50)
    n_sim: int = Field(default=10000, description="Number of Monte Carlo simulations", ge=100, le=50000)

    @field_validator('down_payment')
    @classmethod
    def validate_down_payment(cls, v, info):
        if 'apartment_price' in info.data and v > info.data['apartment_price']:
            raise ValueError("Down payment cannot exceed apartment price")
        return v

class InvestmentScenarioInput(BaseModel):
    """Input for investment scenario simulation"""
    profile: FinancialProfileInput
    tax_rate: float = Field(..., description="Tax rate on gains in percent", ge=0, le=100)
    transaction_fee: float = Field(default=0.0, description="Transaction fee in percent", ge=0, le=100)
    percentage_management_fee: float = Field(
        default=0.0,
        description="Annual management fee in percent",
        ge=0,
        le=100
    )
    ILS_management_fee: float = Field(
        default=0.0,
        description="Fixed monthly management fee",
        ge=0
    )
    initial_already_invested: bool = Field(
        default=True,
        description="Whether initial savings are already invested"
    )
    forecast_params: ForecastParams
    simulation_years: int = Field(default=30, description="Simulation duration in years", ge=1, le=50)
    n_sim: int = Field(default=10000, description="Number of Monte Carlo simulations", ge=100, le=50000)

class ComparisonInput(BaseModel):
    """Input for comparing multiple scenarios"""
    buying_scenario: Optional[BuyingScenarioInput] = None
    investment_scenario: Optional[InvestmentScenarioInput] = None

    @field_validator('investment_scenario')
    @classmethod
    def validate_at_least_one_scenario(cls, v, info):
        if not v and not info.data.get('buying_scenario'):
            raise ValueError("At least one scenario must be provided")
        return v
