#!/usr/bin/env python3
"""
Build Resort Data from Hardcoded Lists + Geocode Cache
=======================================================

Uses our Epic/Ikon resort lists and cached coordinates.
NO NETWORK CALLS - runs instantly.

Usage:
    python scripts/build_resorts.py
"""

import json

CACHE_FILE = "resort_geocoded_cache.json"
OUTPUT_FILE = "public/resorts.json"

# Epic Pass US Resorts (name, state, region)
EPIC_RESORTS = [
    ("Vail", "CO", "rockies"),
    ("Beaver Creek", "CO", "rockies"),
    ("Breckenridge", "CO", "rockies"),
    ("Park City", "UT", "rockies"),
    ("Keystone", "CO", "rockies"),
    ("Crested Butte", "CO", "rockies"),
    ("Heavenly", "CA/NV", "west"),
    ("Northstar", "CA", "west"),
    ("Kirkwood", "CA", "west"),
    ("Stevens Pass", "WA", "pacific-northwest"),
    ("Stowe", "VT", "northeast"),
    ("Okemo", "VT", "northeast"),
    ("Mount Snow", "VT", "northeast"),
    ("Hunter", "NY", "northeast"),
    ("Attitash", "NH", "northeast"),
    ("Wildcat", "NH", "northeast"),
    ("Mount Sunapee", "NH", "northeast"),
    ("Crotched", "NH", "northeast"),
    ("Liberty Mountain", "PA", "northeast"),
    ("Roundtop", "PA", "northeast"),
    ("Whitetail", "PA", "northeast"),
    ("Jack Frost", "PA", "northeast"),
    ("Big Boulder", "PA", "northeast"),
    ("Seven Springs", "PA", "northeast"),
    ("Hidden Valley Resort", "PA", "northeast"),
    ("Laurel Mountain", "PA", "northeast"),
    ("Wilmot Mountain", "WI", "midwest"),
    ("Afton Alps", "MN", "midwest"),
    ("Mt Brighton", "MI", "midwest"),
    ("Alpine Valley", "OH", "midwest"),
    ("Boston Mills", "OH", "midwest"),
    ("Brandywine", "OH", "midwest"),
    ("Mad River Mountain", "OH", "midwest"),
    ("Hidden Valley", "MO", "midwest"),
    ("Snow Creek", "MO", "midwest"),
    ("Paoli Peaks", "IN", "midwest"),
    ("Telluride Ski Resort", "CO", "rockies"),
]

# Ikon Pass US Resorts (name, state, region)
IKON_RESORTS = [
    ("Aspen Snowmass", "CO", "rockies"),
    ("Steamboat", "CO", "rockies"),
    ("Winter Park", "CO", "rockies"),
    ("Copper Mountain", "CO", "rockies"),
    ("Eldora Mountain Resort", "CO", "rockies"),
    ("Jackson Hole", "WY", "rockies"),
    ("Big Sky", "MT", "rockies"),
    ("Alta", "UT", "rockies"),
    ("Snowbird", "UT", "rockies"),
    ("Deer Valley", "UT", "rockies"),
    ("Brighton", "UT", "rockies"),
    ("Solitude", "UT", "rockies"),
    ("Taos Ski Valley", "NM", "rockies"),
    ("Palisades Tahoe", "CA", "west"),
    ("Mammoth Mountain", "CA", "west"),
    ("June Mountain", "CA", "west"),
    ("Big Bear Mountain Resort", "CA", "west"),
    ("Snow Valley", "CA", "west"),
    ("Crystal Mountain", "WA", "pacific-northwest"),
    ("Summit at Snoqualmie", "WA", "pacific-northwest"),
    ("Schweitzer", "ID", "pacific-northwest"),
    ("Stratton", "VT", "northeast"),
    ("Sugarbush", "VT", "northeast"),
    ("Killington", "VT", "northeast"),
    ("Sunday River", "ME", "northeast"),
    ("Sugarloaf", "ME", "northeast"),
    ("Loon Mountain", "NH", "northeast"),
    ("Windham Mountain", "NY", "northeast"),
    ("Boyne Highlands", "MI", "midwest"),
    ("Boyne Mountain", "MI", "midwest"),
    ("Snowshoe", "WV", "southeast"),
    ("Blue Mountain", "PA", "northeast"),
]

def main():
    print("=" * 50)
    print("Building resort data from cache")
    print("=" * 50)
    
    # Load geocode cache
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} cached coordinates")
    except FileNotFoundError:
        print(f"ERROR: {CACHE_FILE} not found")
        print("Run the original data generator first to build the cache")
        return
    
    resorts = []
    missing = []
    
    # Process Epic resorts
    print("\nEpic Pass resorts:")
    for name, state, region in EPIC_RESORTS:
        key = f"{name}|{state}"
        if key in cache and cache[key].get("lat"):
            resort = {
                "id": key,
                "name": name,
                "state": state,
                "lat": round(cache[key]["lat"], 6),
                "lon": round(cache[key]["lon"], 6),
                "passNetwork": "epic",
                "region": region,
            }
            resorts.append(resort)
            print(f"  ✓ {name}, {state}")
        else:
            missing.append((name, state, "epic"))
            print(f"  ✗ {name}, {state} (no coords)")
    
    # Process Ikon resorts
    print("\nIkon Pass resorts:")
    for name, state, region in IKON_RESORTS:
        key = f"{name}|{state}"
        
        # Check if already added (some resorts are on both passes)
        existing = next((r for r in resorts if r["id"] == key), None)
        if existing:
            existing["passNetwork"] = "both"
            print(f"  ⚡ {name}, {state} (both passes)")
            continue
        
        if key in cache and cache[key].get("lat"):
            resort = {
                "id": key,
                "name": name,
                "state": state,
                "lat": round(cache[key]["lat"], 6),
                "lon": round(cache[key]["lon"], 6),
                "passNetwork": "ikon",
                "region": region,
            }
            resorts.append(resort)
            print(f"  ✓ {name}, {state}")
        else:
            missing.append((name, state, "ikon"))
            print(f"  ✗ {name}, {state} (no coords)")
    
    # Sort by name
    resorts.sort(key=lambda r: r["name"])
    
    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(resorts, f, indent=2)
    
    # Summary
    epic = sum(1 for r in resorts if r["passNetwork"] == "epic")
    ikon = sum(1 for r in resorts if r["passNetwork"] == "ikon")
    both = sum(1 for r in resorts if r["passNetwork"] == "both")
    
    print("\n" + "=" * 50)
    print(f"Saved {len(resorts)} resorts to {OUTPUT_FILE}")
    print(f"  Epic: {epic} | Ikon: {ikon} | Both: {both}")
    
    if missing:
        print(f"\n⚠️  {len(missing)} resorts missing coordinates:")
        for name, state, network in missing:
            print(f"    - {name}, {state} ({network})")
        print("\nRun `npm run data:generate` to geocode missing resorts")
    
    print("=" * 50)

if __name__ == "__main__":
    main()

