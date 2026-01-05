"""
Geocoding Utilities
===================

Functions for geocoding resorts and facilities using free public APIs.
"""

import json
import math
import os
import time
from typing import Dict, Optional, Tuple

import requests

# Rate limiting (seconds between API calls)
NOMINATIM_DELAY = 1.1  # Nominatim requires ~1 request/second
CENSUS_DELAY = 0.3     # Census API is faster


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in miles."""
    r = 3958.7613  # Earth's radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_json_cache(filepath: str) -> Dict:
    """Load cache from JSON file."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_json_cache(cache: Dict, filepath: str) -> None:
    """Save cache to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(cache, f, indent=2)


def geocode_resort_nominatim(
    name: str, 
    state: str,
    delay: float = NOMINATIM_DELAY
) -> Tuple[Optional[float], Optional[float], str]:
    """
    Geocode a ski resort using OpenStreetMap Nominatim.
    
    Args:
        name: Resort name
        state: State abbreviation
        delay: Seconds to sleep after request (rate limiting)
    
    Returns:
        Tuple of (lat, lon, query_string)
    """
    query = f"{name}, {state}, USA"
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "skiwithcare/2.0 (personal project)"}
    params = {"q": query, "format": "json", "limit": 1}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=60)
        resp.raise_for_status()
        results = resp.json()
        
        time.sleep(delay)
        
        if not results:
            return None, None, query
        
        return float(results[0]["lat"]), float(results[0]["lon"]), query
        
    except requests.RequestException as e:
        print(f"  [ERROR] Geocoding failed for '{query}': {e}")
        return None, None, query


def geocode_facility_census(
    address: str, 
    city: str, 
    state: str, 
    zipcode: str,
    delay: float = CENSUS_DELAY
) -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode a facility using US Census Bureau Geocoder.
    
    Args:
        address: Street address
        city: City name
        state: State abbreviation
        zipcode: ZIP code
        delay: Seconds to sleep after request (rate limiting)
    
    Returns:
        Tuple of (lat, lon) or (None, None) if failed
    """
    full_address = f"{address}, {city}, {state} {zipcode}"
    
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    params = {
        "address": full_address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        time.sleep(delay)
        
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            coords = matches[0].get("coordinates", {})
            # Census returns x=lon, y=lat
            lon = coords.get("x")
            lat = coords.get("y")
            if lat and lon:
                return float(lat), float(lon)
        
        return None, None
        
    except requests.RequestException:
        return None, None


class ResortGeocoder:
    """Geocoder for ski resorts with caching."""
    
    def __init__(self, cache_file: str = "resort_geocoded_cache.json"):
        self.cache_file = cache_file
        self.cache = load_json_cache(cache_file)
    
    def geocode(self, name: str, state: str) -> Tuple[Optional[float], Optional[float]]:
        """Geocode a resort, using cache if available."""
        cache_key = f"{name}|{state}"
        
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            return cached.get("lat"), cached.get("lon")
        
        lat, lon, query = geocode_resort_nominatim(name, state)
        self.cache[cache_key] = {"lat": lat, "lon": lon, "query": query}
        return lat, lon
    
    def save(self):
        """Save cache to file."""
        save_json_cache(self.cache, self.cache_file)


class FacilityGeocoder:
    """Geocoder for healthcare facilities with caching."""
    
    def __init__(self, cache_file: str = "facility_geocoded_cache.json"):
        self.cache_file = cache_file
        self.cache = load_json_cache(cache_file)
    
    def geocode(
        self, 
        ccn: str, 
        address: str, 
        city: str, 
        state: str, 
        zipcode: str
    ) -> Tuple[Optional[float], Optional[float]]:
        """Geocode a facility, using cache if available."""
        if ccn in self.cache:
            cached = self.cache[ccn]
            return cached.get("lat"), cached.get("lon")
        
        lat, lon = geocode_facility_census(address, city, state, zipcode)
        self.cache[ccn] = {"lat": lat, "lon": lon}
        return lat, lon
    
    def save(self):
        """Save cache to file."""
        save_json_cache(self.cache, self.cache_file)

