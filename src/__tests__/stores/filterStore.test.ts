import { describe, it, expect, beforeEach } from "vitest";
import { useFilterStore } from "@/stores/filterStore";

describe("filterStore", () => {
  beforeEach(() => {
    // Reset store to defaults before each test
    useFilterStore.getState().reset();
  });

  describe("initial state", () => {
    it("has correct default values", () => {
      const state = useFilterStore.getState();

      expect(state.searchQuery).toBe("");
      expect(state.selectedState).toBeNull();
      expect(state.maxDistance).toBe(100);
      expect(state.passNetworks.has("epic")).toBe(true);
      expect(state.passNetworks.has("ikon")).toBe(true);
      expect(state.careTypes.has("dialysis")).toBe(true);
      expect(state.careTypes.has("hospital")).toBe(true);
    });
  });

  describe("setSearchQuery()", () => {
    it("updates search query", () => {
      useFilterStore.getState().setSearchQuery("vail");
      expect(useFilterStore.getState().searchQuery).toBe("vail");
    });

    it("handles empty string", () => {
      useFilterStore.getState().setSearchQuery("test");
      useFilterStore.getState().setSearchQuery("");
      expect(useFilterStore.getState().searchQuery).toBe("");
    });
  });

  describe("setSelectedState()", () => {
    it("sets selected state", () => {
      useFilterStore.getState().setSelectedState("CO");
      expect(useFilterStore.getState().selectedState).toBe("CO");
    });

    it("clears state with null", () => {
      useFilterStore.getState().setSelectedState("CO");
      useFilterStore.getState().setSelectedState(null);
      expect(useFilterStore.getState().selectedState).toBeNull();
    });
  });

  describe("setMaxDistance()", () => {
    it("updates max distance", () => {
      useFilterStore.getState().setMaxDistance(50);
      expect(useFilterStore.getState().maxDistance).toBe(50);
    });
  });

  describe("togglePassNetwork()", () => {
    it("removes pass network when toggled", () => {
      useFilterStore.getState().togglePassNetwork("epic");
      expect(useFilterStore.getState().passNetworks.has("epic")).toBe(false);
      expect(useFilterStore.getState().passNetworks.has("ikon")).toBe(true);
    });

    it("adds pass network when toggled back", () => {
      useFilterStore.getState().togglePassNetwork("epic");
      useFilterStore.getState().togglePassNetwork("epic");
      expect(useFilterStore.getState().passNetworks.has("epic")).toBe(true);
    });

    it("prevents removing last pass network", () => {
      useFilterStore.getState().togglePassNetwork("epic");
      useFilterStore.getState().togglePassNetwork("ikon"); // Should be prevented
      expect(useFilterStore.getState().passNetworks.has("ikon")).toBe(true);
    });
  });

  describe("toggleCareType()", () => {
    it("removes care type when toggled", () => {
      useFilterStore.getState().toggleCareType("dialysis");
      expect(useFilterStore.getState().careTypes.has("dialysis")).toBe(false);
    });

    it("prevents removing last care type", () => {
      useFilterStore.getState().toggleCareType("dialysis");
      useFilterStore.getState().toggleCareType("hospital"); // Should be prevented
      expect(useFilterStore.getState().careTypes.has("hospital")).toBe(true);
    });
  });

  describe("setPassNetworks()", () => {
    it("sets pass networks from array", () => {
      useFilterStore.getState().setPassNetworks(["ikon"]);
      expect(useFilterStore.getState().passNetworks.has("epic")).toBe(false);
      expect(useFilterStore.getState().passNetworks.has("ikon")).toBe(true);
    });
  });

  describe("setCareTypes()", () => {
    it("sets care types from array", () => {
      useFilterStore.getState().setCareTypes(["hospital"]);
      expect(useFilterStore.getState().careTypes.has("dialysis")).toBe(false);
      expect(useFilterStore.getState().careTypes.has("hospital")).toBe(true);
    });
  });

  describe("reset()", () => {
    it("resets all filters to defaults", () => {
      // Change all filters
      const store = useFilterStore.getState();
      store.setSearchQuery("test");
      store.setSelectedState("CO");
      store.setMaxDistance(25);
      store.togglePassNetwork("epic");

      // Reset
      useFilterStore.getState().reset();

      // Verify defaults restored
      const state = useFilterStore.getState();
      expect(state.searchQuery).toBe("");
      expect(state.selectedState).toBeNull();
      expect(state.maxDistance).toBe(100);
      expect(state.passNetworks.has("epic")).toBe(true);
      expect(state.passNetworks.has("ikon")).toBe(true);
    });
  });
});

