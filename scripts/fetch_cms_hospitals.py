#!/usr/bin/env python3
"""
Fetch Hospital Data from CMS
============================

Downloads hospital data from CMS Provider Data Catalog,
geocodes addresses in ski states, and filters to hospitals near resorts.

Usage:
    python scripts/fetch_cms_hospitals.py
"""

import json
import math
import time
import os
import requests
import csv
from io import StringIO

# CMS Hospital Data API
CMS_HOSPITAL_METADATA = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items/xubh-q36u"

# Files
RESORTS_FILE = "public/resorts.json"
OUTPUT_FILE = "public/hospitals.json"
CACHE_FILE = "hospital_geocode_cache.json"

# Maximum distance from any ski resort (miles)
MAX_DISTANCE_MILES = 75

# States with ski resorts (only geocode these)
SKI_STATES = {
    "CA", "CO", "UT", "WY", "MT", "ID", "NM", "AZ", "NV",
    "WA", "OR", "VT", "NH", "ME", "NY", "PA", "MA", "CT", "NJ",
    "MI", "WI", "MN", "OH", "IN", "MO", "WV", "VA", "NC", "TN",
}


def haversine_miles(lat1, lon1, lat2, lon2):
    r = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_resorts():
    try:
        with open(RESORTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def geocode_address(address, city, state, zipcode):
    """Geocode via US Census Bureau Geocoder."""
    full_address = f"{address}, {city}, {state} {zipcode}"
    
    try:
        resp = requests.get(
            "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
            params={
                "address": full_address,
                "benchmark": "Public_AR_Current",
                "format": "json"
            },
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            coords = matches[0].get("coordinates", {})
            return coords.get("y"), coords.get("x")  # lat, lon
    except:
        pass
    return None, None


def main():
    print("=" * 60)
    print("SkiWithCare - CMS Hospital Data Fetcher")
    print("=" * 60, flush=True)
    
    resorts = load_resorts()
    if not resorts:
        print("ERROR: No resort data. Run build_resorts.py first.")
        return
    print(f"Loaded {len(resorts)} resorts", flush=True)
    
    cache = load_cache()
    print(f"Loaded {len(cache)} cached geocodes", flush=True)
    
    # Get CSV URL
    print(f"\nFetching hospital data from CMS...", flush=True)
    try:
        meta = requests.get(CMS_HOSPITAL_METADATA, timeout=30).json()
        csv_url = next(d["downloadURL"] for d in meta["distribution"] if "csv" in d.get("mediaType", ""))
        resp = requests.get(csv_url, timeout=120)
        resp.raise_for_status()
        print(f"  Downloaded {len(resp.content) / 1024 / 1024:.1f} MB", flush=True)
    except Exception as e:
        print(f"  ERROR: {e}")
        return
    
    reader = csv.DictReader(StringIO(resp.text))
    rows = [r for r in reader if r.get("State") in SKI_STATES]
    print(f"  {len(rows)} hospitals in ski states", flush=True)
    
    # Geocode and filter
    print(f"\nGeocoding hospitals (this may take a while)...", flush=True)
    hospitals = []
    geocoded = 0
    cached = 0
    
    for i, row in enumerate(rows):
        facility_id = row.get("Facility ID", "")
        name = row.get("Facility Name", "")
        address = row.get("Address", "")
        city = row.get("City/Town", "")
        state = row.get("State", "")
        zipcode = row.get("ZIP Code", "")
        
        # Check cache
        cache_key = facility_id
        if cache_key in cache:
            lat, lon = cache[cache_key].get("lat"), cache[cache_key].get("lon")
            cached += 1
        else:
            lat, lon = geocode_address(address, city, state, zipcode)
            cache[cache_key] = {"lat": lat, "lon": lon}
            geocoded += 1
            time.sleep(0.3)  # Rate limit
        
        if not lat or not lon:
            continue
        
        # Find nearest resort
        min_dist = float("inf")
        nearest_resort = None
        for resort in resorts:
            dist = haversine_miles(lat, lon, resort["lat"], resort["lon"])
            if dist < min_dist:
                min_dist = dist
                nearest_resort = resort["name"]
        
        if min_dist > MAX_DISTANCE_MILES:
            continue
        
        hospitals.append({
            "id": facility_id,
            "name": name,
            "address": address,
            "city": city,
            "state": state,
            "zip": zipcode,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "hasEmergency": row.get("Emergency Services", "").lower() == "yes",
            "phone": row.get("Telephone Number", ""),
            "nearestResort": nearest_resort,
            "nearestResortDist": round(min_dist, 1),
        })
        
        # Progress
        if (i + 1) % 100 == 0:
            print(f"  [{i+1}/{len(rows)}] {len(hospitals)} near resorts...", flush=True)
            save_cache(cache)
    
    save_cache(cache)
    
    # Sort and save
    hospitals.sort(key=lambda h: (h["state"], h["name"]))
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(hospitals, f, indent=2)
    
    er_count = sum(1 for h in hospitals if h.get("hasEmergency"))
    
    print("\n" + "=" * 60)
    print(f"SUCCESS: {len(hospitals)} hospitals within {MAX_DISTANCE_MILES} mi of resorts")
    print(f"  With Emergency Room: {er_count}")
    print(f"  Geocoded: {geocoded} new, {cached} cached")
    print("=" * 60)


if __name__ == "__main__":
    main()
