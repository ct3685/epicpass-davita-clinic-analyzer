#!/usr/bin/env python3
"""
Fetch Ski Resort Data from OpenStreetMap
=========================================

Queries the OSM Overpass API for ski resorts in the United States,
enriches with Epic/Ikon pass network data, and outputs to public/resorts.json.

Rate Limiting:
- Overpass API is free but requests should be spaced out
- This script is designed to run weekly via GitHub Actions
- Manual runs should be infrequent

Usage:
    python scripts/fetch_osm_resorts.py
"""

import json
import time
import requests
from typing import Optional

# Overpass API endpoint (public, free, no API key)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Output file
OUTPUT_FILE = "public/resorts.json"

# Overpass query for ski resorts in the United States
# Queries for: landuse=winter_sports, sport=skiing, and piste:type areas
OVERPASS_QUERY = """
[out:json][timeout:120];
area["name"="United States"]["admin_level"="2"]->.usa;
(
  // Ski areas marked as winter_sports
  nwr["landuse"="winter_sports"](area.usa);
  // Ski resorts
  nwr["sport"="skiing"]["name"](area.usa);
  // Downhill ski areas
  nwr["piste:type"="downhill"]["name"](area.usa);
  // Leisure ski resorts
  nwr["leisure"="ski_resort"](area.usa);
);
out center tags;
"""

# Epic Pass resorts (name patterns for matching)
# Source: https://www.epicpass.com/
EPIC_RESORTS = {
    # Vail Resorts owned
    "vail", "beaver creek", "breckenridge", "keystone", "crested butte",
    "park city", "heavenly", "northstar", "kirkwood", "stevens pass",
    "stowe", "okemo", "mount snow", "hunter mountain", "attitash",
    "wildcat", "mount sunapee", "crotched mountain",
    # Mid-Atlantic
    "liberty mountain", "roundtop", "whitetail", "jack frost", "big boulder",
    "seven springs", "hidden valley", "laurel mountain",
    # Midwest
    "wilmot", "afton alps", "mt brighton", "alpine valley", "boston mills",
    "brandywine", "mad river mountain", "snow creek", "paoli peaks",
    # Partners
    "telluride",
}

# Ikon Pass resorts (name patterns for matching)
# Source: https://www.ikonpass.com/
IKON_RESORTS = {
    # Full access
    "aspen", "snowmass", "steamboat", "winter park", "copper mountain",
    "eldora", "jackson hole", "big sky", "alta", "snowbird",
    "deer valley", "brighton", "solitude", "taos",
    # Tahoe
    "palisades tahoe", "squaw valley", "alpine meadows", "mammoth",
    "june mountain", "big bear", "snow valley",
    # Pacific Northwest  
    "crystal mountain", "snoqualmie", "schweitzer",
    # Northeast
    "stratton", "sugarbush", "killington", "pico", "sunday river",
    "sugarloaf", "loon mountain", "windham",
    # Midwest
    "boyne highlands", "boyne mountain",
    # Southeast
    "snowshoe",
}

def get_region(state: str, lat: float, lon: float) -> str:
    """Determine geographic region based on state and coordinates."""
    northeast = {"ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"}
    southeast = {"WV", "VA", "NC", "TN", "GA"}
    midwest = {"OH", "MI", "IN", "IL", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"}
    rockies = {"CO", "UT", "WY", "MT", "ID", "NM"}
    west = {"CA", "NV", "AZ"}
    pacific_nw = {"WA", "OR"}
    
    if state in northeast:
        return "northeast"
    elif state in southeast:
        return "southeast"
    elif state in midwest:
        return "midwest"
    elif state in rockies:
        return "rockies"
    elif state in west:
        return "west"
    elif state in pacific_nw:
        return "pacific-northwest"
    else:
        # Default based on longitude
        if lon < -115:
            return "west"
        elif lon < -100:
            return "rockies"
        else:
            return "midwest"

def get_pass_network(name: str) -> str:
    """Determine pass network affiliation based on resort name."""
    name_lower = name.lower()
    
    is_epic = any(epic in name_lower for epic in EPIC_RESORTS)
    is_ikon = any(ikon in name_lower for ikon in IKON_RESORTS)
    
    if is_epic and is_ikon:
        return "both"
    elif is_epic:
        return "epic"
    elif is_ikon:
        return "ikon"
    else:
        return "independent"

def get_state_from_coords(lat: float, lon: float) -> Optional[str]:
    """
    Reverse geocode to get state from coordinates.
    Uses Nominatim with proper rate limiting.
    """
    try:
        time.sleep(1.1)  # Nominatim rate limit: 1 req/sec
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 5,  # State level
        }
        headers = {"User-Agent": "SkiWithCare/2.0 (github.com/ct3685/skiwithcare)"}
        
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        address = data.get("address", {})
        state = address.get("state")
        
        if state:
            # Convert state name to abbreviation
            return STATE_ABBREVS.get(state.upper(), state[:2].upper())
        
        return None
    except Exception as e:
        print(f"  Warning: Could not reverse geocode ({lat}, {lon}): {e}")
        return None

