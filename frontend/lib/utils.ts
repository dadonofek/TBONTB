/**
 * Utility functions
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format number as currency (ILS)
 */
export function formatCurrency(amount: number, currency: string = 'ILS'): string {
  return new Intl.NumberFormat('he-IL', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format large numbers with commas
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Format percentage
 */
export function formatPercent(value: number, decimals: number = 2): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Create a grid of monthly income (all same value)
 */
export function createUniformIncome(monthlyAmount: number, years: number): number[][] {
  return Array(years).fill(null).map(() => Array(12).fill(monthlyAmount));
}

/**
 * Calculate total from monthly income grid
 */
export function calculateTotalIncome(monthlyIncome: number[][]): number {
  return monthlyIncome.reduce((total, year) =>
    total + year.reduce((yearTotal, month) => yearTotal + month, 0), 0
  );
}

/**
 * Validate positive number
 */
export function isPositiveNumber(value: any): boolean {
  return typeof value === 'number' && value > 0 && !isNaN(value);
}

/**
 * Validate non-negative number
 */
export function isNonNegativeNumber(value: any): boolean {
  return typeof value === 'number' && value >= 0 && !isNaN(value);
}

/**
 * Download data as JSON file
 */
export function downloadJSON(data: any, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Download data as CSV file
 */
export function downloadCSV(data: string, filename: string) {
  const blob = new Blob([data], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Convert results to CSV format
 */
export function resultsToCSV(results: any): string {
  const rows: string[] = [];

  // Header
  rows.push('Metric,Value');

  // Summary data
  if (results.buying_results) {
    const summary = results.buying_results.summary;
    rows.push(`Scenario Type,${summary.scenario_type}`);
    rows.push(`Final Value (Median),${summary.final_value_median}`);
    rows.push(`Final Value (10th percentile),${summary.final_value_pessimistic}`);
    rows.push(`Final Value (90th percentile),${summary.final_value_optimistic}`);
    rows.push(`Annualized Return,${summary.annualized_return}%`);
  }

  if (results.investment_results) {
    const summary = results.investment_results.summary;
    rows.push(`Scenario Type,${summary.scenario_type}`);
    rows.push(`Final Value (Median),${summary.final_value_median}`);
    rows.push(`Final Value (10th percentile),${summary.final_value_pessimistic}`);
    rows.push(`Final Value (90th percentile),${summary.final_value_optimistic}`);
    rows.push(`Annualized Return,${summary.annualized_return}%`);
  }

  return rows.join('\n');
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}
