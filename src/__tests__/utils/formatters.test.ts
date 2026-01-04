import { describe, it, expect } from "vitest";
import {
  formatDistance,
  formatAddress,
  formatPhone,
  truncate,
  getDistanceColorClass,
} from "@/utils/formatters";

describe("formatters", () => {
  describe("formatDistance()", () => {
    it("formats distance in miles with one decimal", () => {
      expect(formatDistance(97.456, "miles")).toBe("97.5 mi");
    });

    it("formats distance in kilometers", () => {
      expect(formatDistance(97.456, "km")).toBe("156.8 km");
    });

    it("handles zero distance", () => {
      expect(formatDistance(0, "miles")).toBe("0.0 mi");
    });

    it("handles small distances", () => {
      expect(formatDistance(0.1, "miles")).toBe("0.1 mi");
    });

    it("handles large distances", () => {
      expect(formatDistance(2500.789, "miles")).toBe("2500.8 mi");
    });

    it("supports custom decimal places", () => {
      expect(formatDistance(97.456, "miles", 2)).toBe("97.46 mi");
      expect(formatDistance(97.456, "km", 0)).toBe("157 km");
    });
  });

  describe("formatAddress()", () => {
    it("formats full address with zip correctly", () => {
      const result = formatAddress("123 Main St", "Denver", "CO", "80202");
      expect(result).toBe("123 Main St\nDenver, CO 80202");
    });

    it("formats address without zip", () => {
      const result = formatAddress("123 Main St", "Denver", "CO");
      expect(result).toBe("123 Main St\nDenver, CO");
    });
  });

  describe("formatPhone()", () => {
    it("formats 10-digit phone number", () => {
      expect(formatPhone("3035551234")).toBe("(303) 555-1234");
    });

    it("handles phone with dashes", () => {
      expect(formatPhone("303-555-1234")).toBe("(303) 555-1234");
    });

    it("handles phone with spaces", () => {
      expect(formatPhone("303 555 1234")).toBe("(303) 555-1234");
    });

    it("handles 11-digit phone with country code", () => {
      expect(formatPhone("13035551234")).toBe("+1 (303) 555-1234");
    });

    it("returns original for invalid length", () => {
      expect(formatPhone("12345")).toBe("12345");
    });

    it("returns original for too many digits", () => {
      expect(formatPhone("123456789012")).toBe("123456789012");
    });
  });

  describe("truncate()", () => {
    it("returns text unchanged if shorter than maxLength", () => {
      expect(truncate("Hello", 10)).toBe("Hello");
    });

    it("truncates with ellipsis if longer than maxLength", () => {
      expect(truncate("Hello World", 8)).toBe("Hello W…");
    });

    it("handles exact length", () => {
      expect(truncate("Hello", 5)).toBe("Hello");
    });

    it("handles empty string", () => {
      expect(truncate("", 5)).toBe("");
    });
  });

  describe("getDistanceColorClass()", () => {
    it("returns success class for distances under 25 miles", () => {
      expect(getDistanceColorClass(10)).toBe("text-accent-success");
      expect(getDistanceColorClass(24.9)).toBe("text-accent-success");
    });

    it("returns warning class for distances 25-75 miles", () => {
      expect(getDistanceColorClass(25)).toBe("text-accent-warning");
      expect(getDistanceColorClass(50)).toBe("text-accent-warning");
      expect(getDistanceColorClass(74.9)).toBe("text-accent-warning");
    });

    it("returns danger class for distances 75+ miles", () => {
      expect(getDistanceColorClass(75)).toBe("text-accent-danger");
      expect(getDistanceColorClass(100)).toBe("text-accent-danger");
      expect(getDistanceColorClass(200)).toBe("text-accent-danger");
    });
  });
});
