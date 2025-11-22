/**
 * TypeScript types for TBONTB application
 * Mirrors the backend Pydantic models
 */

// ============================================================================
// Forecast & Financial Parameters
// ============================================================================

export interface ForecastParams {
  mu: number;  // Annual drift/expected return
  sigma: number;  // Annual volatility
}

export interface FinancialProfile {
  monthly_free_income: number[][];  // years x 12 months
  savings: number;
}

// ============================================================================
// Mortgage Types
// ============================================================================

export type MortgageType = 'fixed' | 'prime' | 'linked' | 'adjustable' | 'adjustablelinked';

export interface MortgageTrackParams {
  type: MortgageType;
  principal: number;
  term_years: number;
  interest_rate?: number;
  spread?: number;
}

export interface MortgageParams {
  [trackName: string]: MortgageTrackParams;
}

// ============================================================================
// Scenario Inputs
// ============================================================================

export interface BuyingScenarioInput {
  profile: FinancialProfile;
  apartment_price: number;
  down_payment: number;
  mortgage_params: MortgageParams;
  maintenance_cost_rate: number;
  fixed_maintenance_cost: number;
  forecast_params: ForecastParams;
  simulation_years: number;
  n_sim: number;
}

export interface InvestmentScenarioInput {
  profile: FinancialProfile;
  tax_rate: number;
  transaction_fee: number;
  percentage_management_fee: number;
  ILS_management_fee: number;
  initial_already_invested: boolean;
  forecast_params: ForecastParams;
  simulation_years: number;
  n_sim: number;
}

export interface ComparisonInput {
  buying_scenario?: BuyingScenarioInput;
  investment_scenario?: InvestmentScenarioInput;
}

// ============================================================================
// Results Types
// ============================================================================

export type SimulationStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface SimulationResponse {
  simulation_id: string;
  status: SimulationStatus;
  created_at: string;
  estimated_time_seconds?: number;
  message: string;
}

export interface PercentileStats {
  median: number;
  p10: number;
  p90: number;
  mean: number;
  std: number;
}

export interface ScenarioSummary {
  scenario_type: 'buying' | 'investment';
  final_value_median: number;
  final_value_pessimistic: number;
  final_value_optimistic: number;
  total_invested?: number;
  total_return?: number;
  annualized_return?: number;
}

export interface BuyingScenarioResults {
  summary: ScenarioSummary;
  final_property_value: PercentileStats;
  remaining_mortgage: number;
  total_maintenance_cost: PercentileStats;
  net_equity: PercentileStats;
  monthly_mortgage_balance: number[];
  monthly_principal_paid: number[];
  monthly_interest_paid: number[];
  property_value_paths: number[][];
  net_equity_paths: number[][];
}

export interface InvestmentScenarioResults {
  summary: ScenarioSummary;
  final_value_untaxed: PercentileStats;
  final_value_taxed: PercentileStats;
  investment_paths_untaxed: number[][];
  investment_paths_taxed: number[][];
}

export interface ChartData {
  type: string;
  data: any;
  layout?: any;
}

export interface ResultsResponse {
  simulation_id: string;
  status: SimulationStatus;
  created_at: string;
  completed_at?: string;
  buying_results?: BuyingScenarioResults;
  investment_results?: InvestmentScenarioResults;
  charts?: ChartData[];
  simulation_params: any;
}

export interface ErrorResponse {
  error: string;
  message: string;
  detail?: string;
  timestamp: string;
}

// ============================================================================
// Default Parameters
// ============================================================================

export interface DefaultParameters {
  simulation_years: number;
  n_simulations: number;
  stocks_tax_rate: number;
  forecast_params: {
    stocks: ForecastParams & { description: string };
    real_estate: ForecastParams & { description: string };
  };
  mortgage_types: MortgageType[];
  limits: {
    max_simulations: number;
    max_years: number;
    min_years: number;
  };
}

// ============================================================================
// Mortgage Preview
// ============================================================================

export interface MortgagePreview {
  total_loan_value: number;
  monthly_payment_first_year: number[];
  average_monthly_payment: number;
  total_interest_year_1: number;
  schedule_sample: any[];
}
