# Getting Started with TBONTB

This guide will help you get the TBONTB web application up and running quickly.

## Quick Start

### Using Docker (Easiest)

1. **Start the application:**
   ```bash
   docker-compose up
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

That's it! Both services will start automatically.

## Manual Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Verify it's running:**
   - Visit http://localhost:8000/docs
   - You should see the Swagger UI documentation

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.local.example .env.local
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Verify it's running:**
   - Visit http://localhost:3000
   - You should see the TBONTB home page

## Testing the Application

### Test the Backend API

1. **Health check:**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Get default parameters:**
   ```bash
   curl http://localhost:8000/api/v1/parameters/defaults
   ```

3. **Test a simple simulation:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/simulate/investment \
     -H "Content-Type: application/json" \
     -d '{
       "profile": {
         "monthly_free_income": [[10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000]],
         "savings": 100000
       },
       "tax_rate": 25,
       "transaction_fee": 0,
       "percentage_management_fee": 0,
       "ILS_management_fee": 0,
       "initial_already_invested": true,
       "forecast_params": {
         "mu": 0.07,
         "sigma": 0.15
       },
       "simulation_years": 1,
       "n_sim": 100
     }'
   ```

### Test the Frontend

1. Visit http://localhost:3000
2. Click "Start Your Simulation"
3. The page should be ready (forms will be added in next phase)

## Next Steps

### Phase 1: Complete MVP (Next Tasks)

Now that the infrastructure is set up, here's what comes next:

1. **Create form components** (Week 3-4):
   - Financial profile form
   - Buying scenario form with mortgage builder
   - Investment scenario form
   - Form validation with Zod

2. **Build results dashboard** (Week 5):
   - Results page with summary cards
   - Detailed breakdown tables
   - Comparison view

3. **Integrate charts** (Week 5-6):
   - Implement Plotly.js heatmap charts
   - Percentile line charts
   - Interactive comparison charts

4. **Add features** (Week 6):
   - Export to CSV/JSON
   - Save/load scenarios
   - Mobile responsive design

### Development Workflow

1. **Backend changes:**
   - Edit files in `backend/app/`
   - FastAPI will auto-reload
   - Test at http://localhost:8000/docs

2. **Frontend changes:**
   - Edit files in `frontend/`
   - Next.js will auto-reload
   - View at http://localhost:3000

3. **Adding new API endpoints:**
   - Add route in `backend/app/api/routes.py`
   - Add types in `backend/app/models/`
   - Test in Swagger UI
   - Update frontend types in `frontend/types/index.ts`
   - Use in frontend via `frontend/lib/api.ts`

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

**Module not found errors:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**CORS errors:**
- Check `backend/app/core/config.py` has your frontend URL in `ALLOWED_ORIGINS`

### Frontend Issues

**Port 3000 already in use:**
```bash
# Kill the process
lsof -ti:3000 | xargs kill -9
```

**Module not found:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
- Verify backend is running at http://localhost:8000
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Check browser console for CORS errors

### Docker Issues

**Containers won't start:**
```bash
# Stop all containers
docker-compose down

# Rebuild
docker-compose up --build
```

**Can't connect to backend from frontend:**
- Make sure both services are in `docker-compose up`
- Check network configuration in `docker-compose.yml`

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs
- **Plotly.js Documentation**: https://plotly.com/javascript/
- **TailwindCSS Documentation**: https://tailwindcss.com/docs

## Support

If you encounter issues:
1. Check this guide
2. Review the API documentation at http://localhost:8000/docs
3. Check the browser console for errors
4. Review backend logs in terminal
