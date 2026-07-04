"""
Demographic Loader - Census and socio-demographic baseline data
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

from metabolic_city.utils.data_models import DemographicData
from metabolic_city.utils.geohash_utils import encode_geohash


class DemographicLoader:
    """Handles loading and processing of demographic baseline data"""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize demographic loader
        
        Args:
            data_path: Path to demographic data file (JSON format)
        """
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = Path("metabolic_city/data/demographic_baseline.json")
        
        self._cache: Optional[Dict[str, Any]] = None
        self._geohash_index: Optional[Dict[str, Dict[str, Any]]] = None
    
    def load_demographic_data(self) -> Dict[str, Any]:
        """
        Load demographic data from file
        
        Returns:
            Dictionary containing demographic data
        """
        if self._cache is not None:
            return self._cache
        
        if not self.data_path.exists():
            logger.warning(f"Demographic data file not found at {self.data_path}, generating mock data")
            self._cache = self._generate_mock_demographic_data()
            self._save_demographic_data(self._cache)
            return self._cache
        
        try:
            with open(self.data_path, 'r') as f:
                self._cache = json.load(f)
            logger.info(f"Loaded demographic data from {self.data_path}")
            return self._cache
        except Exception as e:
            logger.error(f"Error loading demographic data: {e}")
            self._cache = self._generate_mock_demographic_data()
            return self._cache
    
    def _save_demographic_data(self, data: Dict[str, Any]):
        """Save demographic data to file"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved demographic data to {self.data_path}")
        except Exception as e:
            logger.error(f"Error saving demographic data: {e}")
    
    def _generate_mock_demographic_data(self) -> Dict[str, Any]:
        """Generate mock demographic data for testing/demo"""
        import random
        
        # Generate census blocks with demographic data
        census_blocks = []
        for i in range(100):
            # Random coordinates around a city center
            lat = 40.7128 + random.uniform(-0.1, 0.1)
            lon = -74.0060 + random.uniform(-0.1, 0.1)
            
            census_blocks.append({
                "block_id": f"block_{i}",
                "latitude": lat,
                "longitude": lon,
                "population": random.randint(100, 5000),
                "households": random.randint(50, 2000),
                "vehicle_ownership": random.uniform(0.3, 0.95),
                "elderly_population": random.randint(10, 500),
                "youth_population": random.randint(20, 800),
                "working_age_population": random.randint(100, 3000),
                "median_income": random.randint(30000, 150000),
                "below_poverty_line": random.uniform(0.05, 0.3),
                "limited_english_proficiency": random.uniform(0.0, 0.4),
                "disability_population": random.randint(5, 200)
            })
        
        logger.info(f"Generated mock demographic data for {len(census_blocks)} census blocks")
        return {"census_blocks": census_blocks}
    
    def build_geohash_index(self, precision: int = 6) -> Dict[str, Dict[str, Any]]:
        """
        Build geohash index for demographic data
        
        Args:
            precision: Geohash precision
            
        Returns:
            Dictionary mapping geohash to demographic data
        """
        if self._geohash_index is not None:
            return self._geohash_index
        
        data = self.load_demographic_data()
        census_blocks = data.get("census_blocks", [])
        
        geohash_index = {}
        
        for block in census_blocks:
            lat = block.get("latitude")
            lon = block.get("longitude")
            if lat and lon:
                geohash = encode_geohash(lat, lon, precision)
                
                # Calculate derived metrics
                total_pop = block.get("population", 0)
                elderly = block.get("elderly_population", 0)
                youth = block.get("youth_population", 0)
                working_age = block.get("working_age_population", 0)
                
                elderly_ratio = elderly / working_age if working_age > 0 else 0
                youth_ratio = youth / working_age if working_age > 0 else 0
                
                # Calculate financial stress index (inverse of income, normalized)
                median_income = block.get("median_income", 50000)
                financial_stress = max(0, min(10, (100000 - median_income) / 10000))
                
                # Language access barrier
                lep_rate = block.get("limited_english_proficiency", 0)
                language_barrier = lep_rate * 25  # Scale to 0-10
                
                # Disability access needs
                disability_pop = block.get("disability_population", 0)
                disability_access = (disability_pop / total_pop * 100) if total_pop > 0 else 0
                
                # Population density (simplified)
                density = total_pop / 0.01  # Assuming ~0.01 sq km per block
                
                geohash_index[geohash] = {
                    "population_density": density,
                    "vehicle_ownership_rate": block.get("vehicle_ownership", 0.7),
                    "elderly_dependency_ratio": elderly_ratio,
                    "youth_dependency_ratio": youth_ratio,
                    "financial_stress_index": financial_stress,
                    "language_access_barrier": language_barrier,
                    "disability_access_needs": disability_access,
                    "raw_census_data": block
                }
        
        self._geohash_index = geohash_index
        logger.info(f"Built geohash index for {len(geohash_index)} geohashes")
        return geohash_index
    
    def get_demographic_data(self, geohash: str) -> Optional[DemographicData]:
        """
        Get demographic data for a specific geohash
        
        Args:
            geohash: Geohash string
            
        Returns:
            DemographicData object or None if not found
        """
        index = self.build_geohash_index()
        
        if geohash not in index:
            logger.warning(f"No demographic data found for geohash {geohash}")
            return None
        
        data = index[geohash]
        
        return DemographicData(
            geohash=geohash,
            timestamp=datetime.utcnow(),
            population_density=data["population_density"],
            vehicle_ownership_rate=data["vehicle_ownership_rate"],
            elderly_dependency_ratio=data["elderly_dependency_ratio"],
            youth_dependency_ratio=data["youth_dependency_ratio"],
            financial_stress_index=data["financial_stress_index"],
            language_access_barrier=data["language_access_barrier"],
            disability_access_needs=data["disability_access_needs"],
            raw_data=data["raw_census_data"]
        )
    
    def get_all_demographic_data(self, geohashes: list) -> Dict[str, DemographicData]:
        """
        Get demographic data for multiple geohashes
        
        Args:
            geohashes: List of geohash strings
            
        Returns:
            Dictionary mapping geohash to DemographicData
        """
        demographic_data = {}
        
        for geohash in geohashes:
            demo = self.get_demographic_data(geohash)
            if demo:
                demographic_data[geohash] = demo
        
        return demographic_data
