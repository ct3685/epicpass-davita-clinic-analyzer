#!/usr/bin/env python3
"""
SkiWithCare Data Generator
==========================

Generates JSON data files for the SkiWithCare web application:
- resorts.json: All ski resorts (Epic + Ikon Pass)
- clinics.json: All dialysis clinics near resorts (all providers)
- hospitals.json: Hospitals near resorts (future)

Data Sources:
- OpenStreetMap Nominatim (resort geocoding)
- CMS Provider Data Catalog (dialysis facilities)
- US Census Bureau Geocoder (facility geocoding)

Usage:
    python scripts/generate_data.py

Output:
    public/resorts.json
    public/clinics.json
"""

import json
import os
import sys
import time
from io import StringIO
from typing import Dict, List

import pandas as pd
import requests

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_all_resorts, classify_provider
from geocoder import ResortGeocoder, FacilityGeocoder, haversine_miles

# === CONFIGURATION ===

OUTPUT_DIR = "public"
RESORTS_JSON = f"{OUTPUT_DIR}/resorts.json"
CLINICS_JSON = f"{OUTPUT_DIR}/clinics.json"
HOSPITALS_JSON = f"{OUTPUT_DIR}/hospitals.json"

# CMS Dialysis Facility Dataset
CMS_METADATA_URL = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items/23ew-n7w9"
CMS_CSV_FALLBACK = "https://data.cms.gov/provider-data/sites/default/files/resources/c04d84bc5c641284494bee4f20f17f9c_1759341903/DFC_FACILITY.csv"

# Distance threshold for clinic inclusion (miles)
MAX_CLINIC_DISTANCE = 200

# US states (filter out Canadian resorts)
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV",
    "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN",
    "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC", "CA/NV"
}


