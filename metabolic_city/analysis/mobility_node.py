"""
Isolated Mobility Node - Evaluates transit data independently
"""

from typing import Optional
from loguru import logger

from metabolic_city.utils.data_models import MobilityData, RiskScore


class MobilityNode:
    """
    Isolated AI node for evaluating mobility/transit threats.
    Blinded to weather and demographic data.
    """
    
    def __init__(self):
        self.node_name = "mobility_node"
    
    def evaluate(self, mobility_data: Optional[MobilityData]) -> float:
        """
        Evaluate mobility threat score (0-10)
        
        Args:
            mobility_data: Mobility data for a geohash
            
        Returns:
            Mobility threat score from 0 to 10
        """
        if mobility_data is None:
            logger.warning(f"{self.node_name}: No mobility data available, returning 0")
            return 0.0
        
        try:
            score = 0.0
            
            # Factor 1: Average delay (0-4 points)
            avg_delay = mobility_data.average_delay_minutes
            if avg_delay == 0:
                score += 0.0
            elif avg_delay < 5:
                score += 1.0
            elif avg_delay < 10:
                score += 2.0
            elif avg_delay < 15:
                score += 3.0
            elif avg_delay < 30:
                score += 3.5
            else:
                score += 4.0
            
            # Factor 2: Cancelled routes (0-3 points)
            cancelled = mobility_data.cancelled_routes
            if cancelled == 0:
                score += 0.0
            elif cancelled < 3:
                score += 1.0
            elif cancelled < 5:
                score += 2.0
            else:
                score += 3.0
            
            # Factor 3: Status-based penalty (0-3 points)
            from metabolic_city.utils.data_models import MobilityStatus
            status = mobility_data.status
            if status == MobilityStatus.NORMAL:
                score += 0.0
            elif status == MobilityStatus.DELAYED:
                score += 1.0
            elif status == MobilityStatus.SEVERELY_DELAYED:
                score += 2.0
            elif status == MobilityStatus.CANCELLED:
                score += 2.5
            elif status == MobilityStatus.SUSPENDED:
                score += 3.0
            
            # Ensure score is within bounds
            score = max(0.0, min(10.0, score))
            
            logger.debug(f"{self.node_name}: Evaluated geohash {mobility_data.geohash} - Score: {score:.2f}")
            return score
            
        except Exception as e:
            logger.error(f"{self.node_name}: Error evaluating mobility data: {e}")
            return 0.0
    
    def evaluate_batch(self, mobility_data_dict: dict) -> dict:
        """
        Evaluate mobility threat scores for multiple geohashes
        
        Args:
            mobility_data_dict: Dictionary mapping geohash to MobilityData
            
        Returns:
            Dictionary mapping geohash to mobility score
        """
        results = {}
        for geohash, mobility_data in mobility_data_dict.items():
            results[geohash] = self.evaluate(mobility_data)
        
        logger.info(f"{self.node_name}: Evaluated {len(results)} geohashes")
        return results
