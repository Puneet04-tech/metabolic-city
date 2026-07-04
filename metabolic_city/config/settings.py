"""
Application settings using Pydantic for validation
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration"""
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    weather_api_key: Optional[str] = Field(None, env="WEATHER_API_KEY")
    
    # GTFS-RT Endpoints
    gtfs_rt_vehicle_positions_url: Optional[str] = Field(None, env="GTFS_RT_VEHICLE_POSITIONS_URL")
    gtfs_rt_trip_updates_url: Optional[str] = Field(None, env="GTFS_RT_TRIP_UPDATES_URL")
    gtfs_static_url: Optional[str] = Field(None, env="GTFS_STATIC_URL")
    
    # Weather API Configuration
    weather_api_provider: str = Field("openweathermap", env="WEATHER_API_PROVIDER")
    weather_api_base_url: str = Field("https://api.openweathermap.org/data/2.5", env="WEATHER_API_BASE_URL")
    
    # Database Configuration
    database_url: str = Field("sqlite:///metabolic_city/data/metabolic_city.db", env="DATABASE_URL")
    database_pool_size: int = Field(5, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(10, env="DATABASE_MAX_OVERFLOW")
    
    # Pipeline Settings
    pipeline_cycle_minutes: int = Field(10, env="PIPELINE_CYCLE_MINUTES")
    pipeline_enabled: bool = Field(True, env="PIPELINE_ENABLED")
    risk_threshold: float = Field(7.0, env="RISK_THRESHOLD")
    
    # Domain Weights (must sum to 1.0)
    weight_mobility: float = Field(0.4, env="WEIGHT_MOBILITY")
    weight_climate: float = Field(0.3, env="WEIGHT_CLIMATE")
    weight_vulnerability: float = Field(0.3, env="WEIGHT_VULNERABILITY")
    
    # Geohash Configuration
    geohash_precision: int = Field(6, env="GEOHASH_PRECISION")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/metabolic_city.log", env="LOG_FILE")
    
    # API Server
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_reload: bool = Field(True, env="API_RELOAD")
    
    # Forecasting Settings
    forecasting_horizon_hours: int = Field(24, env="FORECASTING_HORIZON_HOURS")
    forecasting_enabled: bool = Field(True, env="FORECASTING_ENABLED")
    
    # Simulation Settings
    simulation_enabled: bool = Field(True, env="SIMULATION_ENABLED")
    
    # Feedback Integration
    feedback_enabled: bool = Field(True, env="FEEDBACK_ENABLED")
    feedback_api_endpoint: Optional[str] = Field(None, env="FEEDBACK_API_ENDPOINT")
    
    # Dispatch Settings
    dispatch_enabled: bool = Field(True, env="DISPATCH_ENABLED")
    dispatch_transit_system: Optional[str] = Field(None, env="DISPATCH_TRANSIT_SYSTEM")
    dispatch_public_works: Optional[str] = Field(None, env="DISPATCH_PUBLIC_WORKS")
    dispatch_emergency_services: Optional[str] = Field(None, env="DISPATCH_EMERGENCY_SERVICES")
    
    @validator("weight_mobility", "weight_climate", "weight_vulnerability")
    def validate_weights(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Weights must be between 0 and 1")
        return v
    
    @validator("risk_threshold")
    def validate_risk_threshold(cls, v):
        if not 0 <= v <= 10:
            raise ValueError("Risk threshold must be between 0 and 10")
        return v
    
    @property
    def total_weight(self) -> float:
        """Check if weights sum to 1.0"""
        return self.weight_mobility + self.weight_climate + self.weight_vulnerability
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
