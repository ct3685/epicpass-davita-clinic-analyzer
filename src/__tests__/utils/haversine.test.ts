import { describe, it, expect } from "vitest";
import { haversine, haversineRaw } from "@/utils/haversine";

describe("haversine", () => {
  describe("haversine()", () => {
    it("calculates distance between Denver and Vail correctly", () => {
      const denver = { lat: 39.7392, lon: -104.9903 };
      const vail = { lat: 39.6403, lon: -106.3742 };

      const distance = haversine(denver, vail);

      // Should be approximately 74 miles (actual road distance is longer due to terrain)
      expect(distance).toBeGreaterThan(70);
      expect(distance).toBeLessThan(80);
    });

    it("returns 0 for same coordinates", () => {
      const point = { lat: 39.7392, lon: -104.9903 };

      const distance = haversine(point, point);

      expect(distance).toBe(0);
    });

    it("calculates distance in kilometers when specified", () => {
      const denver = { lat: 39.7392, lon: -104.9903 };
      const vail = { lat: 39.6403, lon: -106.3742 };

      const miles = haversine(denver, vail, "miles");
      const km = haversine(denver, vail, "km");

      // km should be ~1.6x miles
      expect(km).toBeGreaterThan(miles * 1.5);
      expect(km).toBeLessThan(miles * 1.7);
    });

    it("handles cross-country distances", () => {
      const newYork = { lat: 40.7128, lon: -74.006 };
      const losAngeles = { lat: 34.0522, lon: -118.2437 };

      const distance = haversine(newYork, losAngeles);

      // NYC to LA is approximately 2,451 miles
      expect(distance).toBeGreaterThan(2400);
      expect(distance).toBeLessThan(2500);
    });

    it("handles negative longitude differences", () => {
      const seattle = { lat: 47.6062, lon: -122.3321 };
      const boston = { lat: 42.3601, lon: -71.0589 };

      const distance = haversine(seattle, boston);

      // Seattle to Boston is approximately 2,489 miles
      expect(distance).toBeGreaterThan(2400);
      expect(distance).toBeLessThan(2550);
    });
  });

  describe("haversineRaw()", () => {
    it("works with raw lat/lon values", () => {
      const distance = haversineRaw(39.7392, -104.9903, 39.6403, -106.3742);

      // Should be approximately 74 miles
      expect(distance).toBeGreaterThan(70);
      expect(distance).toBeLessThan(80);
    });

    it("supports unit parameter", () => {
      const miles = haversineRaw(39.7392, -104.9903, 39.6403, -106.3742, "miles");
      const km = haversineRaw(39.7392, -104.9903, 39.6403, -106.3742, "km");

      expect(km).toBeGreaterThan(miles);
    });
  });
});

