"""
Climate Feed - Weather API data ingestion
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from metabolic_city.config.settings import settings
from metabolic_city.utils.data_models import ClimateData, ClimateStatus
from metabolic_city.utils.geohash_utils import encode_geohash, decode_geohash


class ClimateFeed:
    """Handles weather data ingestion from meteorological APIs"""
    
    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = settings.weather_api_base_url
        self.provider = settings.weather_api_provider
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_weather_by_coordinates(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for specific coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Weather data dictionary or None if failed
        """
        if not self.api_key:
            logger.warning("Weather API key not configured, using mock data")
            return self._generate_mock_weather(latitude, longitude)
        
        try:
            if self.provider == "openweathermap":
                return await self._fetch_openweathermap(latitude, longitude)
            else:
                logger.warning(f"Unsupported weather provider: {self.provider}")
                return self._generate_mock_weather(latitude, longitude)
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._generate_mock_weather(latitude, longitude)
    
    async def _fetch_openweathermap(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Fetch data from OpenWeatherMap API"""
        url = f"{self.base_url}/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"Successfully fetched weather for {latitude}, {longitude}")
                return data
            else:
                logger.error(f"Failed to fetch weather: HTTP {response.status}")
                return None
    
    def _generate_mock_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Generate mock weather data for testing/demo"""
        import random
        return {
            "main": {
                "temp": random.uniform(15, 35),
                "humidity": random.uniform(30, 90),
                "pressure": random.uniform(1000, 1030)
            },
            "wind": {
                "speed": random.uniform(0, 50)
            },
            "rain": {
                "1h": random.uniform(0, 10) if random.random() > 0.7 else 0
            },
            "weather": [{
                "main": random.choice(["Clear", "Clouds", "Rain", "Storm", "Snow"]),
                "description": "mock weather data"
            }],
            "coord": {"lat": latitude, "lon": longitude}
        }
    
    def parse_weather_data(self, raw_data: Dict[str, Any], geohash: str) -> ClimateData:
        """
        Parse raw weather API data into ClimateData model
        
        Args:
            raw_data: Raw weather API response
            geohash: Geohash for the location
            
        Returns:
            ClimateData object
        """
        main = raw_data.get("main", {})
        wind = raw_data.get("wind", {})
        rain = raw_data.get("rain", {})
        weather_list = raw_data.get("weather", [])
        
        temperature = main.get("temp", 0.0)
        humidity = main.get("humidity", 0.0)
        pressure = main.get("pressure", 0.0)
        wind_speed = wind.get("speed", 0.0)
        precipitation = rain.get("1h", 0.0)
        
        # Determine weather warnings
        warnings = []
        if temperature > 35:
            warnings.append("extreme_heat")
        elif temperature < 0:
            warnings.append("freezing")
        
        if precipitation > 20:
            warnings.append("heavy_rain")
        elif precipitation > 50:
            warnings.append("flash_flood")
        
        if wind_speed > 50:
            warnings.append("high_wind")
        
        # Determine status
        if warnings:
            if "flash_flood" in warnings or "extreme_heat" in warnings:
                status = ClimateStatus.EMERGENCY
            elif "high_wind" in warnings or "heavy_rain" in warnings:
                status = ClimateStatus.WARNING
            else:
                status = ClimateStatus.ADVISORY
        else:
            status = ClimateStatus.NORMAL
        
        return ClimateData(
            geohash=geohash,
            timestamp=datetime.utcnow(),
            temperature_celsius=temperature,
            humidity_percent=humidity,
            pressure_hpa=pressure,
            precipitation_mm=precipitation,
            wind_speed_kmh=wind_speed * 3.6,  # Convert m/s to km/h
            status=status,
            weather_warnings=warnings,
            raw_data=raw_data
        )
    
    async def fetch_grid_weather(
        self,
        geohashes: List[str],
        precision: int = 6
    ) -> Dict[str, ClimateData]:
        """
        Fetch weather data for a grid of geohashes
        
        Args:
            geohashes: List of geohash strings
            precision: Geohash precision
            
        Returns:
            Dictionary mapping geohash to ClimateData
        """
        climate_data = {}
        
        # Fetch weather for each geohash center point
        tasks = []
        for geohash in geohashes:
            lat, lon, _ = decode_geohash(geohash)
            task = self.fetch_weather_by_coordinates(lat, lon)
            tasks.append((geohash, task))
        
        # Execute concurrently
        results = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )
        
        # Parse results
        for (geohash, _), result in zip(tasks, results):
            if isinstance(result, dict) and result:
                climate_data[geohash] = self.parse_weather_data(result, geohash)
            elif isinstance(result, Exception):
                logger.error(f"Error fetching weather for {geohash}: {result}")
        
        logger.info(f"Fetched climate data for {len(climate_data)} geohashes")
        return climate_data
    
    async def fetch_and_process(self, geohashes: List[str]) -> Dict[str, ClimateData]:
        """
        Main method to fetch and process climate data
        
        Args:
            geohashes: List of geohash strings to fetch weather for
            
        Returns:
            Dictionary mapping geohash to ClimateData
        """
        async with self:
            climate_data = await self.fetch_grid_weather(geohashes, settings.geohash_precision)
            return climate_data
