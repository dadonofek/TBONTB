'use client';

import { useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import ResultsDisplay from '@/components/ResultsDisplay';
import {
  BuyingScenarioInput,
  InvestmentScenarioInput,
  ComparisonInput,
  ResultsResponse,
  MortgageTrackParams,
  MortgageType,
} from '@/types';

type ScenarioType = 'buying' | 'investment' | 'compare';

interface MortgageTrack {
  id: string;
  name: string;
  type: MortgageType;
  principal: number;
  term_years: number;
  interest_rate: number;
  spread: number;
}

// Default values matching main.py
const DEFAULT_VALUES = {
  // Financial Profile
  monthly_income: 10000,
  savings: 500000,

  // Buying Scenario
  apartment_price: 1800000,
  down_payment: 500000,
  maintenance_cost_rate: 0,
  fixed_maintenance_cost: 10000,
  apt_mu: 0.054,
  apt_sigma: 0.052,

  // Investment Scenario
  tax_rate: 25,
  transaction_fee: 0.07,
  percentage_management_fee: 0.1,
  ils_management_fee: 15,
  initial_already_invested: true,
  stocks_mu: 0.078,
  stocks_sigma: 0.15,

  // Simulation
  simulation_years: 30,
  n_simulations: 10000,
};

export default function SimulatePage() {
  const [selectedScenario, setSelectedScenario] = useState<ScenarioType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<ResultsResponse | null>(null);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);

  // Financial Profile State
  const [monthlyIncome, setMonthlyIncome] = useState(DEFAULT_VALUES.monthly_income);
  const [savings, setSavings] = useState(DEFAULT_VALUES.savings);

  // Buying Scenario State
  const [apartmentPrice, setApartmentPrice] = useState(DEFAULT_VALUES.apartment_price);
  const [downPayment, setDownPayment] = useState(DEFAULT_VALUES.down_payment);
  const [maintenanceCostRate, setMaintenanceCostRate] = useState(DEFAULT_VALUES.maintenance_cost_rate);
  const [fixedMaintenanceCost, setFixedMaintenanceCost] = useState(DEFAULT_VALUES.fixed_maintenance_cost);
  const [aptMu, setAptMu] = useState(DEFAULT_VALUES.apt_mu);
  const [aptSigma, setAptSigma] = useState(DEFAULT_VALUES.apt_sigma);
  const [mortgageTracks, setMortgageTracks] = useState<MortgageTrack[]>([
    {
      id: '1',
      name: 'fixed_mortgage',
      type: 'fixed',
      principal: 650000,
      term_years: 30,
      interest_rate: 4.0,
      spread: 0,
    },
    {
      id: '2',
      name: 'prime_mortgage',
      type: 'prime',
      principal: 650000,
      term_years: 30,
      interest_rate: 4.5,
      spread: -0.5,
    },
  ]);

  // Investment Scenario State
  const [taxRate, setTaxRate] = useState(DEFAULT_VALUES.tax_rate);
  const [transactionFee, setTransactionFee] = useState(DEFAULT_VALUES.transaction_fee);
  const [percentageManagementFee, setPercentageManagementFee] = useState(DEFAULT_VALUES.percentage_management_fee);
  const [ilsManagementFee, setIlsManagementFee] = useState(DEFAULT_VALUES.ils_management_fee);
  const [initialAlreadyInvested, setInitialAlreadyInvested] = useState(DEFAULT_VALUES.initial_already_invested);
  const [stocksMu, setStocksMu] = useState(DEFAULT_VALUES.stocks_mu);
  const [stocksSigma, setStocksSigma] = useState(DEFAULT_VALUES.stocks_sigma);

  // Simulation Parameters State
  const [simulationYears, setSimulationYears] = useState(DEFAULT_VALUES.simulation_years);
  const [nSimulations, setNSimulations] = useState(DEFAULT_VALUES.n_simulations);

  // Helper to generate monthly income schedule
  const generateIncomeSchedule = (income: number, years: number): number[][] => {
    return Array(years).fill(null).map(() => Array(12).fill(income));
  };

  // Add new mortgage track
  const addMortgageTrack = () => {
    const newId = String(Date.now());
    setMortgageTracks([
      ...mortgageTracks,
      {
        id: newId,
        name: `mortgage_${mortgageTracks.length + 1}`,
        type: 'fixed',
        principal: 100000,
        term_years: 30,
        interest_rate: 4.0,
        spread: 0,
      },
    ]);
  };

  // Remove mortgage track
  const removeMortgageTrack = (id: string) => {
    if (mortgageTracks.length > 1) {
      setMortgageTracks(mortgageTracks.filter(track => track.id !== id));
    }
  };

  // Update mortgage track
  const updateMortgageTrack = (id: string, field: keyof MortgageTrack, value: string | number) => {
    setMortgageTracks(mortgageTracks.map(track =>
      track.id === id ? { ...track, [field]: value } : track
    ));
  };

  // Calculate total mortgage
  const totalMortgage = mortgageTracks.reduce((sum, track) => sum + track.principal, 0);
  const mortgageValid = totalMortgage + downPayment === apartmentPrice;

  // Build buying scenario input
  const buildBuyingInput = (): BuyingScenarioInput => {
    const mortgageParams: { [key: string]: MortgageTrackParams } = {};
    mortgageTracks.forEach(track => {
      const params: MortgageTrackParams = {
        type: track.type,
        principal: track.principal,
        term_years: track.term_years,
        interest_rate: track.interest_rate,
      };

      // Only add spread for prime mortgages
      if (track.type === 'prime') {
        params.spread = track.spread;
      }

      mortgageParams[track.name] = params;
    });

    return {
      profile: {
        monthly_free_income: generateIncomeSchedule(monthlyIncome, simulationYears),
        savings: savings,
      },
      apartment_price: apartmentPrice,
      down_payment: downPayment,
      mortgage_params: mortgageParams,
      maintenance_cost_rate: maintenanceCostRate,
      fixed_maintenance_cost: fixedMaintenanceCost,
      forecast_params: { mu: aptMu, sigma: aptSigma },
      simulation_years: simulationYears,
      n_sim: nSimulations,
    };
  };

  // Build investment scenario input
  const buildInvestmentInput = (): InvestmentScenarioInput => {
    return {
      profile: {
        monthly_free_income: generateIncomeSchedule(monthlyIncome, simulationYears),
        savings: savings,
      },
      tax_rate: taxRate,
      transaction_fee: transactionFee,
      percentage_management_fee: percentageManagementFee,
      ILS_management_fee: ilsManagementFee,
      initial_already_invested: initialAlreadyInvested,
      forecast_params: { mu: stocksMu, sigma: stocksSigma },
      simulation_years: simulationYears,
      n_sim: nSimulations,
    };
  };

  // Run simulation
  const runSimulation = async () => {
    if (!selectedScenario) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      let response: ResultsResponse;

      if (selectedScenario === 'buying') {
        if (!mortgageValid) {
          throw new Error('Mortgage + Down Payment must equal Apartment Price');
        }
        response = await api.simulateBuying(buildBuyingInput());
      } else if (selectedScenario === 'investment') {
        response = await api.simulateInvestment(buildInvestmentInput());
      } else {
        // Compare both
        if (!mortgageValid) {
          throw new Error('Mortgage + Down Payment must equal Apartment Price');
        }
        const input: ComparisonInput = {
          buying_scenario: buildBuyingInput(),
          investment_scenario: buildInvestmentInput(),
        };
        response = await api.compareScenarios(input);
      }

      setResults(response);
    } catch (err) {
      console.error('Simulation error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred during simulation');
    } finally {
      setIsLoading(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <Link href="/" className="text-indigo-600 hover:text-indigo-800 mb-4 inline-block">
            &larr; Back to Home
          </Link>
          <h1 className="text-4xl font-bold text-indigo-900">Start Your Simulation</h1>
          <p className="text-indigo-700 mt-2">
            Choose a scenario type and configure your parameters
          </p>
        </header>

        {/* Scenario Selection */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Buying Scenario */}
          <button
            onClick={() => { setSelectedScenario('buying'); resetForm(); }}
            className={`p-6 rounded-lg shadow-lg transition-all text-left ${
              selectedScenario === 'buying'
                ? 'bg-indigo-600 text-white ring-4 ring-indigo-300'
                : 'bg-white hover:shadow-xl'
            }`}
          >
            <div className="text-4xl mb-4">🏠</div>
            <h3 className={`text-xl font-bold mb-2 ${
              selectedScenario === 'buying' ? 'text-white' : 'text-gray-900'
            }`}>
              Buying Scenario
            </h3>
            <p className={selectedScenario === 'buying' ? 'text-indigo-100' : 'text-gray-700'}>
              Simulate apartment purchase with mortgage, property appreciation, and maintenance costs
            </p>
          </button>

          {/* Investment Scenario */}
          <button
            onClick={() => { setSelectedScenario('investment'); resetForm(); }}
            className={`p-6 rounded-lg shadow-lg transition-all text-left ${
              selectedScenario === 'investment'
                ? 'bg-indigo-600 text-white ring-4 ring-indigo-300'
                : 'bg-white hover:shadow-xl'
            }`}
          >
            <div className="text-4xl mb-4">📈</div>
            <h3 className={`text-xl font-bold mb-2 ${
              selectedScenario === 'investment' ? 'text-white' : 'text-gray-900'
            }`}>
              Investment Scenario
            </h3>
            <p className={selectedScenario === 'investment' ? 'text-indigo-100' : 'text-gray-700'}>
              Model direct investment portfolios with fees, taxes, and market volatility
            </p>
          </button>

          {/* Compare Scenarios */}
          <button
            onClick={() => { setSelectedScenario('compare'); resetForm(); }}
            className={`p-6 rounded-lg shadow-lg transition-all text-left ${
              selectedScenario === 'compare'
                ? 'bg-indigo-600 text-white ring-4 ring-indigo-300'
                : 'bg-white hover:shadow-xl'
            }`}
          >
            <div className="text-4xl mb-4">⚖️</div>
            <h3 className={`text-xl font-bold mb-2 ${
              selectedScenario === 'compare' ? 'text-white' : 'text-gray-900'
            }`}>
              Compare Scenarios
            </h3>
            <p className={selectedScenario === 'compare' ? 'text-indigo-100' : 'text-gray-700'}>
              Side-by-side comparison of buying vs investing scenarios
            </p>
          </button>
        </div>

        {/* Configuration Form */}
        {selectedScenario && (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {selectedScenario === 'buying' && 'Configure Buying Scenario'}
              {selectedScenario === 'investment' && 'Configure Investment Scenario'}
              {selectedScenario === 'compare' && 'Configure Comparison'}
            </h2>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            <div className="space-y-8">
              {/* Financial Profile Section */}
              <div className="border-b pb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Profile</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Monthly Free Income (ILS)
                    </label>
                    <input
                      type="number"
                      value={monthlyIncome}
                      onChange={(e) => setMonthlyIncome(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                    />
                    <p className="text-xs text-gray-500 mt-1">Income available after expenses</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Savings (ILS)
                    </label>
                    <input
                      type="number"
                      value={savings}
                      onChange={(e) => setSavings(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                    />
                    <p className="text-xs text-gray-500 mt-1">Initial capital available</p>
                  </div>
                </div>
              </div>

              {/* Buying Scenario Fields */}
              {(selectedScenario === 'buying' || selectedScenario === 'compare') && (
                <div className="border-b pb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Property Details</h3>

                  <div className="grid md:grid-cols-3 gap-4 mb-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Apartment Price (ILS)
                      </label>
                      <input
                        type="number"
                        value={apartmentPrice}
                        onChange={(e) => setApartmentPrice(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Down Payment (ILS)
                      </label>
                      <input
                        type="number"
                        value={downPayment}
                        onChange={(e) => setDownPayment(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Total Mortgage
                      </label>
                      <div className={`px-3 py-2 rounded-md ${mortgageValid ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                        {totalMortgage.toLocaleString()} ILS
                        {!mortgageValid && (
                          <span className="text-xs block">
                            Should be {(apartmentPrice - downPayment).toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Maintenance Cost Rate (% of property value)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={maintenanceCostRate}
                        onChange={(e) => setMaintenanceCostRate(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Fixed Annual Maintenance (ILS)
                      </label>
                      <input
                        type="number"
                        value={fixedMaintenanceCost}
                        onChange={(e) => setFixedMaintenanceCost(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                      />
                    </div>
                  </div>

                  {/* Mortgage Tracks */}
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-medium text-gray-900">Mortgage Tracks</h4>
                      <button
                        type="button"
                        onClick={addMortgageTrack}
                        className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-md hover:bg-indigo-200 text-sm"
                      >
                        + Add Track
                      </button>
                    </div>

                    {mortgageTracks.map((track, index) => (
                      <div key={track.id} className="bg-gray-50 p-4 rounded-lg mb-3">
                        <div className="flex justify-between items-center mb-3">
                          <span className="font-medium text-gray-700">Track {index + 1}</span>
                          {mortgageTracks.length > 1 && (
                            <button
                              type="button"
                              onClick={() => removeMortgageTrack(track.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                        <div className="grid md:grid-cols-5 gap-3">
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Type</label>
                            <select
                              value={track.type}
                              onChange={(e) => updateMortgageTrack(track.id, 'type', e.target.value as MortgageType)}
                              className="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm text-gray-900"
                            >
                              <option value="fixed">Fixed</option>
                              <option value="prime">Prime</option>
                              <option value="linked">CPI-Linked</option>
                              <option value="adjustable">Adjustable</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Principal (ILS)</label>
                            <input
                              type="number"
                              value={track.principal}
                              onChange={(e) => updateMortgageTrack(track.id, 'principal', Number(e.target.value))}
                              className="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm text-gray-900"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Term (Years)</label>
                            <input
                              type="number"
                              value={track.term_years}
                              onChange={(e) => updateMortgageTrack(track.id, 'term_years', Number(e.target.value))}
                              className="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm text-gray-900"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Interest Rate (%)</label>
                            <input
                              type="number"
                              step="0.1"
                              value={track.interest_rate}
                              onChange={(e) => updateMortgageTrack(track.id, 'interest_rate', Number(e.target.value))}
                              className="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm text-gray-900"
                            />
                          </div>
                          {track.type === 'prime' && (
                            <div>
                              <label className="block text-xs text-gray-600 mb-1">Spread (%)</label>
                              <input
                                type="number"
                                step="0.1"
                                value={track.spread}
                                onChange={(e) => updateMortgageTrack(track.id, 'spread', Number(e.target.value))}
                                className="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm text-gray-900"
                              />
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Investment Scenario Fields */}
              {(selectedScenario === 'investment' || selectedScenario === 'compare') && (
                <div className="border-b pb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Details</h3>

                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Capital Gains Tax Rate (%)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={taxRate}
                        onChange={(e) => setTaxRate(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Transaction Fee (%)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={transactionFee}
                        onChange={(e) => setTransactionFee(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Management Fee (% per year)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={percentageManagementFee}
                        onChange={(e) => setPercentageManagementFee(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Fixed Management Fee (ILS/month)
                      </label>
                      <input
                        type="number"
                        value={ilsManagementFee}
                        onChange={(e) => setIlsManagementFee(Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                      />
                    </div>
                  </div>

                  <div className="mb-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={initialAlreadyInvested}
                        onChange={(e) => setInitialAlreadyInvested(e.target.checked)}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        Initial savings already invested (no transaction fee on initial amount)
                      </span>
                    </label>
                  </div>
                </div>
              )}

              {/* Simulation Parameters */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Simulation Parameters</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Simulation Years
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={simulationYears}
                      onChange={(e) => setSimulationYears(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                    />
                    <p className="text-xs text-gray-500 mt-1">1-50 years</p>
                  </div>

                  {/* Advanced Settings Toggle */}
                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                      className="flex items-center gap-2 text-indigo-600 hover:text-indigo-800 font-medium text-sm"
                    >
                      <svg
                        className={`w-4 h-4 transition-transform ${showAdvancedSettings ? 'rotate-90' : ''}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                      Advanced Settings
                    </button>
                  </div>

                  {/* Advanced Settings Content */}
                  {showAdvancedSettings && (
                    <div className="pl-6 space-y-6 border-l-2 border-indigo-200">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Number of Simulations
                        </label>
                        <input
                          type="number"
                          min="100"
                          max="50000"
                          step="100"
                          value={nSimulations}
                          onChange={(e) => setNSimulations(Number(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                        />
                        <p className="text-xs text-gray-500 mt-1">100-50,000 (higher = more accurate, slower)</p>
                      </div>

                      {/* Property Forecast Parameters */}
                      {(selectedScenario === 'buying' || selectedScenario === 'compare') && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-3">Property Forecast Parameters</h4>
                          <div className="grid md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Expected Annual Appreciation (mu)
                              </label>
                              <input
                                type="number"
                                step="0.001"
                                value={aptMu}
                                onChange={(e) => setAptMu(Number(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                              />
                              <p className="text-xs text-gray-500 mt-1">Historical: ~5.4% for real estate</p>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Volatility (sigma)
                              </label>
                              <input
                                type="number"
                                step="0.001"
                                value={aptSigma}
                                onChange={(e) => setAptSigma(Number(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                              />
                              <p className="text-xs text-gray-500 mt-1">Historical: ~5.2% for real estate</p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Stock Market Forecast Parameters */}
                      {(selectedScenario === 'investment' || selectedScenario === 'compare') && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-3">Stock Market Forecast Parameters</h4>
                          <div className="grid md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Expected Annual Return (mu)
                              </label>
                              <input
                                type="number"
                                step="0.001"
                                value={stocksMu}
                                onChange={(e) => setStocksMu(Number(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                              />
                              <p className="text-xs text-gray-500 mt-1">Historical S&P 500: ~7.8%</p>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Volatility (sigma)
                              </label>
                              <input
                                type="number"
                                step="0.001"
                                value={stocksSigma}
                                onChange={(e) => setStocksSigma(Number(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                              />
                              <p className="text-xs text-gray-500 mt-1">Historical S&P 500: ~15%</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-4">
                <button
                  onClick={runSimulation}
                  disabled={isLoading || (selectedScenario !== 'investment' && !mortgageValid)}
                  className={`w-full font-bold py-3 px-6 rounded-lg transition-colors ${
                    isLoading || (selectedScenario !== 'investment' && !mortgageValid)
                      ? 'bg-gray-400 text-white cursor-not-allowed'
                      : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                  }`}
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Running Simulation...
                    </span>
                  ) : (
                    'Run Simulation'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Results Display */}
        {results && selectedScenario && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <ResultsDisplay results={results} scenarioType={selectedScenario} />
          </div>
        )}

        {/* Info Section */}
        <div className="mt-8 text-center text-gray-600">
          <p>
            Powered by Monte Carlo simulations with {nSimulations.toLocaleString()} iterations for accurate probability distributions
          </p>
        </div>
      </div>
    </div>
  );
}
