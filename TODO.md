# TBONTB Frontend Implementation TODO

## Goal
Get all configs from the user via the frontend, run simulations, display results, and compare between them.

## Status: COMPLETED

---

## open bugs:

- 1- light gry in frontend. fix all occurences.

- 2- plot looks wired. what exactly are we plotting? what is the x axis?
---

## Phase 1: Setup & Infrastructure
- [x] Explore codebase structure
- [x] Understand main.py configurations
- [x] Review existing frontend types and API client
- [x] Verify backend is running
- [x] Verify frontend dev server works

## Phase 2: Form Implementation
### Financial Profile (Shared Component)
- [x] Create reusable FinancialProfileForm component
  - Monthly free income input
  - Current savings input

### Buying Scenario Form
- [x] Apartment price input
- [x] Down payment input
- [x] Mortgage configuration (multi-track support)
  - Mortgage type selector (fixed, prime, linked, adjustable)
  - Principal amount
  - Term (years)
  - Interest rate
  - Spread (for prime mortgages)
- [x] Maintenance cost rate input
- [x] Fixed maintenance cost input
- [x] Forecast params (mu, sigma) with sensible defaults
- [x] Add/remove mortgage tracks dynamically

### Investment Scenario Form
- [x] Tax rate input
- [x] Transaction fee input
- [x] Percentage management fee input
- [x] Fixed management fee (ILS) input
- [x] Initial already invested toggle
- [x] Forecast params (mu, sigma) with sensible defaults

### Simulation Parameters (Shared)
- [x] Simulation years input (1-50)
- [x] Number of simulations input (100-50,000)

## Phase 3: Results Display
- [x] Create ResultsDisplay component
- [x] Summary cards showing:
  - Median final value
  - Pessimistic (10th percentile)
  - Optimistic (90th percentile)
  - Total return / Annualized return
- [x] Monte Carlo paths visualization using Plotly
- [x] Property value / Investment value charts
- [x] Net equity visualization (for buying)

## Phase 4: Comparison View
- [x] Side-by-side results display
- [x] Comparison chart overlay
- [x] Winner/difference summary

## Phase 5: Polish & Testing
- [x] Error handling and display
- [x] Loading states
- [x] Test all button interactions

---

## What Was Implemented

### Simulate Page (`/simulate`)
1. **Scenario Selection**: Three clickable cards (Buying, Investment, Compare)
2. **Financial Profile Form**: Monthly income and savings inputs
3. **Buying Scenario Form**:
   - Apartment price, down payment with validation
   - Dynamic mortgage tracks (add/remove)
   - Mortgage types: fixed, prime, CPI-linked, adjustable
   - Maintenance costs (rate + fixed)
   - GBM forecast parameters (mu, sigma)
4. **Investment Scenario Form**:
   - Tax rate, transaction fees, management fees
   - Initial invested toggle
   - GBM forecast parameters (mu, sigma)
5. **Simulation Parameters**: Years (1-50), Number of simulations (100-50,000)
6. **Run Simulation Button**: Connects to backend API

### ResultsDisplay Component
1. **Summary Cards**: Median, pessimistic, optimistic values
2. **Detailed Stats**: Property/investment value distributions
3. **Plotly Charts**: Monte Carlo path visualization
4. **Comparison View**: Side-by-side comparison with bar charts

### API Integration
- `api.simulateBuying()` - Buying scenario
- `api.simulateInvestment()` - Investment scenario
- `api.compareScenarios()` - Compare both

---

## Configuration Reference (from main.py)

### Financial Profile
```python
USER_FREE_INCOME = [[10000] * 12 for _ in range(SIMULATION_YEARS)]  # Monthly for each year
USER_SAVINGS = 500000
```

### Buying Scenario
```python
APARTMENT_PRICE = 1800000
DOWN_PAYMENT = 500000
MAINTENANCE_COST_RATE = 0.0  # % of property value
FIXED_MAINTENANCE_COST = 10000  # Annual in ILS
APT_FORECAST_PARAMS = {'mu': 0.054, 'sigma': 0.052}
mortgage_params = {
    "fixed_mortgage": {
        "type": "fixed",
        "principal": 650000,
        "term_years": 30,
        "interest_rate": 4.0
    },
    "prime_mortgage": {
        "type": "prime",
        "principal": 650000,
        "term_years": 30,
        "interest_rate": 4.5,
        "spread": -0.5
    }
}
```

### Investment Scenario
```python
STOCKS_TAX_RATE = 25  # %
TRANSACTION_FEES = 0.07  # %
PR_MANAGEMENT_FEE = 0.1  # % per year
ILS_MANAGEMENT_FEE = 15  # ILS per month
FORTUNE_INVESTED = True
STOCKS_FORECAST_PARAMS = {'mu': 0.078, 'sigma': 0.15}
```

### Simulation Settings
```python
SIMULATION_YEARS = 30
N_SIM = 10000
```