def get_cms_csv_url() -> str:
    """Fetch the current CSV download URL from CMS metadata."""
    try:
        resp = requests.get(CMS_METADATA_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        distributions = data.get("distribution", [])
        for dist in distributions:
            if dist.get("mediaType") == "text/csv":
                return dist.get("downloadURL", CMS_CSV_FALLBACK)
        
        return CMS_CSV_FALLBACK
    except requests.RequestException:
        print("  [WARNING] Could not fetch metadata, using fallback CSV URL")
        return CMS_CSV_FALLBACK


def geocode_resorts(resorts: List[Dict]) -> pd.DataFrame:
    """Geocode all resorts and return DataFrame."""
    print("\n[1/3] Geocoding resorts via OpenStreetMap Nominatim...")
    
    geocoder = ResortGeocoder()
    print(f"  Loaded {len(geocoder.cache)} cached resort geocodes")
    
    data = []
    new_count = 0
    cached_count = 0
    
    # Filter to US resorts only
    us_resorts = [r for r in resorts if r["state"] in US_STATES]
    print(f"  Processing {len(us_resorts)} US resorts (skipping {len(resorts) - len(us_resorts)} non-US)")
    
    for idx, resort in enumerate(us_resorts, start=1):
        name = resort["name"]
        state = resort["state"]
        cache_key = f"{name}|{state}"
        
        was_cached = cache_key in geocoder.cache
        lat, lon = geocoder.geocode(name, state)
        
        if was_cached:
            cached_count += 1
        else:
            new_count += 1
            status = f"OK ({lat:.4f}, {lon:.4f})" if lat else "FAILED"
            print(f"  [{idx:02d}/{len(us_resorts)}] {name}, {state}... {status}")
        
        data.append({
            "id": f"{name}|{state}",
            "name": name,
            "state": state,
            "lat": lat,
            "lon": lon,
            "passNetwork": resort["passNetwork"],
            "region": resort["region"],
        })
    
    geocoder.save()
    print(f"  Summary: {cached_count} cached, {new_count} newly geocoded")
    
    return pd.DataFrame(data)


def download_dialysis_data() -> pd.DataFrame:
    """Download dialysis facility data from CMS."""
    print("\n[2/3] Downloading CMS dialysis facility data...")
    
    csv_url = get_cms_csv_url()
    print(f"  URL: {csv_url[:70]}...")
    
    try:
        resp = requests.get(csv_url, timeout=120)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        print(f"  Total facilities: {len(df):,}")
        return df
    except requests.RequestException as e:
        print(f"  [ERROR] Download failed: {e}")
        return pd.DataFrame()


def geocode_clinics(df_facilities: pd.DataFrame) -> pd.DataFrame:
    """Geocode dialysis facilities and return DataFrame with coordinates."""
    print("\n[3/3] Geocoding dialysis facilities via US Census Geocoder...")
    
    geocoder = FacilityGeocoder()
    print(f"  Loaded {len(geocoder.cache):,} cached geocodes")
    
    lats = []
    lons = []
    providers = []
    
    total = len(df_facilities)
    geocoded_count = 0
    cached_count = 0
    failed_count = 0
    
    for idx, (_, row) in enumerate(df_facilities.iterrows(), start=1):
        ccn = str(row.get("CMS Certification Number (CCN)", ""))
        
        # Get cached or geocode
        was_cached = ccn in geocoder.cache
        lat, lon = geocoder.geocode(
            ccn,
            str(row.get("Address Line 1", "")),
            str(row.get("City/Town", "")),
            str(row.get("State", "")),
            str(row.get("ZIP Code", ""))
        )
        
        lats.append(lat)
        lons.append(lon)
        
        # Classify provider chain
        chain = str(row.get("Chain Organization", ""))
        providers.append(classify_provider(chain))
        
        if was_cached:
            cached_count += 1
        else:
            if lat is not None:
                geocoded_count += 1
            else:
                failed_count += 1
        
        # Progress update every 100 facilities
        if idx % 100 == 0 or idx == total:
            print(f"  Progress: {idx:,}/{total:,} ({geocoded_count:,} new, {cached_count:,} cached, {failed_count:,} failed)")
            geocoder.save()
    
    geocoder.save()
    
    df_facilities = df_facilities.copy()
    df_facilities["lat"] = lats
    df_facilities["lon"] = lons
    df_facilities["provider"] = providers
    
    return df_facilities


def generate_resorts_json(df_resorts: pd.DataFrame) -> None:
    """Generate resorts.json from DataFrame."""
    print(f"\n[OUTPUT] Generating {RESORTS_JSON}...")
    
    valid = df_resorts.dropna(subset=["lat", "lon"]).copy()
    
    resorts = []
    for _, row in valid.sort_values("name").iterrows():
        resorts.append({
            "id": row["id"],
            "name": row["name"],
            "state": row["state"],
            "lat": round(float(row["lat"]), 6),
            "lon": round(float(row["lon"]), 6),
            "passNetwork": row["passNetwork"],
            "region": row["region"],
        })
    
    with open(RESORTS_JSON, 'w') as f:
        json.dump(resorts, f, indent=2)
    
    # Count by pass network
    epic_count = sum(1 for r in resorts if r["passNetwork"] == "epic")
    ikon_count = sum(1 for r in resorts if r["passNetwork"] == "ikon")
    
    print(f"  Total resorts: {len(resorts)} ({epic_count} Epic, {ikon_count} Ikon)")
    print(f"  Saved to: {RESORTS_JSON}")


def generate_clinics_json(df_resorts: pd.DataFrame, df_clinics: pd.DataFrame) -> None:
    """Generate clinics.json with all clinics within MAX_CLINIC_DISTANCE of any resort."""
    print(f"\n[OUTPUT] Generating {CLINICS_JSON} (clinics within {MAX_CLINIC_DISTANCE} mi of any resort)...")
    
    valid_resorts = df_resorts.dropna(subset=["lat", "lon"])
    valid_clinics = df_clinics.dropna(subset=["lat", "lon"])
    
    clinics = []
    
    for _, clinic in valid_clinics.iterrows():
        clinic_lat = float(clinic["lat"])
        clinic_lon = float(clinic["lon"])
        
        # Find nearest resort
        min_dist = float('inf')
        nearest_resort = None
        
        for _, resort in valid_resorts.iterrows():
            dist = haversine_miles(
                clinic_lat, clinic_lon,
                float(resort["lat"]), float(resort["lon"])
            )
            if dist < min_dist:
                min_dist = dist
                nearest_resort = resort["name"]
        
        # Only include if within threshold
        if min_dist <= MAX_CLINIC_DISTANCE:
            clinics.append({
                "ccn": str(clinic.get("CMS Certification Number (CCN)", "")),
                "facility": clinic.get("Facility Name", ""),
                "provider": clinic.get("provider", "other"),
                "address": clinic.get("Address Line 1", ""),
                "city": clinic.get("City/Town", ""),
                "state": clinic.get("State", ""),
                "zip": str(clinic.get("ZIP Code", "")),
                "lat": round(clinic_lat, 6),
                "lon": round(clinic_lon, 6),
                "nearestResort": nearest_resort,
                "nearestResortDist": round(min_dist, 2)
            })
    
    # Sort by state, city, facility
    clinics.sort(key=lambda c: (c["state"], c["city"], c["facility"]))
    
    with open(CLINICS_JSON, 'w') as f:
        json.dump(clinics, f, indent=2)
    
    # Count by provider
    provider_counts = {}
    for c in clinics:
        p = c["provider"]
        provider_counts[p] = provider_counts.get(p, 0) + 1
    
    print(f"  Total clinics: {len(clinics):,} (of {len(valid_clinics):,} total)")
    for provider, count in sorted(provider_counts.items()):
        print(f"    - {provider}: {count:,}")
    print(f"  Saved to: {CLINICS_JSON}")


def main():
    """Main execution flow."""
    print("=" * 70)
    print("SkiWithCare Data Generator")
    print("Epic Pass + Ikon Pass Resorts | All Dialysis Providers")
    print("=" * 70)
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Geocode resorts
    all_resorts = get_all_resorts()
    df_resorts = geocode_resorts(all_resorts)
    
    # Report failures
    failed = df_resorts[df_resorts["lat"].isna()]
    if not failed.empty:
        print("\n  [WARNING] Resorts that failed to geocode:")
        for _, row in failed.iterrows():
            print(f"    - {row['name']}, {row['state']}")
    
    # Step 2: Download dialysis data
    df_facilities = download_dialysis_data()
    if df_facilities.empty:
        print("\n[ERROR] No dialysis data available, cannot continue.")
        return
    
    # Step 3: Geocode clinics
    df_clinics = geocode_clinics(df_facilities)
    
    # Step 4: Generate output files
    print("\n[4/4] Generating output files...")
    generate_resorts_json(df_resorts)
    generate_clinics_json(df_resorts, df_clinics)
    
    # Summary
    valid_resorts = df_resorts.dropna(subset=["lat", "lon"])
    print("\n" + "=" * 70)
    print("SUCCESS! Data generation complete.")
    print(f"  - {RESORTS_JSON} ({len(valid_resorts)} resorts)")
    print(f"  - {CLINICS_JSON} (dialysis clinics within {MAX_CLINIC_DISTANCE} mi)")
    print("=" * 70)


if __name__ == "__main__":
    main()

