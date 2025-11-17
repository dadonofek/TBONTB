# TBONTB Backend API

FastAPI backend for the TBONTB (To Buy Or Not To Buy) financial simulation application.

## Setup

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to configure your settings.

### Run Development Server

```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Simulations

- `POST /api/v1/simulate/buying` - Run buying scenario simulation
- `POST /api/v1/simulate/investment` - Run investment scenario simulation
- `POST /api/v1/simulate/compare` - Compare multiple scenarios

### Utilities

- `GET /api/v1/parameters/defaults` - Get default parameters
- `POST /api/v1/mortgage/preview` - Preview mortgage payments

### Info

- `GET /api/health` - Health check
- `GET /api/v1/info` - API information

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic
│   ├── core/         # Configuration
│   └── main.py       # FastAPI app
├── forecasting.py    # GBM forecasting
├── functions.py      # Simulation functions
├── mortgage_calc.py  # Mortgage calculator
└── requirements.txt
```

## Example Usage

### Buying Scenario

```python
import requests

response = requests.post('http://localhost:8000/api/v1/simulate/buying', json={
    "profile": {
        "monthly_free_income": [[10000] * 12 for _ in range(30)],
        "savings": 500000
    },
    "apartment_price": 1800000,
    "down_payment": 500000,
    "mortgage_params": {
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
    },
    "maintenance_cost_rate": 0.0,
    "fixed_maintenance_cost": 10000,
    "forecast_params": {
        "mu": 0.054,
        "sigma": 0.052
    },
    "simulation_years": 30,
    "n_sim": 10000
})

results = response.json()
print(f"Median net equity: {results['buying_results']['summary']['final_value_median']}")
```

## Development

### Run Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint
ruff check app/
```

## Docker

Build and run with Docker:

```bash
docker build -t tbontb-backend .
docker run -p 8000:8000 tbontb-backend
```
