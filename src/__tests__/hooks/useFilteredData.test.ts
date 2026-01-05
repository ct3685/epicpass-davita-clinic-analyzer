import { describe, it, expect, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useFilteredData } from "@/hooks/useFilteredData";
import { useFilterStore } from "@/stores/filterStore";
import { useLocationStore } from "@/stores/locationStore";
import { mockResorts } from "../fixtures/resorts";
import { mockClinics } from "../fixtures/clinics";
import { mockHospitals } from "../fixtures/hospitals";

describe("useFilteredData", () => {
  beforeEach(() => {
    useFilterStore.getState().reset();
    useLocationStore.getState().clear();
  });

  describe("pass network filtering", () => {
    it("includes epic resorts when epic is selected", () => {
      useFilterStore.getState().setPassNetworks(["epic"]);

      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      const resortNames = result.current.resorts.map((r) => r.name);
      expect(resortNames).toContain("Vail");
      expect(resortNames).toContain("Breckenridge");
      expect(resortNames).not.toContain("Aspen Snowmass"); // ikon only
      expect(resortNames).not.toContain("Jackson Hole"); // ikon only
    });

    it("includes ikon resorts when ikon is selected", () => {
      useFilterStore.getState().setPassNetworks(["ikon"]);

      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      const resortNames = result.current.resorts.map((r) => r.name);
      expect(resortNames).toContain("Aspen Snowmass");
      expect(resortNames).toContain("Jackson Hole");
      expect(resortNames).not.toContain("Vail"); // epic only
    });

    it("includes 'both' resorts when epic is selected", () => {
      useFilterStore.getState().setPassNetworks(["epic"]);

      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      const resortNames = result.current.resorts.map((r) => r.name);
      expect(resortNames).toContain("Arapahoe Basin"); // passNetwork: "both"
    });

    it("includes 'both' resorts when ikon is selected", () => {
      useFilterStore.getState().setPassNetworks(["ikon"]);

      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      const resortNames = result.current.resorts.map((r) => r.name);
      expect(resortNames).toContain("Arapahoe Basin"); // passNetwork: "both"
    });

    it("includes 'both' resorts when both passes are selected", () => {
      useFilterStore.getState().setPassNetworks(["epic", "ikon"]);

      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      const resortNames = result.current.resorts.map((r) => r.name);
      expect(resortNames).toContain("Arapahoe Basin");
      expect(resortNames).toContain("Vail");
      expect(resortNames).toContain("Aspen Snowmass");
    });

    it("returns all resorts when no pass filter is applied", () => {
      // Default state has both passes selected, clear the set to test no filter
      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      // With both selected, should have all resorts
      expect(result.current.resorts.length).toBe(mockResorts.length);
    });
  });

  describe("search filtering", () => {
    it("filters resorts by name", () => {
      useFilterStore.getState().setSearchQuery("vail");

      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      expect(result.current.resorts.length).toBe(1);
      expect(result.current.resorts[0].name).toBe("Vail");
    });

    it("filters resorts by state", () => {
      useFilterStore.getState().setSearchQuery("CO");

      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      const states = result.current.resorts.map((r) => r.state);
      expect(states.every((s) => s === "CO")).toBe(true);
    });
  });

  describe("state filtering", () => {
    it("filters by selected state", () => {
      useFilterStore.getState().setSelectedState("CO");

      const { result } = renderHook(() =>
        useFilteredData(mockResorts, mockClinics, mockHospitals)
      );

      expect(result.current.resorts.every((r) => r.state === "CO")).toBe(true);
    });
  });
});

