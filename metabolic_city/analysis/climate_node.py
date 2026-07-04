"""
Isolated Climate Node - Evaluates environmental data independently
"""

from typing import Optional
from loguru import logger

from metabolic_city.utils.data_models import ClimateData, RiskScore


class ClimateNode:
    """
    Isolated AI node for evaluating climate/environmental threats.
    Blinded to traffic and demographic data.
    """
    
    def __init__(self):
        self.node_name = "climate_node"
    
    def evaluate(self, climate_data: Optional[ClimateData]) -> float:
        """
        Evaluate climate threat score (0-10)
        
        Args:
            climate_data: Climate data for a geohash
            
        Returns:
            Climate threat score from 0 to 10
        """
        if climate_data is None:
            logger.warning(f"{self.node_name}: No climate data available, returning 0")
            return 0.0
        
        try:
            score = 0.0
            
            # Factor 1: Extreme temperature (0-3 points)
            temp = climate_data.temperature_celsius
            if temp > 40:
                score += 3.0
            elif temp > 35:
                score += 2.5
            elif temp > 30:
                score += 1.5
            elif temp < -10:
                score += 3.0
            elif temp < 0:
                score += 1.0
            else:
                score += 0.0
            
            # Factor 2: Precipitation/flooding risk (0-3 points)
            precip = climate_data.precipitation_mm
            if precip > 50:
                score += 3.0
            elif precip > 30:
                score += 2.5
            elif precip > 20:
                score += 2.0
            elif precip > 10:
                score += 1.0
            else:
                score += 0.0
            
            # Factor 3: Wind hazards (0-2 points)
            wind_speed = climate_data.wind_speed_kmh
            if wind_speed > 100:
                score += 2.0
            elif wind_speed > 70:
                score += 1.5
            elif wind_speed > 50:
                score += 1.0
            else:
                score += 0.0
            
            # Factor 4: Weather warnings (0-2 points)
            warning_count = len(climate_data.weather_warnings)
            if warning_count >= 3:
                score += 2.0
            elif warning_count == 2:
                score += 1.5
            elif warning_count == 1:
                score += 1.0
            else:
                score += 0.0
            
            # Ensure score is within bounds
            score = max(0.0, min(10.0, score))
            
            logger.debug(f"{self.node_name}: Evaluated geohash {climate_data.geohash} - Score: {score:.2f}")
            return score
            
        except Exception as e:
            logger.error(f"{self.node_name}: Error evaluating climate data: {e}")
            return 0.0
    
    def evaluate_batch(self, climate_data_dict: dict) -> dict:
        """
        Evaluate climate threat scores for multiple geohashes
        
        Args:
            climate_data_dict: Dictionary mapping geohash to ClimateData
            
        Returns:
            Dictionary mapping geohash to climate score
        """
        results = {}
        for geohash, climate_data in climate_data_dict.items():
            results[geohash] = self.evaluate(climate_data)
        
        logger.info(f"{self.node_name}: Evaluated {len(results)} geohashes")
        return results
