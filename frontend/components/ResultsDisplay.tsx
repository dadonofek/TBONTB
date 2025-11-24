'use client';

import dynamic from 'next/dynamic';
import { ResultsResponse, BuyingScenarioResults, InvestmentScenarioResults } from '@/types';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface ResultsDisplayProps {
  results: ResultsResponse;
  scenarioType: 'buying' | 'investment' | 'compare';
}

function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-IL', {
    maximumFractionDigits: 0,
  }).format(num);
}

function formatPercent(num: number): string {
  return `${(num * 100).toFixed(2)}%`;
}

function SummaryCard({ title, value, subtitle, color }: {
  title: string;
  value: string;
  subtitle?: string;
  color: 'blue' | 'green' | 'red' | 'purple';
}) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    green: 'bg-green-50 border-green-200 text-green-800',
    red: 'bg-red-50 border-red-200 text-red-800',
    purple: 'bg-purple-50 border-purple-200 text-purple-800',
  };

  return (
    <div className={`p-4 rounded-lg border ${colorClasses[color]}`}>
      <p className="text-sm font-medium opacity-75">{title}</p>
      <p className="text-2xl font-bold">{value}</p>
      {subtitle && <p className="text-sm opacity-75">{subtitle}</p>}
    </div>
  );
}

function BuyingResultsSection({ results }: { results: BuyingScenarioResults }) {
  const { summary, final_property_value, net_equity, total_maintenance_cost, remaining_mortgage } = results;

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-bold text-gray-900">Buying Scenario Results</h3>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          title="Median Net Equity"
          value={`${formatNumber(summary.final_value_median)} ILS`}
          color="blue"
        />
        <SummaryCard
          title="Pessimistic (10th %)"
          value={`${formatNumber(summary.final_value_pessimistic)} ILS`}
          color="red"
        />
        <SummaryCard
          title="Optimistic (90th %)"
          value={`${formatNumber(summary.final_value_optimistic)} ILS`}
          color="green"
        />
        <SummaryCard
          title="Remaining Mortgage"
          value={`${formatNumber(remaining_mortgage)} ILS`}
          color="purple"
        />
      </div>

      {/* Property Value Stats */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="font-semibold text-gray-900 mb-3">Final Property Value Distribution</h4>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Median: </span>
            <span className="font-medium">{formatNumber(final_property_value.median)} ILS</span>
          </div>
          <div>
            <span className="text-gray-600">10th Percentile: </span>
            <span className="font-medium">{formatNumber(final_property_value.p10)} ILS</span>
          </div>
          <div>
            <span className="text-gray-600">90th Percentile: </span>
            <span className="font-medium">{formatNumber(final_property_value.p90)} ILS</span>
          </div>
        </div>
      </div>

      {/* Charts */}
      {results.net_equity_paths && results.net_equity_paths.length > 0 && (
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-3">Net Equity Over Time</h4>
          <Plot
            data={[
              {
                type: 'scatter',
                mode: 'lines',
                y: results.net_equity_paths[Math.floor(results.net_equity_paths.length / 2)],
                name: 'Median Path',
                line: { color: 'blue', width: 2 },
              },
            ]}
            layout={{
              height: 400,
              margin: { t: 30, r: 30, b: 50, l: 80 },
              xaxis: { title: 'Months' },
              yaxis: { title: 'Net Equity (ILS)' },
              showlegend: true,
            }}
            config={{ responsive: true }}
            style={{ width: '100%' }}
          />
        </div>
      )}
    </div>
  );
}

function InvestmentResultsSection({ results }: { results: InvestmentScenarioResults }) {
  const { summary, final_value_untaxed, final_value_taxed } = results;

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-bold text-gray-900">Investment Scenario Results</h3>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          title="Median Value (Taxed)"
          value={`${formatNumber(summary.final_value_median)} ILS`}
          color="blue"
        />
        <SummaryCard
          title="Pessimistic (10th %)"
          value={`${formatNumber(summary.final_value_pessimistic)} ILS`}
          color="red"
        />
        <SummaryCard
          title="Optimistic (90th %)"
          value={`${formatNumber(summary.final_value_optimistic)} ILS`}
          color="green"
        />
        <SummaryCard
          title="Annualized Return"
          value={summary.annualized_return ? formatPercent(summary.annualized_return) : 'N/A'}
          color="purple"
        />
      </div>

      {/* Value Stats */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-3">Final Value (Before Tax)</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Median:</span>
              <span className="font-medium">{formatNumber(final_value_untaxed.median)} ILS</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">10th Percentile:</span>
              <span className="font-medium">{formatNumber(final_value_untaxed.p10)} ILS</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">90th Percentile:</span>
              <span className="font-medium">{formatNumber(final_value_untaxed.p90)} ILS</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-3">Final Value (After Tax)</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Median:</span>
              <span className="font-medium">{formatNumber(final_value_taxed.median)} ILS</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">10th Percentile:</span>
              <span className="font-medium">{formatNumber(final_value_taxed.p10)} ILS</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">90th Percentile:</span>
              <span className="font-medium">{formatNumber(final_value_taxed.p90)} ILS</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      {results.investment_paths_taxed && results.investment_paths_taxed.length > 0 && (
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-3">Investment Value Over Time</h4>
          <Plot
            data={[
              {
                type: 'scatter',
                mode: 'lines',
                y: results.investment_paths_taxed[Math.floor(results.investment_paths_taxed.length / 2)],
                name: 'Median Path (Taxed)',
                line: { color: 'green', width: 2 },
              },
            ]}
            layout={{
              height: 400,
              margin: { t: 30, r: 30, b: 50, l: 80 },
              xaxis: { title: 'Months' },
              yaxis: { title: 'Investment Value (ILS)' },
              showlegend: true,
            }}
            config={{ responsive: true }}
            style={{ width: '100%' }}
          />
        </div>
      )}
    </div>
  );
}

