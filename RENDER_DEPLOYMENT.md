# MetabolicCity AI - Render Deployment Guide

This guide covers deploying MetabolicCity AI to Render.com, a cloud platform for hosting web services and static sites.

## Prerequisites

- Render account (free tier available)
- GitHub repository with your code
- Valid API keys for Gemini, Mistral, and Weather services
- GTFS-RT endpoints configured

## Quick Start

### 1. Prepare Your Repository

Ensure your repository structure includes:
- `requirements.txt` (Python dependencies)
- `dashboard/package.json` (Node.js dependencies)
- `render.yaml` (Render configuration)
- `.env.example` (Environment variables template)

### 2. Push to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin master
```

### 3. Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Review the configuration and click "Apply"

#### Option B: Manual Setup

**Backend Service:**
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: metabolic-city-backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m metabolic_city.api.server`
   - **Instance Type**: Free

**Frontend Site:**
1. Click "New +" → "Static Site"
2. Connect your GitHub repository
3. Configure:
   - **Name**: metabolic-city-frontend
   - **Build Command**: `cd dashboard && npm install && npm run build`
   - **Publish Directory**: `dashboard/out`
   - **Node Version**: 18

## Environment Variables

### Backend Environment Variables

In your Render dashboard, add these environment variables to the backend service:

**Required:**
- `GEMINI_API_KEY`: Your Gemini API key
- `MISTRAL_API_KEY`: Your Mistral API key  
- `WEATHER_API_KEY`: Your Weather API key
- `GTFS_RT_VEHICLE_POSITIONS_URL`: GTFS-RT vehicle positions endpoint
- `GTFS_RT_TRIP_UPDATES_URL`: GTFS-RT trip updates endpoint
- `GTFS_STATIC_URL`: GTFS static data URL

**Optional:**
- `PYTHONUNBUFFERED`: `1` (for better logging)
- `API_HOST`: `0.0.0.0`
- `API_PORT`: `8000`
- `PIPELINE_CYCLE_MINUTES`: `10`
- `RISK_THRESHOLD`: `7.0`
- `WEIGHT_MOBILITY`: `0.4`
- `WEIGHT_CLIMATE`: `0.3`
- `WEIGHT_VULNERABILITY`: `0.3`

### Frontend Environment Variables

Add to the frontend site:

- `NODE_ENV`: `production`
- `NEXT_PUBLIC_API_URL`: Your backend Render URL (e.g., `https://metabolic-city-backend.onrender.com`)

## Configuration Files

### render.yaml

The `render.yaml` file defines both services:

```yaml
services:
  - type: web
    name: metabolic-city-backend
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python -m metabolic_city.api.server
    envVars:
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: API_HOST
        value: "0.0.0.0"
      - key: API_PORT
        value: "8000"
      # API keys marked as sync: false for manual entry
      - key: GEMINI_API_KEY
        sync: false
      # ... other keys
    healthCheckPath: /api/health

sites:
  - type: web
    name: metabolic-city-frontend
    runtime: node
    buildCommand: cd dashboard && npm install && npm run build
    publishPath: dashboard/out
    envVars:
      - key: NODE_ENV
        value: "production"
      - key: NEXT_PUBLIC_API_URL
        value: https://metabolic-city-backend.onrender.com
```

### next.config.js

Updated for static export:

```javascript
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
}
```

## Deployment Process

### Automatic Deployment

Render automatically deploys when you push to your connected GitHub branch. The process:

1. **Backend**: 
   - Installs Python dependencies
   - Starts FastAPI server
   - Health check at `/api/health`

2. **Frontend**:
   - Installs Node.js dependencies
   - Builds Next.js app as static site
   - Deploys to CDN

### Manual Deployment

Trigger a manual deploy from the Render dashboard:
1. Go to your service
2. Click "Manual Deploy" → "Deploy latest commit"

## Accessing Your Application

After deployment:

- **Backend URL**: `https://metabolic-city-backend.onrender.com`
- **Frontend URL**: `https://metabolic-city-frontend.onrender.com`
- **API Docs**: `https://metabolic-city-backend.onrender.com/docs`

