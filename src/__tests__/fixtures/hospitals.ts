import type { Hospital } from "@/types";

/**
 * Mock hospital data for testing
 */
export const mockHospitals: Hospital[] = [
  {
    id: "hosp-001",
    name: "Vail Health Hospital",
    address: "181 W Meadow Dr",
    city: "Vail",
    state: "CO",
    zip: "81657",
    lat: 39.6433,
    lon: -106.3781,
    hasEmergency: true,
    traumaLevel: 3,
    nearestResort: "Vail",
    nearestResortDist: 0.5,
  },
  {
    id: "hosp-002",
    name: "St. Anthony Summit Medical Center",
    address: "340 Peak One Dr",
    city: "Frisco",
    state: "CO",
    zip: "80443",
    lat: 39.5747,
    lon: -106.0975,
    hasEmergency: true,
    traumaLevel: 3,
    nearestResort: "Breckenridge",
    nearestResortDist: 8.2,
  },
  {
    id: "hosp-003",
    name: "Park City Hospital",
    address: "900 Round Valley Dr",
    city: "Park City",
    state: "UT",
    zip: "84060",
    lat: 40.6861,
    lon: -111.4617,
    hasEmergency: true,
    traumaLevel: 2,
    nearestResort: "Park City",
    nearestResortDist: 3.1,
  },
  {
    id: "hosp-004",
    name: "Aspen Valley Hospital",
    address: "401 Castle Creek Rd",
    city: "Aspen",
    state: "CO",
    zip: "81611",
    lat: 39.1847,
    lon: -106.8256,
    hasEmergency: true,
    traumaLevel: 4,
    nearestResort: "Aspen Snowmass",
    nearestResortDist: 2.8,
  },
];

/**
 * Get mock hospitals with emergency rooms only
 */
export function getMockHospitalsWithER(): Hospital[] {
  return mockHospitals.filter((h) => h.hasEmergency);
}

/**
 * Get mock hospitals by trauma level
 */
export function getMockHospitalsByTraumaLevel(level: number): Hospital[] {
  return mockHospitals.filter((h) => h.traumaLevel === level);
}