function ComparisonSection({ buyingResults, investmentResults }: {
  buyingResults: BuyingScenarioResults;
  investmentResults: InvestmentScenarioResults;
}) {
  const buyingMedian = buyingResults.summary.final_value_median;
  const investmentMedian = investmentResults.summary.final_value_median;
  const difference = investmentMedian - buyingMedian;
  const winner = difference > 0 ? 'Investment' : 'Buying';

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-bold text-gray-900">Comparison Summary</h3>

      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6 text-center">
        <p className="text-lg text-indigo-800 mb-2">
          Based on median outcomes, <span className="font-bold">{winner}</span> scenario performs better
        </p>
        <p className="text-3xl font-bold text-indigo-900">
          Difference: {formatNumber(Math.abs(difference))} ILS
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-4">Buying Scenario</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Median Net Equity:</span>
              <span className="font-medium">{formatNumber(buyingMedian)} ILS</span>
            </div>
            <div className="flex justify-between text-green-600">
              <span>Optimistic:</span>
              <span className="font-medium">{formatNumber(buyingResults.summary.final_value_optimistic)} ILS</span>
            </div>
            <div className="flex justify-between text-red-600">
              <span>Pessimistic:</span>
              <span className="font-medium">{formatNumber(buyingResults.summary.final_value_pessimistic)} ILS</span>
            </div>
          </div>
        </div>

        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-4">Investment Scenario</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Median Value:</span>
              <span className="font-medium">{formatNumber(investmentMedian)} ILS</span>
            </div>
            <div className="flex justify-between text-green-600">
              <span>Optimistic:</span>
              <span className="font-medium">{formatNumber(investmentResults.summary.final_value_optimistic)} ILS</span>
            </div>
            <div className="flex justify-between text-red-600">
              <span>Pessimistic:</span>
              <span className="font-medium">{formatNumber(investmentResults.summary.final_value_pessimistic)} ILS</span>
            </div>
          </div>
        </div>
      </div>

      {/* Comparison Chart */}
      <div className="bg-white border rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-3">Side-by-Side Comparison</h4>
        <Plot
          data={[
            {
              type: 'bar',
              name: 'Buying',
              x: ['Pessimistic', 'Median', 'Optimistic'],
              y: [
                buyingResults.summary.final_value_pessimistic,
                buyingResults.summary.final_value_median,
                buyingResults.summary.final_value_optimistic
              ],
              marker: { color: '#4F46E5' },
            },
            {
              type: 'bar',
              name: 'Investment',
              x: ['Pessimistic', 'Median', 'Optimistic'],
              y: [
                investmentResults.summary.final_value_pessimistic,
                investmentResults.summary.final_value_median,
                investmentResults.summary.final_value_optimistic
              ],
              marker: { color: '#10B981' },
            },
          ]}
          layout={{
            height: 400,
            margin: { t: 30, r: 30, b: 50, l: 80 },
            barmode: 'group',
            yaxis: { title: 'Value (ILS)' },
            showlegend: true,
            legend: { orientation: 'h', y: -0.15 },
          }}
          config={{ responsive: true }}
          style={{ width: '100%' }}
        />
      </div>
    </div>
  );
}

export default function ResultsDisplay({ results, scenarioType }: ResultsDisplayProps) {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Simulation Results</h2>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          results.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
        }`}>
          {results.status}
        </span>
      </div>

      {scenarioType === 'buying' && results.buying_results && (
        <BuyingResultsSection results={results.buying_results} />
      )}

      {scenarioType === 'investment' && results.investment_results && (
        <InvestmentResultsSection results={results.investment_results} />
      )}

      {scenarioType === 'compare' && results.buying_results && results.investment_results && (
        <>
          <ComparisonSection
            buyingResults={results.buying_results}
            investmentResults={results.investment_results}
          />
          <div className="border-t pt-8">
            <BuyingResultsSection results={results.buying_results} />
          </div>
          <div className="border-t pt-8">
            <InvestmentResultsSection results={results.investment_results} />
          </div>
        </>
      )}
    </div>
  );
}
