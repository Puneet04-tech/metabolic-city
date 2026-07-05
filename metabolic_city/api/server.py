"""
FastAPI server for dashboard API endpoints
"""

import sys
import os

# Force unbuffered output for Render logs
sys.stdout = sys.stderr = __import__('io').TextIOWrapper(
    sys.stdout.buffer if hasattr(sys.stdout, 'buffer') else sys.stderr.buffer,
    encoding='utf-8',
    line_buffering=True,
    write_through=True
)

print("=" * 80, flush=True)
print("METABOLIC CITY API SERVER STARTUP", flush=True)
print("=" * 80, flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Working directory: {os.getcwd()}", flush=True)
print("=" * 80, flush=True)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from datetime import datetime
    from typing import Dict, Any, Optional
    import json
    import logging
    
    print("[✓] FastAPI imports successful", flush=True)
    
    from metabolic_city.main import MetabolicCityPipeline
    from metabolic_city.config.settings import settings
    
    print("[✓] Metabolic City imports successful", flush=True)
except Exception as e:
    print(f"[✗] IMPORT ERROR: {type(e).__name__}: {str(e)}", flush=True)
    import traceback
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)

# Set up basic logging for startup debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)
print("[✓] Logging configured", flush=True)

app = FastAPI(title="MetabolicCity API", version="1.0.0")

# CORS middleware for Next.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Render deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-loaded pipeline instance
_pipeline: Optional[MetabolicCityPipeline] = None
last_cycle_data: Dict[str, Any] = {}
last_cycle_time: Optional[datetime] = None


def get_pipeline() -> MetabolicCityPipeline:
    """Get or initialize pipeline with error handling"""
    global _pipeline
    if _pipeline is None:
        try:
            logger.info("Initializing MetabolicCity Pipeline...")
            _pipeline = MetabolicCityPipeline()
            logger.info("Pipeline initialization successful")
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Pipeline initialization error: {str(e)}")
    return _pipeline


@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on server startup with error handling"""
    try:
        logger.info("FastAPI server starting up...")
        get_pipeline()
        logger.info("Server startup complete")
    except Exception as e:
        logger.error(f"Server startup error: {str(e)}", exc_info=True)
        # Don't crash the server, just log the error
        # Pipeline will be initialized on first API call


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    logger.info("FastAPI server shutting down...")



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
    - Forecasting data
    """
    global last_cycle_data, last_cycle_time
    
    if not last_cycle_data:
        # Run a single cycle if no data exists
        try:
            last_cycle_data = await get_pipeline().run_single_cycle()
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
        "issues": []
    }
    
    # Check if gtfs_realtime_bindings is installed
    try:
        import gtfs_realtime_bindings
    except ImportError:
        system_health["issues"].append({
            "severity": "warning",
            "message": "GTFS-RT using mock data (gtfs_realtime_bindings not installed)",
            "component": "Mobility Feed"
        })
    
    # Check demographic data coverage
    total_geohashes = last_cycle_data.get('unified_data_count', 0)
    if total_geohashes > 0:
        # Check if demographic data is available for all geohashes
        # This is a simplified check - in production, would check actual coverage
        demographic_coverage = 4  # This would be calculated from actual data
        if demographic_coverage < total_geohashes:
            system_health["issues"].append({
                "severity": "info",
                "message": f"Demographic data coverage partial ({demographic_coverage}/{total_geohashes} geohashes)",
                "component": "Vulnerability Node"
            })
    
    # Forecasting data
    forecasting_data = {
        "enabled": settings.forecasting_enabled,
        "forecasts_generated": last_cycle_data.get('risk_scores_count', 0),
        "alert_forecasts": 0,  # Will be populated from actual forecasting
        "horizon_hours": settings.forecasting_horizon_hours
    }
    
    return {
        "timestamp": last_cycle_time.isoformat() if last_cycle_time else datetime.utcnow().isoformat(),
        "pipeline_results": last_cycle_data,
        "average_risk": average_risk,
        "alerts": [],  # Would be populated from actual alerts
        "recent_activity": recent_activity,
        "data_sources": data_sources,
        "system_health": system_health,
        "forecasting": forecasting_data,
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
        last_cycle_data = await get_pipeline().run_single_cycle()
        last_cycle_time = datetime.utcnow()
        return last_cycle_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.get("/api/status")
async def get_system_status():
    """Get detailed system status"""
    return get_pipeline().generate_status_report()


@app.post("/api/simulation/run")
async def run_simulation(scenario: dict):
    """
    Run a simulation scenario
    
    Args:
        scenario: Dictionary with scenario parameters
        
    Returns:
        Simulation results
    """
    try:
        from metabolic_city.utils.data_models import SimulationScenario, UnifiedDataPoint
        from metabolic_city.simulation.simulation_engine import SimulationEngine
        
        engine = SimulationEngine()
        
        # Create a simple scenario for testing
        # In production, this would come from the request body
        scenario_data = {
            "scenario_id": "test_scenario",
            "name": "Test Scenario",
            "description": "Test simulation scenario",
            "parameters": {
                "mobility": {"vehicle_count": 50},
                "climate": {"temperature": 25}
            }
        }
        
        # For now, return mock results
        return {
            "scenario_id": "test_scenario",
            "name": "Test Scenario",
            "results": {
                "baseline_composite_risk": 4.1,
                "modified_composite_risk": 4.8,
                "risk_change": 0.7,
                "risk_level_change": "increased",
                "recommendation": "LOW IMPACT: This change slightly increases risk. Monitor closely during implementation."
            },
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@app.post("/api/feedback/submit")
async def submit_feedback(feedback: dict):
    """
    Submit citizen feedback
    
    Args:
        feedback: Dictionary with feedback data
        
    Returns:
        Feedback submission result
    """
    try:
        # For now, return mock response
        return {
            "feedback_id": "fb_" + str(hash(str(feedback)))[0:8],
            "status": "submitted",
            "message": "Feedback submitted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback error: {str(e)}")


@app.post("/api/dispatch/send")
async def send_dispatch(dispatch: dict):
    """
    Send dispatch to agency
    
    Args:
        dispatch: Dictionary with dispatch data
        
    Returns:
        Dispatch result
    """
    try:
        # For now, return mock response
        return {
            "dispatch_id": "dp_" + str(hash(str(dispatch)))[0:8],
            "status": "sent",
            "agency": dispatch.get("agency", "unknown"),
            "message": "Dispatch sent successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dispatch error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "metabolic_city.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
