"""
Pydantic models for simulation results
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class SimulationStatus(str, Enum):
    """Simulation status states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SimulationResponse(BaseModel):
    """Response when simulation is initiated"""
    simulation_id: str = Field(..., description="Unique simulation identifier")
    status: SimulationStatus = Field(..., description="Current simulation status")
    created_at: datetime = Field(..., description="Simulation creation timestamp")
    estimated_time_seconds: Optional[int] = Field(None, description="Estimated completion time in seconds")
    message: str = Field(default="Simulation queued successfully")

class ChartData(BaseModel):
    """Data structure for chart visualization"""
    type: str = Field(..., description="Chart type: heatmap, line, scatter, etc.")
    data: Dict[str, Any] = Field(..., description="Chart-specific data")
    layout: Optional[Dict[str, Any]] = Field(None, description="Plotly layout configuration")

class ScenarioSummary(BaseModel):
    """Summary statistics for a scenario"""
    scenario_type: str = Field(..., description="Type of scenario: buying or investment")

    # Final values
    final_value_median: float = Field(..., description="Median final value (50th percentile)")
    final_value_pessimistic: float = Field(..., description="Pessimistic final value (10th percentile)")
    final_value_optimistic: float = Field(..., description="Optimistic final value (90th percentile)")

    # Additional metrics
    total_invested: Optional[float] = Field(None, description="Total amount invested/paid")
    total_return: Optional[float] = Field(None, description="Total return (final - invested)")
    annualized_return: Optional[float] = Field(None, description="Annualized return rate in percent")

class BuyingScenarioResults(BaseModel):
    """Results for buying scenario"""
    summary: ScenarioSummary

    # Detailed metrics
    final_property_value: Dict[str, float] = Field(
        ...,
        description="Property value statistics (median, p10, p90)"
    )
    remaining_mortgage: float = Field(..., description="Remaining mortgage balance")
    total_maintenance_cost: Dict[str, float] = Field(..., description="Maintenance cost statistics")
    net_equity: Dict[str, float] = Field(..., description="Net equity statistics")

    # Monthly data for charts
    monthly_mortgage_balance: List[float] = Field(..., description="Mortgage balance over time")
    monthly_principal_paid: List[float] = Field(..., description="Principal paid each month")
    monthly_interest_paid: List[float] = Field(..., description="Interest paid each month")

    # Simulation paths (for visualization)
    property_value_paths: List[List[float]] = Field(
        ...,
        description="Property value simulation paths (limited to sample for response size)"
    )
    net_equity_paths: List[List[float]] = Field(
        ...,
        description="Net equity simulation paths"
    )

class InvestmentScenarioResults(BaseModel):
    """Results for investment scenario"""
    summary: ScenarioSummary

    # Final values
    final_value_untaxed: Dict[str, float] = Field(..., description="Untaxed value statistics")
    final_value_taxed: Dict[str, float] = Field(..., description="Taxed value statistics")

    # Simulation paths (for visualization)
    investment_paths_untaxed: List[List[float]] = Field(
        ...,
        description="Investment value paths before tax"
    )
    investment_paths_taxed: List[List[float]] = Field(
        ...,
        description="Investment value paths after tax"
    )

class ResultsResponse(BaseModel):
    """Complete results response"""
    simulation_id: str
    status: SimulationStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    # Results by scenario type
    buying_results: Optional[BuyingScenarioResults] = None
    investment_results: Optional[InvestmentScenarioResults] = None

    # Charts data
    charts: List[ChartData] = Field(default_factory=list, description="Pre-generated chart data")

    # Metadata
    simulation_params: Dict[str, Any] = Field(..., description="Original simulation parameters")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)
