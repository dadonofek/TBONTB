'use client';

import { useState } from 'react';
import Link from 'next/link';

type ScenarioType = 'buying' | 'investment' | 'compare';

export default function SimulatePage() {
  const [selectedScenario, setSelectedScenario] = useState<ScenarioType | null>(null);
  const [isLoading, setIsLoading] = useState(false);

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
            Choose a scenario type to begin your financial analysis
          </p>
        </header>

        {/* Scenario Selection */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Buying Scenario */}
          <button
            onClick={() => setSelectedScenario('buying')}
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
            onClick={() => setSelectedScenario('investment')}
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
            onClick={() => setSelectedScenario('compare')}
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

        {/* Selected Scenario Form */}
        {selectedScenario && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {selectedScenario === 'buying' && 'Configure Buying Scenario'}
              {selectedScenario === 'investment' && 'Configure Investment Scenario'}
              {selectedScenario === 'compare' && 'Configure Comparison'}
            </h2>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <p className="text-yellow-800">
                <strong>Coming Soon:</strong> Full form configuration is under development.
                The simulation engine is ready - this UI will allow you to input your parameters.
              </p>
            </div>

            {/* Basic Form Preview */}
            <div className="space-y-6">
              {/* Financial Profile Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Financial Profile</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Monthly Free Income
                    </label>
                    <input
                      type="number"
                      placeholder="e.g., 15000"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                      disabled
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Savings
                    </label>
                    <input
                      type="number"
                      placeholder="e.g., 500000"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                      disabled
                    />
                  </div>
                </div>
              </div>

              {/* Scenario-specific fields */}
              {selectedScenario === 'buying' && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Property Details</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Apartment Price
                      </label>
                      <input
                        type="number"
                        placeholder="e.g., 2000000"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                        disabled
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Down Payment
                      </label>
                      <input
                        type="number"
                        placeholder="e.g., 500000"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                        disabled
                      />
                    </div>
                  </div>
                </div>
              )}

              {selectedScenario === 'investment' && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Investment Details</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tax Rate (%)
                      </label>
                      <input
                        type="number"
                        placeholder="e.g., 25"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                        disabled
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Management Fee (%)
                      </label>
                      <input
                        type="number"
                        placeholder="e.g., 0.5"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                        disabled
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Simulation Parameters */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Simulation Parameters</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Simulation Years
                    </label>
                    <input
                      type="number"
                      placeholder="30"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                      disabled
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Number of Simulations
                    </label>
                    <input
                      type="number"
                      placeholder="10000"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                      disabled
                    />
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-4">
                <button
                  disabled
                  className="w-full bg-gray-400 text-white font-bold py-3 px-6 rounded-lg cursor-not-allowed"
                >
                  Run Simulation (Coming Soon)
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Info Section */}
        <div className="mt-8 text-center text-gray-600">
          <p>
            Powered by Monte Carlo simulations with {'>'}10,000 iterations for accurate probability distributions
          </p>
        </div>
      </div>
    </div>
  );
}
