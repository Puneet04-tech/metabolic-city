"""
Trend Forecaster - Predictive analysis using historical data
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from metabolic_city.forecasting.memory_matrix import MemoryMatrix
from metabolic_city.config.settings import settings


class TrendForecaster:
    """
    Evaluates historical logs to build Predictive Trend Matrix.
    Flags areas likely to cross risk thresholds up to 24 hours in advance.
    """
    
    def __init__(self):
        self.memory_matrix = MemoryMatrix()
        self.forecasting_horizon = settings.forecasting_horizon_hours
        self.enabled = settings.forecasting_enabled
        
        if not self.enabled:
            logger.warning("Trend forecasting is disabled in settings")
    
    def forecast_risk(self, geohash: str) -> Optional[Dict]:
        """
        Forecast risk for a specific geohash
        
        Args:
            geohash: Geohash string
            
        Returns:
            Dictionary with forecast data or None if insufficient data
        """
        if not self.enabled:
            return None
        
        # Get historical data
        history = self.memory_matrix.get_history(geohash, hours=48)
        
        if len(history) < 10:
            logger.debug(f"Insufficient historical data for {geohash}")
            return None
        
        # Calculate trend
        trend = self.memory_matrix.get_trend(geohash, hours=24)
        
        # Simple linear extrapolation
        recent_scores = [r["composite_risk_index"] for r in history[-10:]]
        avg_rate_of_change = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
        
        # Project forward
        projected_score = recent_scores[-1] + (avg_rate_of_change * (self.forecasting_horizon / 2))
        projected_score = max(0.0, min(10.0, projected_score))
        
        # Check if likely to cross threshold
        from metabolic_city.config.settings import settings
        threshold = settings.risk_threshold
        will_cross_threshold = projected_score >= threshold
        
        forecast = {
            "geohash": geohash,
            "forecast_timestamp": (datetime.utcnow() + timedelta(hours=self.forecasting_horizon)).isoformat(),
            "current_score": recent_scores[-1],
            "projected_score": projected_score,
            "trend": trend["trend"],
            "rate_of_change": avg_rate_of_change,
            "will_cross_threshold": will_cross_threshold,
            "confidence": self._calculate_confidence(history),
            "horizon_hours": self.forecasting_horizon
        }
        
        logger.debug(f"Forecast for {geohash}: {forecast['projected_score']:.2f} (trend: {trend['trend']})")
        return forecast
    
    def _calculate_confidence(self, history: List[Dict]) -> float:
        """
        Calculate confidence score based on data quality
        
        Args:
            history: List of historical records
            
        Returns:
            Confidence score (0-1)
        """
        if len(history) < 10:
            return 0.0
        
        # More data points = higher confidence
        data_points_score = min(1.0, len(history) / 50)
        
        # Lower variance = higher confidence
        scores = [r["composite_risk_index"] for r in history]
        variance = sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores)
        variance_score = max(0.0, 1.0 - (variance / 10))
        
        # Combined confidence
        confidence = (data_points_score * 0.6) + (variance_score * 0.4)
        
        return round(confidence, 2)
    
    def forecast_batch(self, geohashes: List[str]) -> Dict[str, Dict]:
        """
        Forecast risk for multiple geohashes
        
        Args:
            geohashes: List of geohash strings
            
        Returns:
            Dictionary mapping geohash to forecast data
        """
        if not self.enabled:
            return {}
        
        forecasts = {}
        
        for geohash in geohashes:
            forecast = self.forecast_risk(geohash)
            if forecast:
                forecasts[geohash] = forecast
        
        logger.info(f"Generated forecasts for {len(forecasts)} geohashes")
        return forecasts
    
    def get_alert_forecasts(self, geohashes: List[str]) -> List[Dict]:
        """
        Get forecasts for geohashes likely to cross threshold
        
        Args:
            geohashes: List of geohash strings
            
        Returns:
            List of forecasts that will cross threshold
        """
        forecasts = self.forecast_batch(geohashes)
        
        alerts = [
            forecast for forecast in forecasts.values()
            if forecast.get("will_cross_threshold", False)
        ]
        
        logger.info(f"Found {len(alerts)} geohashes likely to cross threshold")
        return alerts
    
    def generate_forecast_summary(self, forecasts: Dict[str, Dict]) -> str:
        """
        Generate natural-language summary of forecasts
        
        Args:
            forecasts: Dictionary mapping geohash to forecast data
            
        Returns:
            Summary string
        """
        if not forecasts:
            return "No forecasts available."
        
        total = len(forecasts)
        alerts = sum(1 for f in forecasts.values() if f.get("will_cross_threshold", False))
        increasing = sum(1 for f in forecasts.values() if f.get("trend") == "increasing")
        
        summary = f"""
FORECASTING SUMMARY
===================

Total Forecasts: {total}
Projected to Cross Threshold: {alerts}
Increasing Trend: {increasing}
Stable/Decreasing: {total - increasing}

ALERT LOCATIONS (Next {self.forecasting_horizon} hours)
--------------------------------------------------
"""
        
        for geohash, forecast in forecasts.items():
            if forecast.get("will_cross_threshold", False):
                summary += f"\n{geohash}: {forecast['projected_score']:.2f} (confidence: {forecast['confidence']:.2f})"
        
        return summary.strip()