## Monitoring

### Logs

View logs in the Render dashboard:
- Go to your service
- Click "Logs" tab
- Filter by: All, Server, Build

### Health Checks

The backend includes a health check endpoint:
- Render automatically checks `/api/health`
- If health check fails, Render restarts the service

### Metrics

Render provides:
- CPU usage
- Memory usage
- Response times
- Error rates

## Troubleshooting

### Backend won't start

**Check logs for:**
- Missing dependencies → Update `requirements.txt`
- Environment variables → Verify all required keys are set
- Port conflicts → Ensure `API_PORT` is set to `8000`

**Common issues:**
- `ModuleNotFoundError`: Add missing package to `requirements.txt`
- `ImportError`: Check Python version compatibility
- Database errors: Ensure data directory exists

### Frontend build fails

**Check logs for:**
- Node.js version mismatch → Set correct Node version in Render
- Missing dependencies → Update `package.json`
- Build errors → Check Next.js configuration

**Common issues:**
- `npm install` fails: Clear cache and retry
- Build timeout: Optimize build process
- Static export errors: Verify `output: 'export'` in config

### CORS errors

If frontend can't connect to backend:
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend CORS configuration (set to allow all origins)
- Ensure backend is running and accessible

### API keys not working

- Verify keys are correctly set in Render environment variables
- Check keys are not expired or invalid
- Ensure API endpoints are accessible from Render's network

## Scaling

### Free Tier Limitations

- **Backend**: 512MB RAM, 0.1 CPU
- **Frontend**: Unlimited bandwidth
- **Sleeps**: Free services sleep after 15min inactivity
- **Cold starts**: 30-60s wake-up time

### Paid Plans

Upgrade to paid plans for:
- No sleep time
- More CPU/RAM
- Faster cold starts
- Better performance

## Custom Domain

### Setup

1. Go to your service in Render
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### SSL

Render automatically provides SSL certificates for all domains.

## Database

### Using Render PostgreSQL

For production, consider using Render PostgreSQL:

1. Create PostgreSQL instance in Render
2. Update `DATABASE_URL` environment variable
3. Modify code to use PostgreSQL instead of SQLite

### Current Setup

Currently uses SQLite with local file storage. For production:
- Migrate to PostgreSQL
- Use Render Disk for persistent storage
- Implement proper backup strategy

## Security Best Practices

1. **Never commit `.env` files** to Git
2. **Use Render environment variables** for sensitive data
3. **Enable HTTPS** (automatic on Render)
4. **Rotate API keys** regularly
5. **Monitor logs** for suspicious activity
6. **Use private Git repositories** for production

## Performance Optimization

1. **Enable caching** for API responses
2. **Use CDN** (automatic for static sites)
3. **Optimize images** (already configured with `unoptimized: true`)
4. **Minimize bundle size** for frontend
5. **Use paid plans** for better performance

## Backup and Recovery

### Code Backup

- Code is stored in GitHub
- Use Git branches for version control
- Tag releases for easy rollback

### Data Backup

For SQLite data:
- Regularly export database
- Store backups externally
- Consider migrating to PostgreSQL for production

### Recovery

- Rollback to previous Git commit
- Restore database from backup
- Redeploy from Render dashboard

## Support

For deployment issues:
1. Check Render logs
2. Review Render documentation: https://render.com/docs
3. Check this guide's troubleshooting section
4. Verify environment variables are set correctly
5. Ensure all dependencies are listed

## Cost

### Free Tier

- **Backend**: Free (with sleep)
- **Frontend**: Free
- **Total**: $0/month

### Paid Plans

- **Starter**: $7/month (no sleep, better performance)
- **Standard**: $25/month (more resources)
- **Pro**: Custom pricing

## Next Steps

1. Deploy using `render.yaml` or manual setup
2. Configure environment variables
3. Test backend health check
4. Verify frontend connects to backend
5. Set up custom domain (optional)
6. Configure monitoring and alerts
7. Implement backup strategy
