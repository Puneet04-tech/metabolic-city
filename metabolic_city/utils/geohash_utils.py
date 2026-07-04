"""
Geohash utilities for spatial normalization
"""

import geohash2
from typing import Tuple, List


def encode_geohash(latitude: float, longitude: float, precision: int = 6) -> str:
    """
    Encode latitude and longitude to geohash string
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        precision: Geohash precision (default 6, ~1.2km accuracy)
    
    Returns:
        Geohash string
    """
    return geohash2.encode(latitude, longitude, precision=precision)


def decode_geohash(geohash: str) -> Tuple[float, float, Tuple[float, float, float, float]]:
    """
    Decode geohash string to latitude, longitude, and bounding box
    
    Args:
        geohash: Geohash string
    
    Returns:
        Tuple of (latitude, longitude, (lat_min, lat_max, lon_min, lon_max))
    """
    lat, lon, lat_err, lon_err = geohash2.decode_exactly(geohash)
    return (lat, lon, (lat - lat_err, lat + lat_err, lon - lon_err, lon + lon_err))


def get_neighbors(geohash: str) -> List[str]:
    """
    Get the 8 neighboring geohashes around a given geohash
    
    Args:
        geohash: Center geohash
    
    Returns:
        List of 8 neighboring geohash strings
    """
    return geohash2.neighbors(geohash)


def get_geohash_bbox(geohash: str) -> Tuple[float, float, float, float]:
    """
    Get the bounding box of a geohash
    
    Args:
        geohash: Geohash string
    
    Returns:
        Tuple of (lat_min, lat_max, lon_min, lon_max)
    """
    _, _, bbox = decode_geohash(geohash)
    return bbox


def geohash_to_polygon(geohash: str) -> List[Tuple[float, float]]:
    """
    Convert geohash to polygon coordinates (4 corners)
    
    Args:
        geohash: Geohash string
    
    Returns:
        List of (lat, lon) tuples representing the polygon corners
    """
    lat_min, lat_max, lon_min, lon_max = get_geohash_bbox(geohash)
    return [
        (lat_min, lon_min),
        (lat_min, lon_max),
        (lat_max, lon_max),
        (lat_max, lon_min),
        (lat_min, lon_min)  # Close the polygon
    ]
