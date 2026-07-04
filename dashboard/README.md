# MetabolicCity Dashboard

A modern Next.js dashboard for visualizing MetabolicCity AI pipeline results in real-time.

## Features

- **Real-time Dashboard**: Live monitoring of pipeline status and results
- **Interactive Visualizations**: Risk maps, trend charts, and alert displays
- **Export Functionality**: Download dashboard data as JSON
- **Modern UI**: Built with Next.js 14, TypeScript, and Tailwind CSS
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Node.js 18+ installed
- MetabolicCity AI backend running (with FastAPI server)

## Installation

1. Navigate to the dashboard directory:
```bash
cd dashboard
```

2. Install dependencies:
```bash
npm install
```

## Running the Dashboard

### Development Mode

Start the development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Production Build

Build for production:
```bash
npm run build
npm start
```

## Backend Setup

The dashboard requires the MetabolicCity AI backend to be running with the FastAPI server.

### Start the Backend API

From the project root:
```bash
# Activate virtual environment
./venv/Scripts/activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Start the FastAPI server
python -m metabolic_city.api.server
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `GET /api/dashboard` - Get dashboard data
- `POST /api/pipeline/run` - Trigger pipeline cycle
- `GET /api/status` - Get system status
- `GET /api/health` - Health check

## Dashboard Components

### Dashboard Stats
- Displays key metrics: locations monitored, risk scores, active alerts, cycle duration

### Risk Map
- Visualizes risk distribution across geohashes
- Shows risk levels (Low, Medium, High, Critical)
- Displays percentage distribution

### Trend Chart
- Shows risk trends over time
- Interactive line chart using Recharts

### Alerts List
- Displays active alerts with details
- Shows alert type, message, and timestamp
- Empty state when no alerts

## Export Functionality

Click the "Export" button to download current dashboard data as JSON. The export includes:
- Timestamp
- Pipeline results
- System status
- Risk scores
- Alerts

## Configuration

### API URL

The dashboard connects to the backend API at `http://localhost:8000`. To change this, edit `src/app/page.tsx`:

```typescript
const response = await fetch('http://localhost:8000/api/dashboard')
```

### Refresh Interval

The dashboard auto-refreshes every 60 seconds. To change this, edit `src/app/page.tsx`:

```typescript
const interval = setInterval(fetchData, 60000) // Change 60000 to desired milliseconds
```

## Troubleshooting

### Dashboard shows "No Data Available"

1. Ensure the FastAPI backend is running
2. Check that the backend is accessible at `http://localhost:8000`
3. Try manually triggering a pipeline cycle via the API

### CORS Errors

The backend includes CORS middleware for `localhost:3000`. If you're running on a different port, update the CORS configuration in `metabolic_city/api/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://your-port:3000"],
    ...
)
```

### Build Errors

If you encounter TypeScript errors during build:
```bash
npm run build
```

The errors are expected during development and will resolve once dependencies are properly installed.

## Development

### Project Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── components/
│       ├── DashboardStats.tsx
│       ├── RiskMap.tsx
│       ├── AlertsList.tsx
│       └── TrendChart.tsx
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

### Adding New Components

1. Create component in `src/components/`
2. Import and use in `src/app/page.tsx`
3. Follow existing component patterns

## Technologies Used

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Charting library
- **Lucide React**: Icon library
- **FastAPI**: Backend API (Python)

## License

Same as parent MetabolicCity AI project.
