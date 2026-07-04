"""
Mobility Feed - GTFS-RT data ingestion
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from metabolic_city.config.settings import settings
from metabolic_city.utils.data_models import MobilityData, MobilityStatus
from metabolic_city.utils.geohash_utils import encode_geohash


class MobilityFeed:
    """Handles GTFS-RT data ingestion for transit information"""
    
    def __init__(self):
        self.vehicle_positions_url = settings.gtfs_rt_vehicle_positions_url
        self.trip_updates_url = settings.gtfs_rt_trip_updates_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_vehicle_positions(self) -> Optional[Dict[str, Any]]:
        """
        Fetch vehicle positions from GTFS-RT endpoint
        
        Returns:
            Raw vehicle positions data or None if failed
        """
        if not self.vehicle_positions_url:
            logger.warning("GTFS-RT vehicle positions URL not configured")
            return None
        
        try:
            async with self.session.get(self.vehicle_positions_url) as response:
                if response.status == 200:
                    data = await response.read()
                    logger.info(f"Successfully fetched vehicle positions ({len(data)} bytes)")
                    return {"raw_data": data, "timestamp": datetime.utcnow()}
                else:
                    logger.error(f"Failed to fetch vehicle positions: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching vehicle positions: {e}")
            return None
    
    async def fetch_trip_updates(self) -> Optional[Dict[str, Any]]:
        """
        Fetch trip updates from GTFS-RT endpoint
        
        Returns:
            Raw trip updates data or None if failed
        """
        if not self.trip_updates_url:
            logger.warning("GTFS-RT trip updates URL not configured")
            return None
        
        try:
            async with self.session.get(self.trip_updates_url) as response:
                if response.status == 200:
                    data = await response.read()
                    logger.info(f"Successfully fetched trip updates ({len(data)} bytes)")
                    return {"raw_data": data, "timestamp": datetime.utcnow()}
                else:
                    logger.error(f"Failed to fetch trip updates: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching trip updates: {e}")
            return None
    
    def parse_vehicle_positions(self, raw_data: bytes) -> List[Dict[str, Any]]:
        """
        Parse GTFS-RT vehicle positions protobuf data
        
        Args:
            raw_data: Raw protobuf bytes
            
        Returns:
            List of vehicle position dictionaries
        """
        try:
            from gtfs_realtime_bindings import FeedMessage
            
            feed = FeedMessage()
            feed.ParseFromString(raw_data)
            
            vehicles = []
            for entity in feed.entity:
                if entity.HasField("vehicle"):
                    vehicle = entity.vehicle
                    if vehicle.HasField("position"):
                        vehicles.append({
                            "id": vehicle.vehicle.id if vehicle.HasField("vehicle") else None,
                            "latitude": vehicle.position.latitude,
                            "longitude": vehicle.position.longitude,
                            "timestamp": vehicle.timestamp if vehicle.HasField("timestamp") else None,
                            "route_id": vehicle.vehicle.id if vehicle.HasField("vehicle") else None
                        })
            
            logger.info(f"Parsed {len(vehicles)} vehicle positions")
            return vehicles
            
        except ImportError:
            logger.warning("gtfs_realtime_bindings not installed, returning mock data")
            return self._generate_mock_vehicle_positions()
        except Exception as e:
            logger.error(f"Error parsing vehicle positions: {e}")
            return []
    
    def parse_trip_updates(self, raw_data: bytes) -> List[Dict[str, Any]]:
        """
        Parse GTFS-RT trip updates protobuf data
        
        Args:
            raw_data: Raw protobuf bytes
            
        Returns:
            List of trip update dictionaries
        """
        try:
            from gtfs_realtime_bindings import FeedMessage
            
            feed = FeedMessage()
            feed.ParseFromString(raw_data)
            
            updates = []
            for entity in feed.entity:
                if entity.HasField("trip_update"):
                    trip_update = entity.trip_update
                    for stop_time_update in trip_update.stop_time_update:
                        updates.append({
                            "trip_id": trip_update.trip.trip_id if trip_update.HasField("trip") else None,
                            "route_id": trip_update.trip.route_id if trip_update.HasField("trip") else None,
                            "stop_id": stop_time_update.stop_id,
                            "arrival_delay": stop_time_update.arrival.delay if stop_time_update.HasField("arrival") else 0,
                            "departure_delay": stop_time_update.departure.delay if stop_time_update.HasField("departure") else 0,
                            "schedule_relationship": str(stop_time_update.schedule_relationship)
                        })
            
            logger.info(f"Parsed {len(updates)} trip updates")
            return updates
            
        except ImportError:
            logger.warning("gtfs_realtime_bindings not installed, returning mock data")
            return self._generate_mock_trip_updates()
        except Exception as e:
            logger.error(f"Error parsing trip updates: {e}")
            return []
    
    def _generate_mock_vehicle_positions(self) -> List[Dict[str, Any]]:
        """Generate mock vehicle positions for testing/demo"""
        import random
        vehicles = []
        for i in range(50):
            vehicles.append({
                "id": f"vehicle_{i}",
                "latitude": 40.7128 + random.uniform(-0.1, 0.1),
                "longitude": -74.0060 + random.uniform(-0.1, 0.1),
                "timestamp": int(datetime.utcnow().timestamp()),
                "route_id": f"route_{random.randint(1, 10)}"
            })
        logger.info(f"Generated {len(vehicles)} mock vehicle positions")
        return vehicles
    
    def _generate_mock_trip_updates(self) -> List[Dict[str, Any]]:
        """Generate mock trip updates for testing/demo"""
        import random
        updates = []
        for i in range(30):
            delay = random.randint(0, 15)
            updates.append({
                "trip_id": f"trip_{i}",
                "route_id": f"route_{random.randint(1, 10)}",
                "stop_id": f"stop_{random.randint(1, 100)}",
                "arrival_delay": delay,
                "departure_delay": delay,
                "schedule_relationship": "SCHEDULED"
            })
        logger.info(f"Generated {len(updates)} mock trip updates")
        return updates
    
    async def aggregate_by_geohash(
        self,
        vehicles: List[Dict[str, Any]],
        updates: List[Dict[str, Any]],
        precision: int = 6
    ) -> Dict[str, MobilityData]:
        """
        Aggregate mobility data by geohash
        
        Args:
            vehicles: List of vehicle position dictionaries
            updates: List of trip update dictionaries
            precision: Geohash precision
            
        Returns:
            Dictionary mapping geohash to MobilityData
        """
        from collections import defaultdict
        
        # Group vehicles by geohash
        geohash_vehicles = defaultdict(list)
        for vehicle in vehicles:
            lat = vehicle.get("latitude")
            lon = vehicle.get("longitude")
            if lat and lon:
                geohash = encode_geohash(lat, lon, precision)
                geohash_vehicles[geohash].append(vehicle)
        
        # Calculate delays by geohash
        geohash_delays = defaultdict(list)
        for update in updates:
            delay = update.get("arrival_delay", 0)
            if delay > 0:
                # For simplicity, assign delay to random geohash with vehicles
                # In production, this would use stop location data
                if geohash_vehicles:
                    geohash = list(geohash_vehicles.keys())[0]
                    geohash_delays[geohash].append(delay)
        
        # Create MobilityData objects
        mobility_data = {}
        timestamp = datetime.utcnow()
        
        for geohash, vehicles_in_area in geohash_vehicles.items():
            delays = geohash_delays.get(geohash, [])
            avg_delay = sum(delays) / len(delays) if delays else 0.0
            
            # Determine status
            if avg_delay == 0:
                status = MobilityStatus.NORMAL
            elif avg_delay < 5:
                status = MobilityStatus.DELAYED
            elif avg_delay < 15:
                status = MobilityStatus.SEVERELY_DELAYED
            else:
                status = MobilityStatus.CANCELLED
            
            mobility_data[geohash] = MobilityData(
                geohash=geohash,
                timestamp=timestamp,
                vehicle_count=len(vehicles_in_area),
                average_delay_minutes=avg_delay,
                cancelled_routes=0,
                status=status,
                raw_data={"vehicles": vehicles_in_area, "updates": updates}
            )
        
        logger.info(f"Aggregated mobility data for {len(mobility_data)} geohashes")
        return mobility_data
    
    async def fetch_and_process(self) -> Dict[str, MobilityData]:
        """
        Main method to fetch and process mobility data
        
        Returns:
            Dictionary mapping geohash to MobilityData
        """
        async with self:
            # Fetch data concurrently
            vehicle_data, trip_data = await asyncio.gather(
                self.fetch_vehicle_positions(),
                self.fetch_trip_updates(),
                return_exceptions=True
            )
            
            # Parse data
            vehicles = []
            if isinstance(vehicle_data, dict) and vehicle_data:
                vehicles = self.parse_vehicle_positions(vehicle_data["raw_data"])
            
            updates = []
            if isinstance(trip_data, dict) and trip_data:
                updates = self.parse_trip_updates(trip_data["raw_data"])
            
            # Aggregate by geohash
            mobility_data = await self.aggregate_by_geohash(
                vehicles,
                updates,
                settings.geohash_precision
            )
            
            return mobility_data