# State name to abbreviation mapping
STATE_ABBREVS = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
    "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE",
    "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID",
    "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS",
    "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD",
    "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS",
    "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY",
    "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
    "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT",
    "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI", "WYOMING": "WY",
}

def fetch_osm_resorts() -> list:
    """Fetch ski resorts from OSM Overpass API."""
    print("Fetching ski resorts from OpenStreetMap Overpass API...")
    print(f"  Endpoint: {OVERPASS_URL}")
    
    try:
        resp = requests.post(
            OVERPASS_URL,
            data={"data": OVERPASS_QUERY},
            headers={"User-Agent": "SkiWithCare/2.0 (github.com/ct3685/skiwithcare)"},
            timeout=180,
        )
        resp.raise_for_status()
        data = resp.json()
        
        elements = data.get("elements", [])
        print(f"  Found {len(elements)} elements from OSM")
        
        return elements
    except requests.RequestException as e:
        print(f"  ERROR: Failed to fetch from Overpass API: {e}")
        return []

def process_resorts(elements: list) -> list:
    """Process OSM elements into resort records."""
    print("Processing resort data...")
    
    resorts = []
    seen_names = set()
    
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        
        if not name:
            continue
        
        # Skip duplicates
        name_key = name.lower().strip()
        if name_key in seen_names:
            continue
        seen_names.add(name_key)
        
        # Get coordinates (center for ways/relations)
        if el.get("type") == "node":
            lat = el.get("lat")
            lon = el.get("lon")
        else:
            center = el.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")
        
        if not lat or not lon:
            continue
        
        # Filter to continental US bounds
        if not (24.0 < lat < 50.0 and -125.0 < lon < -66.0):
            continue
        
        # Get state from tags or reverse geocode
        state = tags.get("addr:state")
        if not state:
            state = get_state_from_coords(lat, lon)
        if not state:
            print(f"  Skipping {name} - could not determine state")
            continue
        
        # Determine pass network and region
        pass_network = get_pass_network(name)
        region = get_region(state, lat, lon)
        
        resort = {
            "id": f"{name}|{state}",
            "name": name,
            "state": state,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "passNetwork": pass_network,
            "region": region,
        }
        
        resorts.append(resort)
        print(f"  ✓ {name}, {state} ({pass_network})")
    
    return resorts

def main():
    """Main execution."""
    print("=" * 60)
    print("SkiWithCare - OSM Resort Data Fetcher")
    print("=" * 60)
    
    # Fetch from OSM
    elements = fetch_osm_resorts()
    
    if not elements:
        print("No data fetched, exiting.")
        return
    
    # Process into resort records
    resorts = process_resorts(elements)
    
    # Sort by name
    resorts.sort(key=lambda r: r["name"])
    
    # Write output
    print(f"\nWriting {len(resorts)} resorts to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(resorts, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"SUCCESS: {len(resorts)} resorts written to {OUTPUT_FILE}")
    
    epic_count = sum(1 for r in resorts if r["passNetwork"] in ("epic", "both"))
    ikon_count = sum(1 for r in resorts if r["passNetwork"] in ("ikon", "both"))
    indie_count = sum(1 for r in resorts if r["passNetwork"] == "independent")
    
    print(f"  Epic Pass: {epic_count}")
    print(f"  Ikon Pass: {ikon_count}")
    print(f"  Independent: {indie_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()

