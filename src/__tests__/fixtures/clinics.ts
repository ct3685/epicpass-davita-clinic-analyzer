import type { Clinic } from "@/types";

/**
 * Mock clinic data for testing
 */
export const mockClinics: Clinic[] = [
  {
    ccn: "06-1234",
    facility: "DaVita Denver Dialysis",
    provider: "davita",
    address: "123 Main St",
    city: "Denver",
    state: "CO",
    zip: "80202",
    lat: 39.7392,
    lon: -104.9903,
    nearestResort: "Vail",
    nearestResortDist: 97.5,
  },
  {
    ccn: "06-5678",
    facility: "Fresenius Kidney Care Boulder",
    provider: "fresenius",
    address: "456 Pearl St",
    city: "Boulder",
    state: "CO",
    zip: "80302",
    lat: 40.015,
    lon: -105.2705,
    nearestResort: "Breckenridge",
    nearestResortDist: 65.2,
  },
  {
    ccn: "49-1111",
    facility: "DaVita Salt Lake Dialysis",
    provider: "davita",
    address: "789 State St",
    city: "Salt Lake City",
    state: "UT",
    zip: "84111",
    lat: 40.7608,
    lon: -111.891,
    nearestResort: "Park City",
    nearestResortDist: 28.4,
  },
  {
    ccn: "50-2222",
    facility: "Mountain Dialysis Center",
    provider: "independent",
    address: "321 Mountain Rd",
    city: "Aspen",
    state: "CO",
    zip: "81611",
    lat: 39.1911,
    lon: -106.8175,
    nearestResort: "Aspen Snowmass",
    nearestResortDist: 8.3,
  },
  {
    ccn: "45-3333",
    facility: "DaVita Burlington Dialysis",
    provider: "davita",
    address: "100 Church St",
    city: "Burlington",
    state: "VT",
    zip: "05401",
    lat: 44.4759,
    lon: -73.2121,
    nearestResort: "Stowe",
    nearestResortDist: 35.6,
  },
];

/**
 * Get mock clinics filtered by provider
 */
export function getMockClinicsByProvider(provider: string): Clinic[] {
  return mockClinics.filter((c) => c.provider === provider);
}

/**
 * Get mock clinics filtered by state
 */
export function getMockClinicsByState(state: string): Clinic[] {
  return mockClinics.filter((c) => c.state === state);
}

