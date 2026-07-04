"""
Deterministic Matrix Triage Engine - Mathematical risk calculation
"""

from typing import Dict, List
from loguru import logger

from metabolic_city.config.settings import settings
from metabolic_city.utils.data_models import RiskScore


class TriageEngine:
    """
    Deterministic mathematical engine for calculating composite risk index.
    Uses transparent formula: Composite Risk Index = (W_mobility × S_mobility) + (W_climate × S_climate) + (W_vulnerability × S_vulnerability)
    """
    
    def __init__(self):
        self.weight_mobility = settings.weight_mobility
        self.weight_climate = settings.weight_climate
        self.weight_vulnerability = settings.weight_vulnerability
        self.risk_threshold = settings.risk_threshold
        
        # Validate weights sum to 1.0
        total_weight = self.weight_mobility + self.weight_climate + self.weight_vulnerability
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, normalizing to 1.0")
            self.weight_mobility /= total_weight
            self.weight_climate /= total_weight
            self.weight_vulnerability /= total_weight
        
        logger.info(f"TriageEngine initialized with weights: Mobility={self.weight_mobility:.2f}, Climate={self.weight_climate:.2f}, Vulnerability={self.weight_vulnerability:.2f}")
        logger.info(f"Risk threshold set to {self.risk_threshold}")
    
    def calculate_composite_risk(self, risk_score: RiskScore) -> RiskScore:
        """
        Calculate composite risk index using deterministic formula
        
        Args:
            risk_score: RiskScore object with individual domain scores
            
        Returns:
            Updated RiskScore with composite_risk_index and risk_level
        """
        try:
            # Apply weighted formula
            composite_risk = (
                (self.weight_mobility * risk_score.mobility_score) +
                (self.weight_climate * risk_score.climate_score) +
                (self.weight_vulnerability * risk_score.vulnerability_score)
            )
            
            # Ensure within bounds
            composite_risk = max(0.0, min(10.0, composite_risk))
            
            # Determine risk level
            if composite_risk >= 8.0:
                risk_level = "critical"
            elif composite_risk >= self.risk_threshold:
                risk_level = "high"
            elif composite_risk >= 4.0:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Update risk score
            risk_score.composite_risk_index = round(composite_risk, 2)
            risk_score.risk_level = risk_level
            
            logger.debug(f"Geohash {risk_score.geohash}: Composite Risk = {composite_risk:.2f}, Level = {risk_level}")
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Error calculating composite risk for {risk_score.geohash}: {e}")
            risk_score.composite_risk_index = 0.0
            risk_score.risk_level = "unknown"
            return risk_score
    
    def calculate_batch(self, risk_scores: Dict[str, RiskScore]) -> Dict[str, RiskScore]:
        """
        Calculate composite risk for multiple geohashes
        
        Args:
            risk_scores: Dictionary mapping geohash to RiskScore
            
        Returns:
            Updated dictionary with composite risk calculated
        """
        logger.info(f"Calculating composite risk for {len(risk_scores)} geohashes")
        
        for geohash, risk_score in risk_scores.items():
            risk_scores[geohash] = self.calculate_composite_risk(risk_score)
        
        return risk_scores
    
    def filter_by_threshold(self, risk_scores: Dict[str, RiskScore]) -> Dict[str, RiskScore]:
        """
        Filter risk scores that exceed the threshold
        
        Args:
            risk_scores: Dictionary mapping geohash to RiskScore
            
        Returns:
            Dictionary of risk scores that exceed threshold
        """
        filtered = {
            geohash: score
            for geohash, score in risk_scores.items()
            if score.composite_risk_index >= self.risk_threshold
        }
        
        logger.info(f"Filtered {len(filtered)} geohashes exceeding threshold {self.risk_threshold}")
        return filtered
    
    def get_risk_summary(self, risk_scores: Dict[str, RiskScore]) -> Dict[str, any]:
        """
        Generate summary statistics for risk scores
        
        Args:
            risk_scores: Dictionary mapping geohash to RiskScore
            
        Returns:
            Dictionary with summary statistics
        """
        if not risk_scores:
            return {"total": 0}
        
        composite_scores = [score.composite_risk_index for score in risk_scores.values()]
        
        return {
            "total_geohashes": len(risk_scores),
            "average_composite_risk": sum(composite_scores) / len(composite_scores),
            "max_composite_risk": max(composite_scores),
            "min_composite_risk": min(composite_scores),
            "critical_count": sum(1 for s in risk_scores.values() if s.risk_level == "critical"),
            "high_count": sum(1 for s in risk_scores.values() if s.risk_level == "high"),
            "medium_count": sum(1 for s in risk_scores.values() if s.risk_level == "medium"),
            "low_count": sum(1 for s in risk_scores.values() if s.risk_level == "low"),
            "above_threshold_count": sum(1 for s in risk_scores.values() if s.composite_risk_index >= self.risk_threshold)
        }
    
    def update_weights(self, mobility: float, climate: float, vulnerability: float):
        """
        Update operational weights (must sum to 1.0)
        
        Args:
            mobility: New mobility weight
            climate: New climate weight
            vulnerability: New vulnerability weight
        """
        total = mobility + climate + vulnerability
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        self.weight_mobility = mobility
        self.weight_climate = climate
        self.weight_vulnerability = vulnerability
        
        logger.info(f"Weights updated: Mobility={mobility:.2f}, Climate={climate:.2f}, Vulnerability={vulnerability:.2f}")
    
    def update_threshold(self, threshold: float):
        """
        Update risk threshold
        
        Args:
            threshold: New threshold value (0-10)
        """
        if not 0 <= threshold <= 10:
            raise ValueError("Threshold must be between 0 and 10")
        
        self.risk_threshold = threshold
        logger.info(f"Risk threshold updated to {threshold}")
