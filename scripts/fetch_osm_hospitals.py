#!/usr/bin/env python3
"""
Fetch Hospital Data from OpenStreetMap
======================================

Queries the OSM Overpass API STATE BY STATE for hospitals,
then filters to those within reasonable distance of ski resorts.

Usage:
    python scripts/fetch_osm_hospitals.py
"""

import json
import time
import math
import requests
from typing import Optional, List

# Overpass API endpoints
OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

# Files
RESORTS_FILE = "public/resorts.json"
OUTPUT_FILE = "public/hospitals.json"

# Maximum distance from any ski resort (miles)
MAX_DISTANCE_MILES = 75

# States with ski resorts
SKI_STATES = [
    "California", "Colorado", "Utah", "Wyoming", "Montana", "Idaho",
    "New Mexico", "Arizona", "Nevada", "Washington", "Oregon",
    "Vermont", "New Hampshire", "Maine", "New York", "Pennsylvania",
    "Massachusetts", "Connecticut", "New Jersey",
    "Michigan", "Wisconsin", "Minnesota", "Ohio", "Indiana", "Missouri",
    "West Virginia", "Virginia", "North Carolina", "Tennessee",
]

STATE_ABBREVS = {
    "California": "CA", "Colorado": "CO", "Utah": "UT", "Wyoming": "WY",
    "Montana": "MT", "Idaho": "ID", "New Mexico": "NM", "Arizona": "AZ",
    "Nevada": "NV", "Washington": "WA", "Oregon": "OR", "Vermont": "VT",
    "New Hampshire": "NH", "Maine": "ME", "New York": "NY", "Pennsylvania": "PA",
    "Massachusetts": "MA", "Connecticut": "CT", "New Jersey": "NJ",
    "Michigan": "MI", "Wisconsin": "WI", "Minnesota": "MN", "Ohio": "OH",
    "Indiana": "IN", "Missouri": "MO", "West Virginia": "WV", "Virginia": "VA",
    "North Carolina": "NC", "Tennessee": "TN",
}


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in miles."""
    r = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_resorts() -> List[dict]:
    """Load existing resort data."""
    try:
        with open(RESORTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def fetch_hospitals_for_state(state_name: str) -> List[dict]:
    """Fetch hospitals from OSM for a specific state."""
    query = f"""
    [out:json][timeout:60];
    area["name"="{state_name}"]["admin_level"="4"]->.state;
    (
      nwr["amenity"="hospital"]["name"](area.state);
    );
    out center tags;
    """
    
    for endpoint in OVERPASS_ENDPOINTS:
        for attempt in range(2):
            try:
                resp = requests.post(
                    endpoint,
                    data={"data": query},
                    headers={"User-Agent": "SkiWithCare/2.0"},
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.json().get("elements", [])
            except requests.RequestException:
                if attempt == 0:
                    time.sleep(3)
    return []


def process_hospital(el: dict, state_abbrev: str, resorts: List[dict]) -> Optional[dict]:
    """Process an OSM element into a hospital record."""
    tags = el.get("tags", {})
    name = tags.get("name")
    
    if not name:
        return None
    
    # Get coordinates
    if el.get("type") == "node":
        lat, lon = el.get("lat"), el.get("lon")
    else:
        center = el.get("center", {})
        lat, lon = center.get("lat"), center.get("lon")
    
    if not lat or not lon:
        return None
    
    # Find nearest resort
    min_dist = float("inf")
    nearest_resort = None
    
    for resort in resorts:
        dist = haversine_miles(lat, lon, resort["lat"], resort["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest_resort = resort["name"]
    
    # Skip if too far
    if min_dist > MAX_DISTANCE_MILES:
        return None
    
    has_emergency = tags.get("emergency") == "yes" or "emergency" in name.lower()
    
    return {
        "id": f"osm-{el.get('id')}",
        "name": name,
        "address": tags.get("addr:street", ""),
        "city": tags.get("addr:city", ""),
        "state": state_abbrev,
        "zip": tags.get("addr:postcode", ""),
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "hasEmergency": has_emergency,
        "phone": tags.get("phone", ""),
        "nearestResort": nearest_resort,
        "nearestResortDist": round(min_dist, 1),
    }


def main():
    """Main execution."""
    print("=" * 60)
    print("SkiWithCare - OSM Hospital Data Fetcher")
    print("=" * 60)
    
    resorts = load_resorts()
    if not resorts:
        print("ERROR: No resort data. Run fetch_osm_resorts.py first.")
        return
    
    print(f"Loaded {len(resorts)} resorts")
    print(f"Querying {len(SKI_STATES)} states...\n")
    
    all_hospitals = []
    seen_ids = set()
    
    for state_name in SKI_STATES:
        state_abbrev = STATE_ABBREVS.get(state_name, state_name[:2])
        print(f"Fetching hospitals in {state_name}...", end=" ", flush=True)
        
        elements = fetch_hospitals_for_state(state_name)
        count = 0
        
        for el in elements:
            hospital = process_hospital(el, state_abbrev, resorts)
            if hospital and hospital["id"] not in seen_ids:
                seen_ids.add(hospital["id"])
                all_hospitals.append(hospital)
                count += 1
        
        print(f"found {count} near ski areas")
        time.sleep(2)
    
    # Sort
    all_hospitals.sort(key=lambda h: (h["state"], h["name"]))
    
    # Write
    print(f"\nWriting {len(all_hospitals)} hospitals to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_hospitals, f, indent=2)
    
    er_count = sum(1 for h in all_hospitals if h.get("hasEmergency"))
    print("\n" + "=" * 60)
    print(f"SUCCESS: {len(all_hospitals)} hospitals within {MAX_DISTANCE_MILES} mi of resorts")
    print(f"  With Emergency: {er_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
