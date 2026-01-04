#!/usr/bin/env python3
"""
Fetch Hospital Data from CMS (FAST BATCH VERSION)
==================================================

Uses Census Bureau BATCH geocoding API - 10,000 addresses at once!
Much faster than one-by-one geocoding.

Expected time: 2-3 minutes total (vs 15-20 min sequential)

Usage:
    python scripts/fetch_cms_hospitals.py
"""

import json
import math
import time
import sys
import os
import requests
import csv
from io import StringIO

# CMS API
CMS_METADATA = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items/xubh-q36u"

# Census Batch Geocoder (handles up to 10,000 addresses per request)
CENSUS_BATCH_URL = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"

# Files
RESORTS_FILE = "public/resorts.json"
OUTPUT_FILE = "public/hospitals.json"
CACHE_FILE = "hospital_geocode_cache.json"
TEMP_CSV = "_temp_addresses.csv"

# Settings
MAX_DISTANCE_MILES = 200
BATCH_SIZE = 5000  # Census allows 10k, but smaller batches = more reliable

# States with ski resorts
SKI_STATES = {
    "CA", "CO", "UT", "WY", "MT", "ID", "NM", "AZ", "NV",
    "WA", "OR", "VT", "NH", "ME", "NY", "PA", "MA", "CT", "NJ",
    "MI", "WI", "MN", "OH", "IN", "MO", "WV", "VA", "NC", "TN",
}


def haversine(lat1, lon1, lat2, lon2):
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl/2)**2
    return 2 * r * math.asin(math.sqrt(a))


def load_json(path, default=None):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default if default is not None else {}


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def spinner(msg, i):
    """Simple spinner for long operations."""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    sys.stdout.write(f"\r   {chars[i % len(chars)]} {msg}")
    sys.stdout.flush()


def batch_geocode(addresses):
    """
    Geocode addresses using Census Bureau batch API.
    addresses: list of (id, street, city, state, zip)
    Returns: dict of id -> {"lat": ..., "lon": ...} or {"failed": True}
    """
    results = {}
    
    # Create CSV content
    csv_content = StringIO()
    writer = csv.writer(csv_content)
    for addr in addresses:
        writer.writerow(addr)
    
    # Submit to Census
    files = {
        'addressFile': ('addresses.csv', csv_content.getvalue(), 'text/csv')
    }
    data = {
        'benchmark': 'Public_AR_Current',
        'vintage': 'Current_Current'
    }
    
    try:
        response = requests.post(
            CENSUS_BATCH_URL,
            files=files,
            data=data,
            timeout=300  # 5 min timeout for large batches
        )
        response.raise_for_status()
        
        # Parse CSV response
        # Format: id, input_address, match_status, match_type, matched_address, "lon,lat", tiger_id, side
        reader = csv.reader(StringIO(response.text))
        for row in reader:
            if len(row) >= 1:
                fid = row[0]
                match_status = row[2] if len(row) > 2 else ""
                
                if match_status in ("Match", "Exact"):
                    # Coordinates are in column 5 as "lon,lat" string
                    try:
                        coords_str = row[5] if len(row) > 5 else ""
                        if "," in coords_str:
                            lon_str, lat_str = coords_str.split(",")
                            lon = float(lon_str.strip())
                            lat = float(lat_str.strip())
                            results[fid] = {"lat": lat, "lon": lon}
                        else:
                            results[fid] = {"failed": True}
                    except (ValueError, IndexError):
                        results[fid] = {"failed": True}
                else:
                    results[fid] = {"failed": True}
                    
    except Exception as e:
        print(f"\n   ❌ Batch geocode error: {e}")
        # Mark all as failed
        for addr in addresses:
            results[addr[0]] = {"failed": True}
    
    return results


def progress_bar(current, total, width=40, prefix="", suffix=""):
    """Display a progress bar."""
    pct = current / total if total > 0 else 1
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    sys.stdout.write(f"\r{prefix} [{bar}] {current}/{total} ({pct*100:.0f}%) {suffix}  ")
    sys.stdout.flush()


