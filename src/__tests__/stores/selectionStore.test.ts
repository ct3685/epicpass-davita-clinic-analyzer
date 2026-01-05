import { describe, it, expect, beforeEach } from "vitest";
import { useSelectionStore } from "@/stores/selectionStore";

describe("selectionStore", () => {
  beforeEach(() => {
    // Reset store to defaults before each test
    useSelectionStore.getState().clearSelection();
    useSelectionStore.getState().setMode("resorts");
  });

  describe("initial state", () => {
    it("has correct default values", () => {
      const state = useSelectionStore.getState();

      expect(state.mode).toBe("resorts");
      expect(state.selectedId).toBeNull();
      expect(state.expandedId).toBeNull();
      expect(state.showAllExpanded).toBe(false);
    });
  });

  describe("setMode()", () => {
    it("changes view mode", () => {
      useSelectionStore.getState().setMode("clinics");
      expect(useSelectionStore.getState().mode).toBe("clinics");
    });

    it("clears selection when mode changes", () => {
      useSelectionStore.getState().select("test-id");
      useSelectionStore.getState().expand("test-id");

      useSelectionStore.getState().setMode("hospitals");

      expect(useSelectionStore.getState().selectedId).toBeNull();
      expect(useSelectionStore.getState().expandedId).toBeNull();
    });
  });

  describe("select()", () => {
    it("sets selected id", () => {
      useSelectionStore.getState().select("resort-1");
      expect(useSelectionStore.getState().selectedId).toBe("resort-1");
    });

    it("clears selection with null", () => {
      useSelectionStore.getState().select("resort-1");
      useSelectionStore.getState().select(null);
      expect(useSelectionStore.getState().selectedId).toBeNull();
    });
  });

  describe("expand()", () => {
    it("sets expanded id", () => {
      useSelectionStore.getState().expand("resort-1");
      expect(useSelectionStore.getState().expandedId).toBe("resort-1");
    });

    it("resets showAllExpanded when expanding", () => {
      useSelectionStore.getState().setShowAllExpanded(true);
      useSelectionStore.getState().expand("resort-1");
      expect(useSelectionStore.getState().showAllExpanded).toBe(false);
    });
  });

  describe("toggleExpand()", () => {
    it("expands when collapsed", () => {
      useSelectionStore.getState().toggleExpand("resort-1");
      expect(useSelectionStore.getState().expandedId).toBe("resort-1");
    });

    it("collapses when already expanded", () => {
      useSelectionStore.getState().expand("resort-1");
      useSelectionStore.getState().toggleExpand("resort-1");
      expect(useSelectionStore.getState().expandedId).toBeNull();
    });

    it("expands different item when one is expanded", () => {
      useSelectionStore.getState().expand("resort-1");
      useSelectionStore.getState().toggleExpand("resort-2");
      expect(useSelectionStore.getState().expandedId).toBe("resort-2");
    });
  });

  describe("setShowAllExpanded()", () => {
    it("sets showAllExpanded state", () => {
      useSelectionStore.getState().setShowAllExpanded(true);
      expect(useSelectionStore.getState().showAllExpanded).toBe(true);
    });
  });

  describe("clearSelection()", () => {
    it("clears all selection state", () => {
      useSelectionStore.getState().select("resort-1");
      useSelectionStore.getState().expand("resort-1");
      useSelectionStore.getState().setShowAllExpanded(true);

      useSelectionStore.getState().clearSelection();

      const state = useSelectionStore.getState();
      expect(state.selectedId).toBeNull();
      expect(state.expandedId).toBeNull();
      expect(state.showAllExpanded).toBe(false);
    });
  });
});

