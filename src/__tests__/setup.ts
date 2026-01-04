/**
 * Vitest test setup
 *
 * This file runs before each test file.
 */

import "@testing-library/jest-dom";
import { beforeEach } from "vitest";

// Mock window.matchMedia for theme tests
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: query === "(prefers-color-scheme: dark)",
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Mock navigator.geolocation
const mockCoords = {
  latitude: 39.7392,
  longitude: -104.9903,
  accuracy: 100,
  altitude: null,
  altitudeAccuracy: null,
  heading: null,
  speed: null,
  toJSON: () => mockCoords,
};

Object.defineProperty(navigator, "geolocation", {
  writable: true,
  value: {
    getCurrentPosition: (success: PositionCallback) => {
      const position = {
        coords: mockCoords as GeolocationCoordinates,
        timestamp: Date.now(),
        toJSON: () => position,
      };
      success(position as GeolocationPosition);
    },
    watchPosition: () => 1,
    clearWatch: () => {},
  },
});

// Mock navigator.vibrate
Object.defineProperty(navigator, "vibrate", {
  writable: true,
  value: () => true,
});

// Reset all stores between tests
beforeEach(() => {
  // Clear localStorage
  localStorage.clear();
});

