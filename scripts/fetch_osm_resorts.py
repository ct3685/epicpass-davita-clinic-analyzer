#!/usr/bin/env python3
"""
Fetch Ski Resort Data from OpenStreetMap
=========================================

Queries the OSM Overpass API STATE BY STATE for ski resorts,
then enriches with Epic/Ikon pass network data.

Usage:
    python scripts/fetch_osm_resorts.py
"""

import json
import time
import requests
from typing import Optional, List

# Overpass API endpoints (multiple mirrors for reliability)
OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

# Output file
OUTPUT_FILE = "public/resorts.json"

# States with ski resorts to query
SKI_STATES = [
    # West / Rockies
    "California", "Colorado", "Utah", "Wyoming", "Montana", "Idaho", 
    "New Mexico", "Arizona", "Nevada",
    # Pacific Northwest
    "Washington", "Oregon",
    # Northeast
    "Vermont", "New Hampshire", "Maine", "New York", "Pennsylvania", 
    "Massachusetts", "Connecticut", "New Jersey",
    # Midwest
    "Michigan", "Wisconsin", "Minnesota", "Ohio", "Indiana", "Missouri",
    # Southeast
    "West Virginia", "Virginia", "North Carolina", "Tennessee",
]

# State name to abbreviation
STATE_ABBREVS = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}

# Epic Pass resorts (for tagging)
EPIC_RESORTS = {
    "vail", "beaver creek", "breckenridge", "keystone", "crested butte",
    "park city", "heavenly", "northstar", "kirkwood", "stevens pass",
    "stowe", "okemo", "mount snow", "hunter mountain", "attitash",
    "wildcat", "mount sunapee", "crotched",
    "liberty mountain", "roundtop", "whitetail", "jack frost", "big boulder",
    "seven springs", "hidden valley", "laurel mountain",
    "wilmot", "afton alps", "mt brighton", "alpine valley", "boston mills",
    "brandywine", "mad river mountain", "snow creek", "paoli peaks",
    "telluride",
}

# Ikon Pass resorts (for tagging)
IKON_RESORTS = {
    "aspen", "snowmass", "steamboat", "winter park", "copper mountain",
    "eldora", "jackson hole", "big sky", "alta", "snowbird",
    "deer valley", "brighton", "solitude", "taos",
    "palisades tahoe", "squaw valley", "alpine meadows", "mammoth",
    "june mountain", "big bear", "snow valley",
    "crystal mountain", "snoqualmie", "schweitzer",
    "stratton", "sugarbush", "killington", "pico", "sunday river",
    "sugarloaf", "loon mountain", "windham",
    "boyne highlands", "boyne mountain",
    "snowshoe",
}


def get_region(state_abbrev: str) -> str:
    """Determine geographic region based on state."""
    northeast = {"ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"}
    southeast = {"WV", "VA", "NC", "TN", "GA"}
    midwest = {"OH", "MI", "IN", "IL", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"}
    rockies = {"CO", "UT", "WY", "MT", "ID", "NM"}
    west = {"CA", "NV", "AZ"}
    pacific_nw = {"WA", "OR"}
    
    if state_abbrev in northeast:
        return "northeast"
    elif state_abbrev in southeast:
        return "southeast"
    elif state_abbrev in midwest:
        return "midwest"
    elif state_abbrev in rockies:
        return "rockies"
    elif state_abbrev in west:
        return "west"
    elif state_abbrev in pacific_nw:
        return "pacific-northwest"
    return "other"


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
    return "independent"


def fetch_resorts_for_state(state_name: str) -> List[dict]:
    """Fetch ski resorts from OSM for a specific state."""
    query = f"""
    [out:json][timeout:30];
    area["name"="{state_name}"]["admin_level"="4"]->.state;
    (
      nwr["landuse"="winter_sports"]["name"](area.state);
      nwr["sport"="skiing"]["name"](area.state);
      nwr["piste:type"="downhill"]["name"](area.state);
      nwr["leisure"="ski_resort"]["name"](area.state);
    );
    out center tags;
    """
    
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            resp = requests.post(
                endpoint,
                data={"data": query},
                headers={"User-Agent": "SkiWithCare/2.0"},
                timeout=45,
            )
            resp.raise_for_status()
            return resp.json().get("elements", [])
        except requests.RequestException as e:
            continue  # Try next endpoint
    
    print("(timeout) ", end="", flush=True)
    return []


def process_element(el: dict, state_name: str) -> Optional[dict]:
    """Process an OSM element into a resort record."""
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
    
    state_abbrev = STATE_ABBREVS.get(state_name, state_name[:2].upper())
    pass_network = get_pass_network(name)
    region = get_region(state_abbrev)
    
    return {
        "id": f"{name}|{state_abbrev}",
        "name": name,
        "state": state_abbrev,
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "passNetwork": pass_network,
        "region": region,
    }


def main():
    """Main execution."""
    import sys
    
    print("=" * 60, flush=True)
    print("SkiWithCare - OSM Resort Data Fetcher", flush=True)
    print("=" * 60, flush=True)
    print(f"Querying {len(SKI_STATES)} states individually...\n", flush=True)
    
    all_resorts = []
    seen_names = set()
    
    for i, state in enumerate(SKI_STATES, 1):
        print(f"[{i}/{len(SKI_STATES)}] {state}... ", end="", flush=True)
        sys.stdout.flush()
        
        elements = fetch_resorts_for_state(state)
        count = 0
        
        for el in elements:
            resort = process_element(el, state)
            if resort:
                # Deduplicate by name
                name_key = resort["name"].lower().strip()
                if name_key not in seen_names:
                    seen_names.add(name_key)
                    all_resorts.append(resort)
                    count += 1
        
        print(f"✓ {count} resorts", flush=True)
        time.sleep(1)  # Rate limiting between states
    
    # Sort by name
    all_resorts.sort(key=lambda r: r["name"])
    
    # Write output
    print(f"\nWriting {len(all_resorts)} resorts to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_resorts, f, indent=2)
    
    # Summary by pass network
    epic_count = sum(1 for r in all_resorts if r["passNetwork"] == "epic")
    ikon_count = sum(1 for r in all_resorts if r["passNetwork"] == "ikon")
    both_count = sum(1 for r in all_resorts if r["passNetwork"] == "both")
    indie_count = sum(1 for r in all_resorts if r["passNetwork"] == "independent")
    
    print("\n" + "=" * 60)
    print(f"SUCCESS: {len(all_resorts)} total resorts")
    print(f"  Epic Pass: {epic_count}")
    print(f"  Ikon Pass: {ikon_count}")
    print(f"  Both: {both_count}")
    print(f"  Independent: {indie_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
