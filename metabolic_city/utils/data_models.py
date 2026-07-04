"""
Data models for MetabolicCity AI
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class MobilityStatus(str, Enum):
    """Transit system status"""
    NORMAL = "normal"
    DELAYED = "delayed"
    SEVERELY_DELAYED = "severely_delayed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class ClimateStatus(str, Enum):
    """Weather condition status"""
    NORMAL = "normal"
    ADVISORY = "advisory"
    WARNING = "warning"
    EMERGENCY = "emergency"


class MobilityData(BaseModel):
    """Mobility/transit data model"""
    geohash: str
    timestamp: datetime
    vehicle_count: int = Field(default=0, description="Number of vehicles in area")
    average_delay_minutes: float = Field(default=0.0, description="Average delay in minutes")
    cancelled_routes: int = Field(default=0, description="Number of cancelled routes")
    status: MobilityStatus = Field(default=MobilityStatus.NORMAL)
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw GTFS-RT data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClimateData(BaseModel):
    """Climate/weather data model"""
    geohash: str
    timestamp: datetime
    temperature_celsius: float = Field(default=0.0, description="Temperature in Celsius")
    humidity_percent: float = Field(default=0.0, description="Humidity percentage")
    pressure_hpa: float = Field(default=0.0, description="Barometric pressure in hPa")
    precipitation_mm: float = Field(default=0.0, description="Precipitation in mm")
    wind_speed_kmh: float = Field(default=0.0, description="Wind speed in km/h")
    status: ClimateStatus = Field(default=ClimateStatus.NORMAL)
    weather_warnings: List[str] = Field(default_factory=list, description="Active weather warnings")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw weather API data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DemographicData(BaseModel):
    """Socio-demographic baseline data model"""
    geohash: str
    timestamp: datetime
    population_density: float = Field(default=0.0, description="Population per square km")
    vehicle_ownership_rate: float = Field(default=0.0, description="Percentage of households with vehicles")
    elderly_dependency_ratio: float = Field(default=0.0, description="Ratio of elderly to working-age population")
    youth_dependency_ratio: float = Field(default=0.0, description="Ratio of youth to working-age population")
    financial_stress_index: float = Field(default=0.0, description="Financial stress index (0-10)")
    language_access_barrier: float = Field(default=0.0, description="Language access barrier score (0-10)")
    disability_access_needs: float = Field(default=0.0, description="Disability access needs score (0-10)")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw census data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UnifiedDataPoint(BaseModel):
    """Unified data point combining all domains"""
    geohash: str
    timestamp: datetime
    mobility: Optional[MobilityData] = None
    climate: Optional[ClimateData] = None
    demographic: Optional[DemographicData] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RiskScore(BaseModel):
    """Risk score output from analysis nodes"""
    geohash: str
    timestamp: datetime
    mobility_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Mobility threat score (0-10)")
    climate_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Climate threat score (0-10)")
    vulnerability_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Vulnerability score (0-10)")
    composite_risk_index: float = Field(default=0.0, ge=0.0, le=10.0, description="Composite risk index (0-10)")
    risk_level: str = Field(default="low", description="Risk level: low, medium, high, critical")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmergencyType(str, Enum):
    """Types of compound urban emergencies"""
    COMPOUND_THERMAL_STRANDING = "compound_thermal_stranding"
    COMPOUND_TRANSIT_ISOLATION = "compound_transit_isolation"
    COMPOUND_FLOOD_EVACUATION = "compound_flood_evacuation"
    COMPOUND_INFRASTRUCTURE_FAILURE = "compound_infrastructure_failure"
    COMPOUND_PUBLIC_HEALTH = "compound_public_health"


class ResponsePlan(BaseModel):
    """Structured response plan"""
    emergency_type: EmergencyType
    geohash: str
    timestamp: datetime
    risk_score: RiskScore
    dispatch_zone: str = Field(description="High-priority dispatch zone")
    staging_area: str = Field(description="Ideal location for relief staging area")
    equipment_checklist: List[str] = Field(description="Required equipment and supplies")
    personnel_requirements: Dict[str, int] = Field(description="Personnel needed by type")
    estimated_duration_hours: int = Field(description="Estimated operation duration in hours")
    priority_level: str = Field(default="medium", description="Priority: low, medium, high, critical")
    raw_plan_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw structured plan data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CitizenReport(BaseModel):
    """Citizen feedback report model"""
    report_id: str
    geohash: str
    timestamp: datetime
    report_type: str = Field(description="Type of issue reported")
    description: str = Field(description="Report description")
    urgency: str = Field(default="medium", description="Urgency level: low, medium, high")
    contact_info: Optional[str] = Field(default=None, description="Optional contact information")
    status: str = Field(default="pending", description="Processing status")
    duplicate_of: Optional[str] = Field(default=None, description="ID of duplicate report if any")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SimulationScenario(BaseModel):
    """Simulation scenario for what-if analysis"""
    scenario_id: str
    name: str
    description: str
    timestamp: datetime
    parameters: Dict[str, Any] = Field(description="Simulation parameters")
    baseline_data: UnifiedDataPoint = Field(description="Baseline data for comparison")
    modified_data: UnifiedDataPoint = Field(description="Modified data with changes applied")
    results: Optional[Dict[str, Any]] = Field(default=None, description="Simulation results")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
