"""
Analysis Orchestrator - Coordinates isolated domain nodes
"""

import asyncio
from typing import Dict, Optional
from loguru import logger

from metabolic_city.utils.data_models import UnifiedDataPoint, RiskScore
from metabolic_city.analysis.mobility_node import MobilityNode
from metabolic_city.analysis.climate_node import ClimateNode
from metabolic_city.analysis.vulnerability_node import VulnerabilityNode


class AnalysisOrchestrator:
    """
    Orchestrates parallel execution of isolated domain nodes.
    Implements graceful degradation if individual feeds fail.
    """
    
    def __init__(self):
        self.mobility_node = MobilityNode()
        self.climate_node = ClimateNode()
        self.vulnerability_node = VulnerabilityNode()
    
    async def analyze_unified_data(
        self,
        unified_data: Dict[str, UnifiedDataPoint]
    ) -> Dict[str, RiskScore]:
        """
        Analyze unified data using all isolated nodes in parallel
        
        Args:
            unified_data: Dictionary mapping geohash to UnifiedDataPoint
            
        Returns:
            Dictionary mapping geohash to RiskScore
        """
        logger.info("Starting parallel analysis of unified data")
        
        # Extract domain-specific data
        mobility_data_dict = {}
        climate_data_dict = {}
        demographic_data_dict = {}
        
        for geohash, data_point in unified_data.items():
            if data_point.mobility:
                mobility_data_dict[geohash] = data_point.mobility
            if data_point.climate:
                climate_data_dict[geohash] = data_point.climate
            if data_point.demographic:
                demographic_data_dict[geohash] = data_point.demographic
        
        # Run isolated nodes in parallel
        logger.info("Running isolated domain nodes in parallel...")
        mobility_scores, climate_scores, vulnerability_scores = await asyncio.gather(
            asyncio.to_thread(self.mobility_node.evaluate_batch, mobility_data_dict),
            asyncio.to_thread(self.climate_node.evaluate_batch, climate_data_dict),
            asyncio.to_thread(self.vulnerability_node.evaluate_batch, demographic_data_dict),
            return_exceptions=True
        )
        
        # Handle exceptions (graceful degradation)
        if isinstance(mobility_scores, Exception):
            logger.error(f"Mobility node failed: {mobility_scores}")
            mobility_scores = {}
        
        if isinstance(climate_scores, Exception):
            logger.error(f"Climate node failed: {climate_scores}")
            climate_scores = {}
        
        if isinstance(vulnerability_scores, Exception):
            logger.error(f"Vulnerability node failed: {vulnerability_scores}")
            vulnerability_scores = {}
        
        # Combine scores into RiskScore objects
        risk_scores = {}
        for geohash in unified_data.keys():
            mobility_score = mobility_scores.get(geohash, 0.0)
            climate_score = climate_scores.get(geohash, 0.0)
            vulnerability_score = vulnerability_scores.get(geohash, 0.0)
            
            risk_scores[geohash] = RiskScore(
                geohash=geohash,
                timestamp=unified_data[geohash].timestamp,
                mobility_score=mobility_score,
                climate_score=climate_score,
                vulnerability_score=vulnerability_score,
                composite_risk_index=0.0,  # Will be calculated in triage stage
                risk_level="pending"  # Will be determined in triage stage
            )
        
        logger.info(f"Analysis complete: {len(risk_scores)} geohashes evaluated")
        logger.info(f"Graceful degradation status: Mobility={len(mobility_scores)}, Climate={len(climate_scores)}, Vulnerability={len(vulnerability_scores)}")
        
        return risk_scores
    
    def get_active_domains(self, unified_data: Dict[str, UnifiedDataPoint]) -> Dict[str, bool]:
        """
        Check which domains have active data
        
        Args:
            unified_data: Dictionary mapping geohash to UnifiedDataPoint
            
        Returns:
            Dictionary with domain availability status
        """
        has_mobility = any(dp.mobility is not None for dp in unified_data.values())
        has_climate = any(dp.climate is not None for dp in unified_data.values())
        has_demographic = any(dp.demographic is not None for dp in unified_data.values())
        
        return {
            "mobility": has_mobility,
            "climate": has_climate,
            "demographic": has_demographic
        }
