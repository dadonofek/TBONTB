# Deployment Guide

This guide covers multiple ways to deploy the TBONTB application so others can use it.

## Table of Contents
- [Quick Start with Docker](#quick-start-with-docker)
- [Free Cloud Hosting](#free-cloud-hosting)
- [VPS Deployment](#vps-deployment)
- [Environment Variables](#environment-variables)

---

## Quick Start with Docker

The easiest way for your friend to run the application is using Docker.

### Prerequisites
- Docker and Docker Compose installed
- Git installed

### Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd TBONTB
```

2. **Run the production build**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

4. **Stop the application**
```bash
docker-compose -f docker-compose.prod.yml down
```

---

## Free Cloud Hosting

Deploy the frontend and backend separately on free hosting platforms.

### Frontend Deployment (Vercel)

Vercel offers free hosting for Next.js applications.

1. **Push your code to GitHub**
```bash
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Click "New Project"
   - Import your repository
   - Configure:
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `.next`
   - Add Environment Variable:
     - `NEXT_PUBLIC_API_URL`: Your backend URL (see below)
   - Click "Deploy"

3. **Note your frontend URL** (e.g., `https://your-app.vercel.app`)

### Backend Deployment (Render)

Render offers free hosting for backend services (with limitations: spins down after 15 min inactivity).

1. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - Name: `tbontb-backend`
     - Root Directory: `backend`
     - Runtime: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

2. **Note your backend URL** (e.g., `https://tbontb-backend.onrender.com`)

3. **Update Frontend Environment Variable**
   - Go back to Vercel
   - Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` to your Render backend URL
   - Redeploy the frontend

### Alternative: Railway

Railway is another free option (similar to Render):

**Backend on Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Deploy
railway up
```

**Get your backend URL** from Railway dashboard and update Vercel environment variables.

---

## VPS Deployment

Deploy the entire stack to a VPS (DigitalOcean, AWS, Google Cloud, etc.)

### Prerequisites
- Ubuntu 20.04+ server
- Domain name (optional)
- SSH access

### Setup Steps

1. **SSH into your server**
```bash
ssh user@your-server-ip
```

2. **Install Docker and Docker Compose**
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

3. **Clone the repository**
```bash
git clone <your-repo-url>
cd TBONTB
```

4. **Configure environment variables**
```bash
# Backend (if needed)
cp backend/.env.example backend/.env

# Frontend
echo "NEXT_PUBLIC_API_URL=http://your-server-ip:8000" > frontend/.env.local
```

5. **Deploy with Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

6. **Configure firewall**
```bash
sudo ufw allow 3000
sudo ufw allow 8000
sudo ufw enable
```

7. **Access the application**
- Frontend: http://your-server-ip:3000
- Backend: http://your-server-ip:8000

### Optional: Setup NGINX reverse proxy

For production, you should use NGINX with SSL:

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

Create NGINX config (`/etc/nginx/sites-available/tbontb`):
```nginx
server {
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and get SSL:
```bash
sudo ln -s /etc/nginx/sites-available/tbontb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d your-domain.com
```

---

## Environment Variables

### Backend (.env)
```env
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000","https://your-frontend-url.vercel.app"]
DEFAULT_SIMULATION_YEARS=30
DEFAULT_N_SIMULATIONS=10000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# For production:
# NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

---

## Recommended Approach for Your Friend

**For non-technical users:**
Use **Option 1: Docker** - They just need to install Docker and run one command.

**For public access:**
Use **Free Cloud Hosting** (Vercel + Render) - No server maintenance required.

**For full control:**
Use **VPS Deployment** - More configuration but complete control.

---

## Troubleshooting

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend is running: `curl http://localhost:8000/docs`
- Check CORS settings in backend

### Docker build fails
- Ensure Docker has enough memory (4GB+ recommended)
- Try: `docker system prune -a` to clean up

### Port conflicts
Change ports in docker-compose.prod.yml:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

---

## Keeping Your Deployment Updated

When you make changes:

**Docker:**
```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

**Vercel:** Automatically deploys on git push to main branch

**Render:** Automatically deploys on git push to main branch

**VPS:**
```bash
git pull
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```
