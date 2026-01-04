#!/usr/bin/env python3
"""
Fetch Hospital Data from OpenStreetMap
======================================

Queries the OSM Overpass API for hospitals in states that have ski resorts,
then filters to those within reasonable distance of ski areas.

Usage:
    python scripts/fetch_osm_hospitals.py
"""

import json
import time
import math
import requests
from typing import Optional

# Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Files
RESORTS_FILE = "public/resorts.json"
OUTPUT_FILE = "public/hospitals.json"

# Maximum distance from any ski resort (miles)
MAX_DISTANCE_MILES = 100

# States with ski resorts (we'll only query hospitals in these states)
SKI_STATES = [
    "CA", "CO", "UT", "WY", "MT", "ID", "NM", "AZ", "NV",  # West/Rockies
    "WA", "OR",  # Pacific NW
    "VT", "NH", "ME", "NY", "PA", "MA", "CT", "NJ",  # Northeast
    "MI", "WI", "MN", "OH", "IN", "MO",  # Midwest
    "WV", "VA", "NC", "TN",  # Southeast
]

def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in miles."""
    r = 3958.8  # Earth's radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

def load_resorts() -> list:
    """Load existing resort data."""
    try:
        with open(RESORTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {RESORTS_FILE} not found")
        return []

def fetch_hospitals_for_state(state: str) -> list:
    """Fetch hospitals from OSM for a specific state."""
    # Build Overpass query for hospitals in this state
    query = f"""
    [out:json][timeout:60];
    area["name"~"{get_state_name(state)}"]["admin_level"="4"]->.state;
    (
      nwr["amenity"="hospital"]["name"](area.state);
    );
    out center tags;
    """
    
    try:
        resp = requests.post(
            OVERPASS_URL,
            data={"data": query},
            headers={"User-Agent": "SkiWithCare/2.0 (github.com/ct3685/skiwithcare)"},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("elements", [])
    except requests.RequestException as e:
        print(f"    Error fetching {state}: {e}")
        return []

def get_state_name(abbrev: str) -> str:
    """Convert state abbreviation to full name for OSM query."""
    names = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
        "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
        "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming",
    }
    return names.get(abbrev, abbrev)

def process_hospital(el: dict, state: str, resorts: list) -> Optional[dict]:
    """Process an OSM element into a hospital record."""
    tags = el.get("tags", {})
    name = tags.get("name")
    
    if not name:
        return None
    
    # Get coordinates
    if el.get("type") == "node":
        lat = el.get("lat")
        lon = el.get("lon")
    else:
        center = el.get("center", {})
        lat = center.get("lat")
        lon = center.get("lon")
    
    if not lat or not lon:
        return None
    
    # Find nearest resort and distance
    min_dist = float("inf")
    nearest_resort = None
    
    for resort in resorts:
        dist = haversine_miles(lat, lon, resort["lat"], resort["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest_resort = resort["name"]
    
    # Skip if too far from any resort
    if min_dist > MAX_DISTANCE_MILES:
        return None
    
    # Check for emergency room
    has_emergency = tags.get("emergency") == "yes" or "emergency" in name.lower()
    
    # Build address
    address = tags.get("addr:street", "")
    if tags.get("addr:housenumber"):
        address = f"{tags['addr:housenumber']} {address}"
    
    city = tags.get("addr:city", "")
    zip_code = tags.get("addr:postcode", "")
    phone = tags.get("phone", tags.get("contact:phone", ""))
    
    return {
        "id": f"osm-{el.get('id')}",
        "name": name,
        "address": address.strip(),
        "city": city,
        "state": state,
        "zip": zip_code,
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "hasEmergency": has_emergency,
        "phone": phone if phone else None,
        "nearestResort": nearest_resort,
        "nearestResortDist": round(min_dist, 1),
    }

def main():
    """Main execution."""
    print("=" * 60)
    print("SkiWithCare - OSM Hospital Data Fetcher")
    print("=" * 60)
    
    # Load resort data for distance calculations
    resorts = load_resorts()
    if not resorts:
        print("ERROR: No resort data found. Run fetch_osm_resorts.py first.")
        return
    
    print(f"Loaded {len(resorts)} resorts for distance filtering")
    
    # Fetch hospitals for each ski state
    hospitals = []
    seen_ids = set()
    
    for state in SKI_STATES:
        print(f"\nFetching hospitals in {state}...")
        time.sleep(2)  # Rate limiting between states
        
        elements = fetch_hospitals_for_state(state)
        print(f"  Found {len(elements)} hospitals in OSM")
        
        for el in elements:
            hospital = process_hospital(el, state, resorts)
            if hospital and hospital["id"] not in seen_ids:
                hospitals.append(hospital)
                seen_ids.add(hospital["id"])
                print(f"  ✓ {hospital['name']} ({hospital['nearestResortDist']} mi from {hospital['nearestResort']})")
    
    # Sort by state, then name
    hospitals.sort(key=lambda h: (h["state"], h["name"]))
    
    # Write output
    print(f"\nWriting {len(hospitals)} hospitals to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(hospitals, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"SUCCESS: {len(hospitals)} hospitals within {MAX_DISTANCE_MILES} miles of ski resorts")
    
    er_count = sum(1 for h in hospitals if h.get("hasEmergency"))
    print(f"  With Emergency Room: {er_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()

