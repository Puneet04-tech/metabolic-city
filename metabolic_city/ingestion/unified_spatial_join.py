"""
Unified Spatial Join - Combines all data sources into unified geohash grid
"""

from typing import Dict, Optional
from loguru import logger

from metabolic_city.utils.data_models import UnifiedDataPoint, MobilityData, ClimateData, DemographicData
from metabolic_city.ingestion.mobility_feed import MobilityFeed
from metabolic_city.ingestion.climate_feed import ClimateFeed
from metabolic_city.ingestion.demographic_loader import DemographicLoader


class UnifiedSpatialJoin:
    """
    Combines mobility, climate, and demographic data into unified spatial grid
    """
    
    def __init__(self):
        self.mobility_feed = MobilityFeed()
        self.climate_feed = ClimateFeed()
        self.demographic_loader = DemographicLoader()
    
    async def fetch_all_data(self) -> Dict[str, UnifiedDataPoint]:
        """
        Fetch and combine all data sources into unified grid
        
        Returns:
            Dictionary mapping geohash to UnifiedDataPoint
        """
        logger.info("Starting unified spatial join process")
        
        # Fetch mobility data
        logger.info("Fetching mobility data...")
        mobility_data = await self.mobility_feed.fetch_and_process()
        
        # Get all geohashes from mobility data
        all_geohashes = set(mobility_data.keys())
        
        # Fetch climate data for these geohashes
        logger.info(f"Fetching climate data for {len(all_geohashes)} geohashes...")
        climate_data = await self.climate_feed.fetch_and_process(list(all_geohashes))
        
        # Fetch demographic data for these geohashes
        logger.info("Fetching demographic data...")
        demographic_data = self.demographic_loader.get_all_demographic_data(list(all_geohashes))
        
        # Combine into unified data points
        unified_data = {}
        for geohash in all_geohashes:
            unified_data[geohash] = UnifiedDataPoint(
                geohash=geohash,
                timestamp=mobility_data[geohash].timestamp,
                mobility=mobility_data.get(geohash),
                climate=climate_data.get(geohash),
                demographic=demographic_data.get(geohash)
            )
        
        logger.info(f"Created {len(unified_data)} unified data points")
        return unified_data
    
    def create_unified_point(
        self,
        geohash: str,
        mobility: Optional[MobilityData],
        climate: Optional[ClimateData],
        demographic: Optional[DemographicData]
    ) -> UnifiedDataPoint:
        """
        Create a unified data point from individual domain data
        
        Args:
            geohash: Geohash identifier
            mobility: Mobility data (optional)
            climate: Climate data (optional)
            demographic: Demographic data (optional)
            
        Returns:
            UnifiedDataPoint object
        """
        # Use the most recent timestamp from available data
        timestamps = []
        if mobility:
            timestamps.append(mobility.timestamp)
        if climate:
            timestamps.append(climate.timestamp)
        if demographic:
            timestamps.append(demographic.timestamp)
        
        timestamp = max(timestamps) if timestamps else None
        
        return UnifiedDataPoint(
            geohash=geohash,
            timestamp=timestamp,
            mobility=mobility,
            climate=climate,
            demographic=demographic
        )
    
    async def refresh_data(self) -> Dict[str, UnifiedDataPoint]:
        """
        Refresh all data sources and return updated unified grid
        
        Returns:
            Dictionary mapping geohash to UnifiedDataPoint
        """
        return await self.fetch_all_data()
    
    def get_data_for_geohash(self, geohash: str) -> Optional[UnifiedDataPoint]:
        """
        Get unified data for a specific geohash (from cached data)
        
        Args:
            geohash: Geohash string
            
        Returns:
            UnifiedDataPoint or None if not found
        """
        # This would typically access cached data
        # For now, return None as this is meant to be used with fetch_all_data
        logger.warning("get_data_for_geohash requires cached data from fetch_all_data")
        return None
