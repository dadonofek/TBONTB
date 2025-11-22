/**
 * API client for TBONTB backend
 */

import {
  BuyingScenarioInput,
  InvestmentScenarioInput,
  ComparisonInput,
  ResultsResponse,
  DefaultParameters,
  MortgagePreview,
  ErrorResponse
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIError extends Error {
  constructor(public status: number, message: string, public detail?: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData: ErrorResponse = await response.json().catch(() => ({
      error: 'UnknownError',
      message: 'An unknown error occurred',
      timestamp: new Date().toISOString()
    }));

    throw new APIError(
      response.status,
      errorData.message || `HTTP ${response.status}`,
      errorData.detail
    );
  }

  return response.json();
}

export const api = {
  // ============================================================================
  // Simulation Endpoints
  // ============================================================================

  async simulateBuying(input: BuyingScenarioInput): Promise<ResultsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/simulate/buying`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(input),
    });

    return handleResponse<ResultsResponse>(response);
  },

  async simulateInvestment(input: InvestmentScenarioInput): Promise<ResultsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/simulate/investment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(input),
    });

    return handleResponse<ResultsResponse>(response);
  },

  async compareScenarios(input: ComparisonInput): Promise<ResultsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/simulate/compare`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(input),
    });

    return handleResponse<ResultsResponse>(response);
  },

  // ============================================================================
  // Parameters & Utilities
  // ============================================================================

  async getDefaultParameters(): Promise<DefaultParameters> {
    const response = await fetch(`${API_BASE_URL}/api/v1/parameters/defaults`);
    return handleResponse<DefaultParameters>(response);
  },

  async previewMortgage(mortgageParams: any): Promise<MortgagePreview> {
    const response = await fetch(`${API_BASE_URL}/api/v1/mortgage/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(mortgageParams),
    });

    return handleResponse<MortgagePreview>(response);
  },

  // ============================================================================
  // Health & Info
  // ============================================================================

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return handleResponse<{ status: string }>(response);
  },

  async getInfo(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/v1/info`);
    return handleResponse<any>(response);
  },
};

export { APIError };