def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   🏥 SkiWithCare - CMS Hospital Fetcher (BATCH MODE)     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Load resorts
    resorts = load_json(RESORTS_FILE, [])
    if not resorts:
        print("❌ ERROR: No resorts. Run build_resorts.py first.")
        return
    print(f"✓ Loaded {len(resorts)} resorts")
    
    # Load cache
    cache = load_json(CACHE_FILE, {})
    print(f"✓ Loaded {len(cache):,} cached geocodes")
    
    # Get CSV URL from CMS
    print()
    print("━" * 60)
    print("📥 Step 1/3: Downloading hospital list from CMS...")
    print("━" * 60)
    
    try:
        for i in range(10):
            spinner("Fetching metadata...", i)
            time.sleep(0.1)
        
        meta = requests.get(CMS_METADATA, timeout=30).json()
        url = next(d["downloadURL"] for d in meta["distribution"] if "csv" in d.get("mediaType", ""))
        
        for i in range(20):
            spinner("Downloading hospital data...", i)
            time.sleep(0.1)
        
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        print(f"\r   ✓ Downloaded {len(resp.content) // 1024:,} KB              ")
    except Exception as e:
        print(f"\r   ❌ ERROR: {e}")
        return
    
    # Parse and filter to ski states
    reader = csv.DictReader(StringIO(resp.text))
    rows = [r for r in reader if r.get("State") in SKI_STATES]
    print(f"   ✓ {len(rows):,} hospitals in ski states")
    
    # Find addresses needing geocode
    need_geocode = []
    for row in rows:
        fid = row.get("Facility ID", "")
        if fid not in cache:
            need_geocode.append((
                fid,
                row.get("Address", ""),
                row.get("City/Town", ""),
                row.get("State", ""),
                row.get("ZIP Code", "")
            ))
    
    cached_count = len(rows) - len(need_geocode)
    
    print()
    print("━" * 60)
    print("📍 Step 2/3: Batch geocoding addresses...")
    print("━" * 60)
    print(f"   Already cached: {cached_count:,}")
    print(f"   Need geocoding: {len(need_geocode):,}")
    
    if need_geocode:
        print()
        start_time = time.time()
        total_batches = (len(need_geocode) + BATCH_SIZE - 1) // BATCH_SIZE
        new_geocodes = 0
        new_failed = 0
        
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(need_geocode))
            batch = need_geocode[start_idx:end_idx]
            
            progress_bar(
                batch_num + 1, 
                total_batches, 
                prefix="   ",
                suffix=f"Batch {batch_num + 1}/{total_batches} ({len(batch)} addresses)"
            )
            
            results = batch_geocode(batch)
            
            for fid, coords in results.items():
                cache[fid] = coords
                if coords.get("lat"):
                    new_geocodes += 1
                else:
                    new_failed += 1
            
            # Save cache after each batch
            save_json(CACHE_FILE, cache)
        
        elapsed = time.time() - start_time
        print()
        print()
        print(f"   ✓ Geocoded: {new_geocodes:,}")
        print(f"   ✗ Failed: {new_failed:,}")
        print(f"   ⏱ Time: {elapsed:.1f}s")
    else:
        print()
        print("   ✓ All hospitals already geocoded!")
    
    # Build output
    print()
    print("━" * 60)
    print(f"🏔 Step 3/3: Finding hospitals within {MAX_DISTANCE_MILES} mi of resorts...")
    print("━" * 60)
    
    hospitals = []
    processed = 0
    
    for row in rows:
        fid = row.get("Facility ID", "")
        c = cache.get(fid, {})
        
        lat, lon = c.get("lat"), c.get("lon")
        if not lat or not lon:
            continue
        
        # Find nearest resort
        min_dist = float("inf")
        nearest = None
        for r in resorts:
            d = haversine(lat, lon, r["lat"], r["lon"])
            if d < min_dist:
                min_dist = d
                nearest = r["name"]
        
        if min_dist > MAX_DISTANCE_MILES:
            continue
        
        hospitals.append({
            "id": fid,
            "name": row.get("Facility Name", ""),
            "address": row.get("Address", ""),
            "city": row.get("City/Town", ""),
            "state": row.get("State", ""),
            "zip": row.get("ZIP Code", ""),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "hasEmergency": row.get("Emergency Services", "").lower() == "yes",
            "phone": row.get("Telephone Number", ""),
            "nearestResort": nearest,
            "nearestResortDist": round(min_dist, 1),
        })
        
        processed += 1
        if processed % 100 == 0:
            spinner(f"Processing... {processed} matched", processed // 10)
    
    hospitals.sort(key=lambda h: (h["state"], h["name"]))
    save_json(OUTPUT_FILE, hospitals)
    
    # Summary
    er = sum(1 for h in hospitals if h["hasEmergency"])
    states = len(set(h["state"] for h in hospitals))
    
    print(f"\r   ✓ Found {len(hospitals):,} hospitals near ski resorts        ")
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                      ✨ COMPLETE ✨                       ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print(f"║  🏥 Hospitals:       {len(hospitals):>5,}                            ║")
    print(f"║  🚑 Emergency rooms: {er:>5,}                            ║")
    print(f"║  📍 States:          {states:>5}                            ║")
    print(f"║  💾 Cache entries:   {len(cache):>5,}                            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Cleanup temp file if exists
    if os.path.exists(TEMP_CSV):
        os.remove(TEMP_CSV)


if __name__ == "__main__":
    main()
