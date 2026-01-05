import { describe, it, expect } from "vitest";
import {
  getNearestClinics,
  getNearestHospitals,
  getNearestResorts,
  getNearestResortsFromHospital,
} from "@/utils/nearestLocations";
import { mockResorts } from "../fixtures/resorts";
import { mockClinics } from "../fixtures/clinics";
import { mockHospitals } from "../fixtures/hospitals";
import type { Resort, Clinic, Hospital } from "@/types";

describe("nearestLocations", () => {
  // =========================================================================
  // getNearestClinics - For Resorts (guaranteed minimum results)
  // =========================================================================
  describe("getNearestClinics", () => {
    const vailResort = mockResorts.find((r) => r.name === "Vail")!;
    const stoweResort = mockResorts.find((r) => r.name === "Stowe")!;

    it("returns clinics sorted by distance ascending", () => {
      const result = getNearestClinics(vailResort, mockClinics);

      for (let i = 1; i < result.length; i++) {
        expect(result[i].distance).toBeGreaterThanOrEqual(
          result[i - 1].distance
        );
      }
    });

    it("includes distance property on each clinic", () => {
      const result = getNearestClinics(vailResort, mockClinics);

      result.forEach((clinic) => {
        expect(clinic).toHaveProperty("distance");
        expect(typeof clinic.distance).toBe("number");
        expect(clinic.distance).toBeGreaterThanOrEqual(0);
      });
    });

    it("returns at least minCount clinics even if beyond maxMiles", () => {
      // Stowe, VT is far from most CO clinics
      const result = getNearestClinics(stoweResort, mockClinics, {
        maxMiles: 50, // Very restrictive
        minCount: 3,
      });

      // Should still return at least 3 even though most are beyond 50mi
      expect(result.length).toBeGreaterThanOrEqual(3);
    });

    it("returns clinics within maxMiles when enough are available", () => {
      const result = getNearestClinics(vailResort, mockClinics, {
        maxMiles: 200,
        minCount: 3,
      });

      // All returned clinics should be within 200 miles
      const allWithinRange = result.every((c) => c.distance <= 200);
      // At least the minCount should be met
      expect(result.length).toBeGreaterThanOrEqual(3);
      // If we have 3+ within range, all should be within range
      if (result.length >= 3) {
        expect(allWithinRange).toBe(true);
      }
    });

    it("respects the limit parameter", () => {
      const result = getNearestClinics(vailResort, mockClinics, { limit: 2 });

      expect(result.length).toBeLessThanOrEqual(2);
    });

    it("returns empty array when no clinics provided", () => {
      const result = getNearestClinics(vailResort, []);

      expect(result).toEqual([]);
    });

    it("uses default config when not specified", () => {
      const result = getNearestClinics(vailResort, mockClinics);

      // Default limit is 5
      expect(result.length).toBeLessThanOrEqual(5);
      // Default minCount is 3
      expect(result.length).toBeGreaterThanOrEqual(
        Math.min(3, mockClinics.length)
      );
    });

    // REGRESSION TEST: This was the original bug - showing distant clinics
    it("REGRESSION: prioritizes nearby clinics over distant ones", () => {
      // Create a clinic right next to Vail and one very far away
      const nearbyClinic: Clinic = {
        ccn: "near-001",
        facility: "Vail Nearby Dialysis",
        provider: "davita",
        address: "1 Main St",
        city: "Vail",
        state: "CO",
        zip: "81657",
        lat: 39.641, // Very close to Vail
        lon: -106.375,
      };

      const distantClinic: Clinic = {
        ccn: "far-001",
        facility: "NYC Far Away Dialysis",
        provider: "davita",
        address: "1 Wall St",
        city: "New York",
        state: "NY",
        zip: "10001",
        lat: 40.7128, // NYC - very far
        lon: -74.006,
      };

      const result = getNearestClinics(
        vailResort,
        [distantClinic, nearbyClinic],
        {
          maxMiles: 100,
          minCount: 1,
        }
      );

      // Nearby should be first
      expect(result[0].ccn).toBe("near-001");
      expect(result[0].distance).toBeLessThan(10); // Should be < 10 miles
    });
  });

  // =========================================================================
  // getNearestHospitals - For Resorts (guaranteed minimum results)
  // =========================================================================
  describe("getNearestHospitals", () => {
    const vailResort = mockResorts.find((r) => r.name === "Vail")!;

    it("returns hospitals sorted by distance ascending", () => {
      const result = getNearestHospitals(vailResort, mockHospitals);

      for (let i = 1; i < result.length; i++) {
        expect(result[i].distance).toBeGreaterThanOrEqual(
          result[i - 1].distance
        );
      }
    });

    it("includes distance property on each hospital", () => {
      const result = getNearestHospitals(vailResort, mockHospitals);

      result.forEach((hospital) => {
        expect(hospital).toHaveProperty("distance");
        expect(typeof hospital.distance).toBe("number");
      });
    });

    it("returns at least minCount hospitals even if beyond maxMiles", () => {
      const result = getNearestHospitals(vailResort, mockHospitals, {
        maxMiles: 1, // Extremely restrictive
        minCount: 3,
      });

      // Should still return at least 3 (or all available if < 3)
      expect(result.length).toBeGreaterThanOrEqual(
        Math.min(3, mockHospitals.length)
      );
    });

    it("respects the limit parameter", () => {
      const result = getNearestHospitals(vailResort, mockHospitals, {
        limit: 2,
      });

      expect(result.length).toBeLessThanOrEqual(2);
    });

    it("returns empty array when no hospitals provided", () => {
      const result = getNearestHospitals(vailResort, []);

      expect(result).toEqual([]);
    });

    // REGRESSION TEST: Ensure we always show hospitals for safety
    it("REGRESSION: always returns hospitals for skier safety even in remote areas", () => {
      // Jackson Hole, WY - more remote location
      const jacksonHole = mockResorts.find((r) => r.name === "Jackson Hole")!;

      const result = getNearestHospitals(jacksonHole, mockHospitals, {
        maxMiles: 50,
        minCount: 3,
      });

      // Even in remote areas, skiers need to know where hospitals are
      expect(result.length).toBeGreaterThanOrEqual(
        Math.min(3, mockHospitals.length)
      );
    });
  });

  // =========================================================================
  // getNearestResorts - For Clinics (STRICT distance filter)
  // =========================================================================
  describe("getNearestResorts", () => {
    const denverClinic = mockClinics.find((c) => c.city === "Denver")!;
    const burlingtonClinic = mockClinics.find((c) => c.city === "Burlington")!;

    it("returns resorts sorted by distance ascending", () => {
      const result = getNearestResorts(denverClinic, mockResorts, {
        maxMiles: 200,
      });

      for (let i = 1; i < result.length; i++) {
        expect(result[i].distance).toBeGreaterThanOrEqual(
          result[i - 1].distance
        );
      }
    });

    it("includes distance property on each resort", () => {
      const result = getNearestResorts(denverClinic, mockResorts, {
        maxMiles: 200,
      });

      result.forEach((resort) => {
        expect(resort).toHaveProperty("distance");
        expect(typeof resort.distance).toBe("number");
      });
    });

    it("STRICT: only returns resorts within maxMiles", () => {
      const result = getNearestResorts(denverClinic, mockResorts, {
        maxMiles: 100,
      });

      // ALL results must be within maxMiles
      result.forEach((resort) => {
        expect(resort.distance).toBeLessThanOrEqual(100);
      });
    });

    it("STRICT: returns empty array if no resorts within maxMiles", () => {
      const result = getNearestResorts(denverClinic, mockResorts, {
        maxMiles: 1,
      });

      // Should be empty - no resort is 1 mile from Denver
      expect(result).toEqual([]);
    });

    it("respects the limit parameter", () => {
      const result = getNearestResorts(denverClinic, mockResorts, {
        limit: 2,
        maxMiles: 500,
      });

      expect(result.length).toBeLessThanOrEqual(2);
    });

    // REGRESSION TEST: This was the bug - showing 400mi resorts
    it("REGRESSION: does NOT show distant resorts beyond maxMiles", () => {
      // Create a resort very far away
      const farResort: Resort = {
        id: "Far Resort|AK",
        name: "Far Resort",
        state: "AK",
        lat: 64.8378, // Alaska
        lon: -147.7164,
        passNetwork: "independent",
        region: "west",
      };

      const nearResort: Resort = {
        id: "Near Resort|CO",
        name: "Near Resort",
        state: "CO",
        lat: 39.75, // Near Denver
        lon: -105.0,
        passNetwork: "independent",
        region: "rockies",
      };

      const result = getNearestResorts(denverClinic, [farResort, nearResort], {
        maxMiles: 100,
      });

      // Should only include the near resort
      expect(result.length).toBe(1);
      expect(result[0].name).toBe("Near Resort");
      expect(result[0].distance).toBeLessThan(100);
    });

    // REGRESSION TEST: Original bug showed 234mi and 401mi results
    it("REGRESSION: filters out 200+ mile results with 100mi max", () => {
      const result = getNearestResorts(burlingtonClinic, mockResorts, {
        maxMiles: 100,
      });

      // Burlington, VT clinic - only Stowe should be nearby
      result.forEach((resort) => {
        expect(resort.distance).toBeLessThanOrEqual(100);
        // Specifically should NOT include Colorado resorts (2000+ miles away)
        expect(resort.state).not.toBe("CO");
      });
    });
  });

  // =========================================================================
  // getNearestResortsFromHospital - For Hospitals (STRICT distance filter)
  // =========================================================================
  describe("getNearestResortsFromHospital", () => {
    const vailHospital = mockHospitals.find((h) => h.city === "Vail")!;
    const parkCityHospital = mockHospitals.find((h) => h.city === "Park City")!;

    it("returns resorts sorted by distance ascending", () => {
      const result = getNearestResortsFromHospital(vailHospital, mockResorts, {
        maxMiles: 200,
      });

      for (let i = 1; i < result.length; i++) {
        expect(result[i].distance).toBeGreaterThanOrEqual(
          result[i - 1].distance
        );
      }
    });

    it("includes distance property on each resort", () => {
      const result = getNearestResortsFromHospital(vailHospital, mockResorts, {
        maxMiles: 200,
      });

      result.forEach((resort) => {
        expect(resort).toHaveProperty("distance");
        expect(typeof resort.distance).toBe("number");
      });
    });

    it("STRICT: only returns resorts within maxMiles", () => {
      const result = getNearestResortsFromHospital(vailHospital, mockResorts, {
        maxMiles: 50,
      });

      result.forEach((resort) => {
        expect(resort.distance).toBeLessThanOrEqual(50);
      });
    });

    it("STRICT: returns empty array if no resorts within maxMiles", () => {
      const result = getNearestResortsFromHospital(
        parkCityHospital,
        mockResorts,
        {
          maxMiles: 1,
        }
      );

      expect(result).toEqual([]);
    });

    it("respects the limit parameter", () => {
      const result = getNearestResortsFromHospital(vailHospital, mockResorts, {
        limit: 2,
        maxMiles: 500,
      });

      expect(result.length).toBeLessThanOrEqual(2);
    });

    // REGRESSION TEST: Same bug as clinics
    it("REGRESSION: does NOT show distant resorts beyond maxMiles", () => {
      const result = getNearestResortsFromHospital(
        parkCityHospital,
        mockResorts,
        {
          maxMiles: 100,
        }
      );

      // Park City Hospital should only show Park City resort (nearby)
      result.forEach((resort) => {
        expect(resort.distance).toBeLessThanOrEqual(100);
      });

      // Should NOT include Vermont resorts (~2000 miles away)
      const hasVermontResort = result.some((r) => r.state === "VT");
      expect(hasVermontResort).toBe(false);
    });

    // REGRESSION TEST: Using inline Hospital fixture for consistency
    it("REGRESSION: remote hospital returns empty when no resorts nearby", () => {
      const remoteHospital: Hospital = {
        id: "hosp-remote",
        name: "Remote Alaska Hospital",
        address: "1 Remote Rd",
        city: "Barrow",
        state: "AK",
        zip: "99723",
        lat: 71.2906, // Barrow, Alaska - very remote
        lon: -156.7886,
        hasEmergency: true,
        traumaLevel: 4,
      };

      const result = getNearestResortsFromHospital(
        remoteHospital,
        mockResorts,
        {
          maxMiles: 100,
        }
      );

      // No resorts within 100 miles of Barrow, Alaska
      expect(result).toEqual([]);
    });
  });

  // =========================================================================
  // Integration-style tests for the behavior difference
  // =========================================================================
  describe("behavior difference: resort vs clinic/hospital queries", () => {
    it("resorts get GUARANTEED minimum results (for skier safety)", () => {
      const remoteResort: Resort = {
        id: "Remote|AK",
        name: "Remote Alaska Resort",
        state: "AK",
        lat: 64.0, // Alaska - far from everything
        lon: -150.0,
        passNetwork: "independent",
        region: "west",
      };

      const clinicResult = getNearestClinics(remoteResort, mockClinics, {
        maxMiles: 10, // Very restrictive
        minCount: 3,
      });

      const hospitalResult = getNearestHospitals(remoteResort, mockHospitals, {
        maxMiles: 10, // Very restrictive
        minCount: 3,
      });

      // Even with restrictive maxMiles, we get minCount results
      expect(clinicResult.length).toBeGreaterThanOrEqual(
        Math.min(3, mockClinics.length)
      );
      expect(hospitalResult.length).toBeGreaterThanOrEqual(
        Math.min(3, mockHospitals.length)
      );
    });

    it("clinics/hospitals get STRICT filtering (show only relevant nearby resorts)", () => {
      const remoteClinic: Clinic = {
        ccn: "remote-001",
        facility: "Remote Clinic",
        provider: "davita",
        address: "1 Remote Rd",
        city: "Remote",
        state: "AK",
        zip: "99999",
        lat: 64.0, // Alaska - far from resorts
        lon: -150.0,
      };

      const result = getNearestResorts(remoteClinic, mockResorts, {
        maxMiles: 100,
      });

      // Should return empty - no resorts within 100 miles of Alaska
      expect(result).toEqual([]);
    });
  });
});
