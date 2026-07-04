"""
FastAPI server for dashboard API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any
import json

from metabolic_city.main import MetabolicCityPipeline
from metabolic_city.config.settings import settings

app = FastAPI(title="MetabolicCity API", version="1.0.0")

# CORS middleware for Next.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline = MetabolicCityPipeline()
last_cycle_data: Dict[str, Any] = {}
last_cycle_time: datetime = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MetabolicCity API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pipeline_enabled": settings.pipeline_enabled,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/dashboard")
async def get_dashboard_data():
    """
    Get dashboard data from last pipeline cycle
    
    Returns comprehensive data for the dashboard including:
    - Pipeline statistics
    - Risk scores
    - Alerts
    - System status
    - Recent activity
    - Data source status
    """
    global last_cycle_data, last_cycle_time
    
    if not last_cycle_data:
        # Run a single cycle if no data exists
        try:
            last_cycle_data = await pipeline.run_single_cycle()
            last_cycle_time = datetime.utcnow()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    
    # Calculate average risk if we have risk scores
    average_risk = None
    if last_cycle_data.get("risk_scores_count", 0) > 0:
        # Mock average risk calculation - in production, calculate from actual scores
        average_risk = 4.1
    
    # Generate recent activity based on pipeline results
    recent_activity = [
        {
            "type": "success",
            "message": f"Processed {last_cycle_data.get('unified_data_count', 0)} locations",
            "timestamp": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat()
        },
        {
            "type": "success",
            "message": f"Generated {last_cycle_data.get('risk_scores_count', 0)} risk scores",
            "timestamp": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat()
        },
        {
            "type": "info",
            "message": f"Cycle completed in {last_cycle_data.get('duration_seconds', 0):.2f}s",
            "timestamp": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat()
        },
        {
            "type": "warning",
            "message": f"{last_cycle_data.get('alerts_generated', 0)} alerts triggered",
            "timestamp": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat()
        }
    ]
    
    # Data source status
    data_sources = [
        {
            "name": "GTFS-RT Transit",
            "status": "active",
            "last_fetch": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat(),
            "records": last_cycle_data.get('unified_data_count', 0)
        },
        {
            "name": "Weather API",
            "status": "active",
            "last_fetch": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat(),
            "records": last_cycle_data.get('unified_data_count', 0)
        },
        {
            "name": "Demographic Data",
            "status": "partial",
            "last_fetch": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat(),
            "records": 4  # Vulnerability node evaluated 4 geohashes
        }
    ]
    
    # System health
    system_health = {
        "overall": "healthy",
        "issues": [
            {
                "severity": "warning",
                "message": "GTFS-RT using mock data (gtfs_realtime_bindings not installed)",
                "component": "Mobility Feed"
            },
            {
                "severity": "info",
                "message": "Demographic data coverage partial (4/49 geohashes)",
                "component": "Vulnerability Node"
            }
        ]
    }
    
    return {
        "timestamp": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat(),
        "pipeline_results": last_cycle_data,
        "average_risk": average_risk,
        "alerts": [],  # Would be populated from actual alerts
        "recent_activity": recent_activity,
        "data_sources": data_sources,
        "system_health": system_health,
        "system_status": {
            "pipeline_enabled": settings.pipeline_enabled,
            "forecasting_enabled": settings.forecasting_enabled,
            "simulation_enabled": settings.simulation_enabled,
            "feedback_enabled": settings.feedback_enabled,
            "dispatch_enabled": settings.dispatch_enabled,
        }
    }


@app.post("/api/pipeline/run")
async def run_pipeline_cycle():
    """
    Manually trigger a pipeline cycle
    
    Returns the results of the pipeline execution
    """
    global last_cycle_data, last_cycle_time
    
    try:
        last_cycle_data = await pipeline.run_single_cycle()
        last_cycle_time = datetime.utcnow()
        return last_cycle_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.get("/api/status")
async def get_system_status():
    """Get detailed system status"""
    return pipeline.generate_status_report()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "metabolic_city.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
