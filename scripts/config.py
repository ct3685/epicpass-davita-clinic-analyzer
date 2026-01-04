"""
SkiWithCare Data Configuration
==============================

Resort lists for Epic Pass and Ikon Pass networks.
"""

# Pass network constants
PASS_EPIC = "epic"
PASS_IKON = "ikon"
PASS_BOTH = "both"
PASS_INDEPENDENT = "independent"

# Region constants
REGION_ROCKIES = "rockies"
REGION_WEST = "west"
REGION_NORTHEAST = "northeast"
REGION_MIDWEST = "midwest"
REGION_SOUTHEAST = "southeast"
REGION_PACIFIC_NW = "pacific-northwest"

# Epic Pass US Resorts (Owned/Operated + US Partners)
# Source: https://www.epicpass.com/
EPIC_RESORTS = [
    # === ROCKIES ===
    {"name": "Vail", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Beaver Creek", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Breckenridge", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Park City", "state": "UT", "region": REGION_ROCKIES},
    {"name": "Keystone", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Crested Butte", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Telluride Ski Resort", "state": "CO", "region": REGION_ROCKIES},

    # === WEST ===
    {"name": "Heavenly", "state": "CA/NV", "region": REGION_WEST},
    {"name": "Northstar", "state": "CA", "region": REGION_WEST},
    {"name": "Kirkwood", "state": "CA", "region": REGION_WEST},
    {"name": "Stevens Pass", "state": "WA", "region": REGION_PACIFIC_NW},

    # === NORTHEAST ===
    {"name": "Stowe", "state": "VT", "region": REGION_NORTHEAST},
    {"name": "Okemo", "state": "VT", "region": REGION_NORTHEAST},
    {"name": "Mount Snow", "state": "VT", "region": REGION_NORTHEAST},
    {"name": "Hunter", "state": "NY", "region": REGION_NORTHEAST},
    {"name": "Attitash", "state": "NH", "region": REGION_NORTHEAST},
    {"name": "Wildcat", "state": "NH", "region": REGION_NORTHEAST},
    {"name": "Mount Sunapee", "state": "NH", "region": REGION_NORTHEAST},
    {"name": "Crotched", "state": "NH", "region": REGION_NORTHEAST},

    # === MID-ATLANTIC ===
    {"name": "Liberty Mountain", "state": "PA", "region": REGION_NORTHEAST},
    {"name": "Roundtop", "state": "PA", "region": REGION_NORTHEAST},
    {"name": "Whitetail", "state": "PA", "region": REGION_NORTHEAST},
    {"name": "Jack Frost", "state": "PA", "region": REGION_NORTHEAST},
    {"name": "Big Boulder", "state": "PA", "region": REGION_NORTHEAST},
    {"name": "Seven Springs", "state": "PA", "region": REGION_NORTHEAST},
    {"name": "Hidden Valley Resort", "state": "PA", "region": REGION_NORTHEAST},
    {"name": "Laurel Mountain", "state": "PA", "region": REGION_NORTHEAST},

    # === MIDWEST ===
    {"name": "Wilmot Mountain", "state": "WI", "region": REGION_MIDWEST},
    {"name": "Afton Alps", "state": "MN", "region": REGION_MIDWEST},
    {"name": "Mt Brighton", "state": "MI", "region": REGION_MIDWEST},
    {"name": "Alpine Valley", "state": "OH", "region": REGION_MIDWEST},
    {"name": "Boston Mills", "state": "OH", "region": REGION_MIDWEST},
    {"name": "Brandywine", "state": "OH", "region": REGION_MIDWEST},
    {"name": "Mad River Mountain", "state": "OH", "region": REGION_MIDWEST},
    {"name": "Hidden Valley", "state": "MO", "region": REGION_MIDWEST},
    {"name": "Snow Creek", "state": "MO", "region": REGION_MIDWEST},
    {"name": "Paoli Peaks", "state": "IN", "region": REGION_MIDWEST},
]

# Ikon Pass US Resorts
# Source: https://www.ikonpass.com/
IKON_RESORTS = [
    # === ROCKIES ===
    {"name": "Aspen Snowmass", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Steamboat", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Winter Park", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Copper Mountain", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Eldora", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Arapahoe Basin", "state": "CO", "region": REGION_ROCKIES},
    {"name": "Snowbird", "state": "UT", "region": REGION_ROCKIES},
    {"name": "Alta", "state": "UT", "region": REGION_ROCKIES},
    {"name": "Brighton", "state": "UT", "region": REGION_ROCKIES},
    {"name": "Solitude", "state": "UT", "region": REGION_ROCKIES},
    {"name": "Deer Valley", "state": "UT", "region": REGION_ROCKIES},
    {"name": "Jackson Hole", "state": "WY", "region": REGION_ROCKIES},
    {"name": "Big Sky", "state": "MT", "region": REGION_ROCKIES},
    {"name": "Taos Ski Valley", "state": "NM", "region": REGION_ROCKIES},

    # === WEST ===
    {"name": "Mammoth Mountain", "state": "CA", "region": REGION_WEST},
    {"name": "June Mountain", "state": "CA", "region": REGION_WEST},
    {"name": "Big Bear Mountain", "state": "CA", "region": REGION_WEST},
    {"name": "Squaw Valley Alpine Meadows", "state": "CA", "region": REGION_WEST},
    {"name": "Mt Bachelor", "state": "OR", "region": REGION_PACIFIC_NW},
    {"name": "Crystal Mountain", "state": "WA", "region": REGION_PACIFIC_NW},
    {"name": "The Summit at Snoqualmie", "state": "WA", "region": REGION_PACIFIC_NW},
    {"name": "Sun Valley", "state": "ID", "region": REGION_WEST},
    {"name": "Schweitzer", "state": "ID", "region": REGION_PACIFIC_NW},

    # === NORTHEAST ===
    {"name": "Killington", "state": "VT", "region": REGION_NORTHEAST},
    {"name": "Pico Mountain", "state": "VT", "region": REGION_NORTHEAST},
    {"name": "Sugarbush", "state": "VT", "region": REGION_NORTHEAST},
    {"name": "Stratton", "state": "VT", "region": REGION_NORTHEAST},
    {"name": "Sunday River", "state": "ME", "region": REGION_NORTHEAST},
    {"name": "Sugarloaf", "state": "ME", "region": REGION_NORTHEAST},
    {"name": "Loon Mountain", "state": "NH", "region": REGION_NORTHEAST},
    {"name": "Tremblant", "state": "QC", "region": REGION_NORTHEAST},  # Canada but close to US
    {"name": "Blue Mountain", "state": "ON", "region": REGION_NORTHEAST},  # Canada

    # === MIDWEST ===
    {"name": "Boyne Highlands", "state": "MI", "region": REGION_MIDWEST},
    {"name": "Boyne Mountain", "state": "MI", "region": REGION_MIDWEST},

    # === SOUTHEAST ===
    {"name": "Snowshoe", "state": "WV", "region": REGION_SOUTHEAST},
]

# Resorts on BOTH passes
BOTH_PASS_RESORTS = [
    # None currently - but could add if any exist
]


def get_all_resorts():
    """Get all resorts with pass network assigned."""
    resorts = []
    
    # Add Epic resorts
    for r in EPIC_RESORTS:
        resorts.append({**r, "passNetwork": PASS_EPIC})
    
    # Add Ikon resorts
    for r in IKON_RESORTS:
        resorts.append({**r, "passNetwork": PASS_IKON})
    
    # Add dual-pass resorts
    for r in BOTH_PASS_RESORTS:
        resorts.append({**r, "passNetwork": PASS_BOTH})
    
    return resorts


# Provider chain mappings for dialysis facilities
PROVIDER_CHAINS = {
    "DAVITA": "davita",
    "FRESENIUS": "fresenius",
    "FMC": "fresenius",  # Fresenius Medical Care
    "DIALYSIS CLINIC": "independent",
}


def classify_provider(chain_name: str) -> str:
    """Classify a dialysis provider chain."""
    if not chain_name:
        return "other"
    
    upper = chain_name.upper()
    for key, value in PROVIDER_CHAINS.items():
        if key in upper:
            return value
    
    return "other"

