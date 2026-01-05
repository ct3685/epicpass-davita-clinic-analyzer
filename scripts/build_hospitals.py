#!/usr/bin/env python3
"""
Build Hospital Data - Major hospitals near ski resorts
=======================================================

Hardcoded list of major hospitals/medical centers near ski areas.
NO NETWORK CALLS - runs instantly.

Usage:
    python scripts/build_hospitals.py
"""

import json
import math

RESORTS_FILE = "public/resorts.json"
OUTPUT_FILE = "public/hospitals.json"

def haversine_miles(lat1, lon1, lat2, lon2):
    r = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

# Major hospitals near ski areas (name, city, state, lat, lon, hasEmergency)
HOSPITALS = [
    # COLORADO
    ("Vail Health Hospital", "Vail", "CO", 39.6403, -106.3742, True),
    ("UCHealth Yampa Valley Medical Center", "Steamboat Springs", "CO", 40.4850, -106.8317, True),
    ("St. Anthony Summit Medical Center", "Frisco", "CO", 39.5753, -106.0975, True),
    ("Aspen Valley Hospital", "Aspen", "CO", 39.1911, -106.8175, True),
    ("UCHealth Poudre Valley Hospital", "Fort Collins", "CO", 40.5608, -105.0842, True),
    ("St. Mary's Medical Center", "Grand Junction", "CO", 39.0639, -108.5506, True),
    ("UCHealth Memorial Hospital", "Colorado Springs", "CO", 38.8581, -104.8214, True),
    ("Boulder Community Health", "Boulder", "CO", 40.0274, -105.2453, True),
    
    # UTAH
    ("Park City Hospital", "Park City", "UT", 40.6461, -111.4980, True),
    ("University of Utah Hospital", "Salt Lake City", "UT", 40.7720, -111.8394, True),
    ("Intermountain Medical Center", "Murray", "UT", 40.6570, -111.8950, True),
    ("LDS Hospital", "Salt Lake City", "UT", 40.7778, -111.8800, True),
    
    # CALIFORNIA / TAHOE
    ("Barton Memorial Hospital", "South Lake Tahoe", "CA", 38.9394, -119.9772, True),
    ("Tahoe Forest Hospital", "Truckee", "CA", 39.3289, -120.1836, True),
    ("Mammoth Hospital", "Mammoth Lakes", "CA", 37.6489, -118.9625, True),
    ("Bear Valley Community Hospital", "Big Bear Lake", "CA", 34.2439, -116.9114, True),
    
    # WYOMING
    ("St. John's Medical Center", "Jackson", "WY", 43.4750, -110.7631, True),
    
    # MONTANA
    ("Bozeman Health Deaconess Hospital", "Bozeman", "MT", 45.6770, -111.0429, True),
    ("Big Sky Medical Center", "Big Sky", "MT", 45.2636, -111.3103, True),
    
    # VERMONT
    ("University of Vermont Medical Center", "Burlington", "VT", 44.4759, -73.1953, True),
    ("Rutland Regional Medical Center", "Rutland", "VT", 43.6106, -72.9726, True),
    ("Southwestern Vermont Medical Center", "Bennington", "VT", 42.8781, -73.1968, True),
    ("Copley Hospital", "Morrisville", "VT", 44.5581, -72.5981, True),
    
    # NEW HAMPSHIRE
    ("Dartmouth-Hitchcock Medical Center", "Lebanon", "NH", 43.6364, -72.2873, True),
    ("Memorial Hospital", "North Conway", "NH", 44.0536, -71.1284, True),
    ("Littleton Regional Healthcare", "Littleton", "NH", 44.3064, -71.7731, True),
    
    # MAINE
    ("Stephens Memorial Hospital", "Norway", "ME", 44.2136, -70.5428, True),
    ("Central Maine Medical Center", "Lewiston", "ME", 44.0978, -70.2178, True),
    ("Franklin Memorial Hospital", "Farmington", "ME", 44.6700, -70.1481, True),
    
    # NEW YORK
    ("Albany Medical Center", "Albany", "NY", 42.6525, -73.7739, True),
    ("Columbia Memorial Hospital", "Hudson", "NY", 42.2528, -73.7907, True),
    
    # PENNSYLVANIA
    ("Lehigh Valley Hospital", "Allentown", "PA", 40.5953, -75.4903, True),
    ("Geisinger Wyoming Valley", "Wilkes-Barre", "PA", 41.2456, -75.8497, True),
    ("Excela Health Westmoreland", "Greensburg", "PA", 40.3017, -79.5389, True),
    
    # MICHIGAN
    ("Munson Medical Center", "Traverse City", "MI", 44.7631, -85.6206, True),
    ("McLaren Northern Michigan", "Petoskey", "MI", 45.3736, -84.9553, True),
    
    # WEST VIRGINIA
    ("Pocahontas Memorial Hospital", "Buckeye", "WV", 38.1867, -80.1356, True),
    ("Davis Medical Center", "Elkins", "WV", 38.9259, -79.8467, True),
    
    # WASHINGTON
    ("EvergreenHealth", "Kirkland", "WA", 47.7217, -122.1778, True),
    ("Overlake Medical Center", "Bellevue", "WA", 47.6183, -122.1817, True),
    ("Cascade Medical Center", "Leavenworth", "WA", 47.5961, -120.6614, True),
    
    # IDAHO
    ("Bonner General Health", "Sandpoint", "ID", 48.2767, -116.5531, True),
    
    # NEW MEXICO
    ("Holy Cross Hospital", "Taos", "NM", 36.4072, -105.5731, True),
]

def main():
    print("=" * 50)
    print("Building hospital data")
    print("=" * 50, flush=True)
    
    # Load resorts for distance calculation
    try:
        with open(RESORTS_FILE, "r") as f:
            resorts = json.load(f)
        print(f"Loaded {len(resorts)} resorts")
    except:
        resorts = []
    
    hospitals = []
    
    for name, city, state, lat, lon, has_er in HOSPITALS:
        # Find nearest resort
        min_dist = float("inf")
        nearest_resort = None
        
        for resort in resorts:
            dist = haversine_miles(lat, lon, resort["lat"], resort["lon"])
            if dist < min_dist:
                min_dist = dist
                nearest_resort = resort["name"]
        
        hospital = {
            "id": f"{name}|{state}".replace(" ", "-").lower(),
            "name": name,
            "address": "",
            "city": city,
            "state": state,
            "zip": "",
            "lat": lat,
            "lon": lon,
            "hasEmergency": has_er,
            "phone": "",
            "nearestResort": nearest_resort,
            "nearestResortDist": round(min_dist, 1) if resorts else None,
        }
        hospitals.append(hospital)
        print(f"  ✓ {name}, {city}, {state}")
    
    # Sort by state, city
    hospitals.sort(key=lambda h: (h["state"], h["city"]))
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(hospitals, f, indent=2)
    
    print("\n" + "=" * 50)
    print(f"Saved {len(hospitals)} hospitals to {OUTPUT_FILE}")
    print("=" * 50)

if __name__ == "__main__":
    main()

