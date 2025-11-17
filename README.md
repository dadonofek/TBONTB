# TBONTB - To Buy Or Not To Buy

A comprehensive financial simulation tool that helps you make informed decisions when comparing buying real estate vs. investing in the stock market.

## Features

- **Monte Carlo Simulations**: Run 10,000+ simulations to model uncertainty and risk
- **Buying Scenario**: Simulate apartment purchase with multi-track mortgages, property appreciation, and maintenance costs
- **Investment Scenario**: Model investment portfolios with fees, taxes, and market volatility
- **Advanced Mortgage Calculator**: Support for fixed, prime, CPI-linked, and adjustable mortgages
- **Interactive Visualizations**: Probability distributions, percentile analysis, and comparative charts
- **Export Results**: Download simulation results as JSON or CSV

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **NumPy** - Numerical computing
- **Plotly** - Data visualization
- **Pydantic** - Data validation

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS** - Utility-first CSS
- **Plotly.js** - Interactive charts
- **React Hook Form** - Form management
- **Tanstack Query** - Data fetching and caching

## Project Structure

```
TBONTB/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Pydantic models
│   │   ├── services/    # Business logic
│   │   ├── core/        # Configuration
│   │   └── main.py      # FastAPI app
│   ├── forecasting.py   # GBM forecasting
│   ├── functions.py     # Simulation functions
│   ├── mortgage_calc.py # Mortgage calculator
│   └── requirements.txt
│
├── frontend/            # Next.js application
│   ├── app/            # App router pages
│   ├── components/     # React components
│   ├── lib/            # Utilities
│   ├── types/          # TypeScript types
│   └── package.json
│
└── docker-compose.yml  # Docker configuration
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd TBONTB

# Start both services
docker-compose up
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local

# Run development server
npm run dev
```

## Usage

### 1. Define Your Financial Profile

- Monthly free income
- Current savings

### 2. Configure Scenarios

**Buying Scenario:**
- Apartment price
- Down payment
- Mortgage configuration (multi-track support)
- Maintenance costs
- Property appreciation parameters

**Investment Scenario:**
- Tax rate
- Transaction fees
- Management fees
- Expected returns and volatility

### 3. Run Simulation

Execute Monte Carlo simulations with customizable parameters:
- Simulation duration (1-50 years)
- Number of simulations (100-50,000)

### 4. Analyze Results

View comprehensive results including:
- Net equity projections
- Probability distributions
- Percentile analysis (10th, 50th, 90th)
- Annualized returns
- Interactive heatmaps

## API Documentation

Once the backend is running, visit:
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/simulate/buying` - Run buying scenario
- `POST /api/v1/simulate/investment` - Run investment scenario
- `POST /api/v1/simulate/compare` - Compare multiple scenarios
- `GET /api/v1/parameters/defaults` - Get default parameters
- `POST /api/v1/mortgage/preview` - Preview mortgage payments

## Development

### Backend

```bash
cd backend

# Run tests
pytest

# Format code
black app/

# Lint
ruff check app/
```

### Frontend

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Run production server
npm start

# Lint
npm run lint
```

## Deployment

### Backend Deployment (Railway/Render)

1. Connect your repository
2. Set environment variables
3. Deploy from `backend/` directory

### Frontend Deployment (Vercel)

```bash
cd frontend
vercel
```

Update `NEXT_PUBLIC_API_URL` to point to your production backend.

## Configuration

### Backend (.env)

```env
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000"]
DEFAULT_SIMULATION_YEARS=30
DEFAULT_N_SIMULATIONS=10000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Monte Carlo simulation methodology based on Geometric Brownian Motion
- Mortgage calculations support Israeli market standards
- Historical data parameters from market research

## TODOs

- Rewrite the simulate_buying_scenario
- Integrate mortgage calc
- Evaluate params for CPI and "ogen" for Adjustable mortgage
- Validate mortgage_calc using the "משכנתאמן" calculator
- Account for rent increase and income increase
- Save data of S&P 500 and don't download it every time
- Save data of CPI from הלשכה המרכזית לסטטיסטיקה

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the examples in the frontend code
