import { haversine } from "./haversine";
import type {
  Resort,
  Clinic,
  Hospital,
  ClinicWithDistance,
  ResortWithDistance,
  HospitalWithDistance,
} from "@/types";

/**
 * Configuration for nearest location queries
 */
export interface NearestConfig {
  /** Maximum number of results to return */
  limit?: number;
  /** Maximum distance in miles to consider */
  maxMiles?: number;
  /** Minimum count to return (even if beyond maxMiles) */
  minCount?: number;
}

const DEFAULT_CONFIG: Required<NearestConfig> = {
  limit: 5,
  maxMiles: 100,
  minCount: 3,
};

/**
 * Get nearest clinics for a resort.
 * Returns at least `minCount` clinics, prioritizing those within `maxMiles`.
 * This ensures skiers always know where to find medical care, even in remote areas.
 *
 * @param resort - The resort to find clinics near
 * @param clinics - Array of all clinics to search
 * @param config - Optional configuration (limit, maxMiles, minCount)
 * @returns Array of clinics sorted by distance, with at least minCount items
 */
export function getNearestClinics(
  resort: Resort,
  clinics: Clinic[],
  config: NearestConfig = {}
): ClinicWithDistance[] {
  const { limit, maxMiles, minCount } = { ...DEFAULT_CONFIG, ...config };

  const withDistance = clinics
    .map((c) => ({
      ...c,
      distance: haversine(
        { lat: resort.lat, lon: resort.lon },
        { lat: c.lat, lon: c.lon }
      ),
    }))
    .sort((a, b) => a.distance - b.distance);

  // Get items within max distance
  const withinRange = withDistance.filter((c) => c.distance <= maxMiles);

  // Ensure at least minCount items (even if beyond maxMiles)
  if (withinRange.length >= minCount) {
    return withinRange.slice(0, limit);
  }

  // Need to include some beyond range to meet minimum
  return withDistance.slice(
    0,
    Math.max(minCount, Math.min(limit, withinRange.length))
  );
}

/**
 * Get nearest hospitals for a resort.
 * Returns at least `minCount` hospitals, prioritizing those within `maxMiles`.
 * This ensures skiers always know where to find emergency care, even in remote areas.
 *
 * @param resort - The resort to find hospitals near
 * @param hospitals - Array of all hospitals to search
 * @param config - Optional configuration (limit, maxMiles, minCount)
 * @returns Array of hospitals sorted by distance, with at least minCount items
 */
export function getNearestHospitals(
  resort: Resort,
  hospitals: Hospital[],
  config: NearestConfig = {}
): HospitalWithDistance[] {
  const { limit, maxMiles, minCount } = { ...DEFAULT_CONFIG, ...config };

  const withDistance = hospitals
    .map((h) => ({
      ...h,
      distance: haversine(
        { lat: resort.lat, lon: resort.lon },
        { lat: h.lat, lon: h.lon }
      ),
    }))
    .sort((a, b) => a.distance - b.distance);

  // Get items within max distance
  const withinRange = withDistance.filter((h) => h.distance <= maxMiles);

  // Ensure at least minCount items (even if beyond maxMiles)
  if (withinRange.length >= minCount) {
    return withinRange.slice(0, limit);
  }

  // Need to include some beyond range to meet minimum
  return withDistance.slice(
    0,
    Math.max(minCount, Math.min(limit, withinRange.length))
  );
}

/**
 * Get nearest resorts for a clinic.
 * Uses STRICT distance filtering - only returns resorts within `maxMiles`.
 * Returns empty array if no resorts are within range.
 *
 * @param clinic - The clinic to find resorts near
 * @param resorts - Array of all resorts to search
 * @param config - Optional configuration (limit, maxMiles)
 * @returns Array of resorts within maxMiles, sorted by distance
 */
export function getNearestResorts(
  clinic: Clinic,
  resorts: Resort[],
  config: Pick<NearestConfig, "limit" | "maxMiles"> = {}
): ResortWithDistance[] {
  const { limit = 5, maxMiles = 100 } = config;

  return resorts
    .map((r) => ({
      ...r,
      distance: haversine(
        { lat: clinic.lat, lon: clinic.lon },
        { lat: r.lat, lon: r.lon }
      ),
    }))
    .filter((r) => r.distance <= maxMiles)
    .sort((a, b) => a.distance - b.distance)
    .slice(0, limit);
}

/**
 * Get nearest resorts for a hospital.
 * Uses STRICT distance filtering - only returns resorts within `maxMiles`.
 * Returns empty array if no resorts are within range.
 *
 * @param hospital - The hospital to find resorts near
 * @param resorts - Array of all resorts to search
 * @param config - Optional configuration (limit, maxMiles)
 * @returns Array of resorts within maxMiles, sorted by distance
 */
export function getNearestResortsFromHospital(
  hospital: Hospital,
  resorts: Resort[],
  config: Pick<NearestConfig, "limit" | "maxMiles"> = {}
): ResortWithDistance[] {
  const { limit = 5, maxMiles = 100 } = config;

  return resorts
    .map((r) => ({
      ...r,
      distance: haversine(
        { lat: hospital.lat, lon: hospital.lon },
        { lat: r.lat, lon: r.lon }
      ),
    }))
    .filter((r) => r.distance <= maxMiles)
    .sort((a, b) => a.distance - b.distance)
    .slice(0, limit);
}

