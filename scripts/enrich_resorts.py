#!/usr/bin/env python3
"""
Enrich Resort Data with Pass Network Info
==========================================

Reads existing resorts.json and adds passNetwork/region fields.
No external API calls - just enriches existing data.

Usage:
    python scripts/enrich_resorts.py
"""

import json

INPUT_FILE = "public/resorts.json"
OUTPUT_FILE = "public/resorts.json"

# Epic Pass resorts (lowercase for matching)
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

# Ikon Pass resorts (lowercase for matching)
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

def get_pass_network(name: str) -> str:
    """Determine pass network affiliation."""
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

def get_region(state: str) -> str:
    """Determine region from state."""
    regions = {
        "northeast": ["ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"],
        "southeast": ["WV", "VA", "NC", "TN", "GA"],
        "midwest": ["OH", "MI", "IN", "IL", "WI", "MN", "IA", "MO"],
        "rockies": ["CO", "UT", "WY", "MT", "ID", "NM"],
        "west": ["CA", "NV", "AZ", "CA/NV"],
        "pacific-northwest": ["WA", "OR"],
    }
    for region, states in regions.items():
        if state in states:
            return region
    return "other"

def main():
    print("=" * 50)
    print("Enriching resort data with pass network info")
    print("=" * 50)
    
    # Load existing data
    with open(INPUT_FILE, "r") as f:
        resorts = json.load(f)
    
    print(f"Loaded {len(resorts)} resorts")
    
    # Enrich each resort
    for resort in resorts:
        name = resort.get("name", "")
        state = resort.get("state", "")
        
        # Add ID if missing
        if "id" not in resort:
            resort["id"] = f"{name}|{state}"
        
        # Add passNetwork
        resort["passNetwork"] = get_pass_network(name)
        
        # Add region
        resort["region"] = get_region(state)
        
        print(f"  {name}: {resort['passNetwork']}")
    
    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(resorts, f, indent=2)
    
    # Summary
    epic = sum(1 for r in resorts if r["passNetwork"] == "epic")
    ikon = sum(1 for r in resorts if r["passNetwork"] == "ikon")
    both = sum(1 for r in resorts if r["passNetwork"] == "both")
    indie = sum(1 for r in resorts if r["passNetwork"] == "independent")
    
    print("\n" + "=" * 50)
    print(f"Done! Saved to {OUTPUT_FILE}")
    print(f"  Epic: {epic} | Ikon: {ikon} | Both: {both} | Independent: {indie}")
    print("=" * 50)

if __name__ == "__main__":
    main()

