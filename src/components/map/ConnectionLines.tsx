import { Polyline } from "react-leaflet";

/**
 * Connection destination with coordinates, rank, and optional item type
 */
interface ConnectionDestination {
  lat: number;
  lon: number;
  rank: number;
  /** Item type for color coding (clinic=cyan, hospital=red, resort=green) */
  itemType?: "clinic" | "hospital" | "resort";
}

interface ConnectionLinesProps {
  /** Origin point coordinates */
  origin: { lat: number; lon: number };
  /** Array of destination points with rank (0-indexed) */
  destinations: ConnectionDestination[];
  /** Optional highlighted destination index (-1 for none) */
  highlightedIndex?: number;
}

/**
 * Get line color based on item type
 */
function getItemColor(itemType?: "clinic" | "hospital" | "resort") {
  switch (itemType) {
    case "clinic":
      return "#22d3ee"; // Cyan for clinics
    case "hospital":
      return "#f87171"; // Red for hospitals
    case "resort":
      return "#4ade80"; // Green for resorts
    default:
      return "#4ade80"; // Default green
  }
}

/**
 * Get line style based on rank and item type
 * - Rank 0 (nearest): Full opacity, thick
 * - Rank 1-2: Medium opacity
 * - Rank 3+: Light opacity, dashed
 */
function getLineStyle(
  rank: number,
  isHighlighted: boolean,
  itemType?: "clinic" | "hospital" | "resort"
) {
  if (isHighlighted) {
    return {
      color: "#fbbf24", // Yellow/amber for highlighted
      weight: 4,
      opacity: 1,
      dashArray: undefined,
    };
  }

  const baseColor = getItemColor(itemType);

  if (rank === 0) {
    return {
      color: baseColor,
      weight: 3,
      opacity: 0.9,
      dashArray: undefined,
    };
  }

  if (rank < 3) {
    return {
      color: baseColor,
      weight: 2,
      opacity: 0.6,
      dashArray: undefined,
    };
  }

  return {
    color: baseColor,
    weight: 2,
    opacity: 0.4,
    dashArray: "6,6",
  };
}

/**
 * Renders polylines connecting an origin point to multiple destinations.
 * Lines are color-coded by item type and rank.
 */
export function ConnectionLines({
  origin,
  destinations,
  highlightedIndex = -1,
}: ConnectionLinesProps) {
  if (!destinations.length) return null;

  return (
    <>
      {destinations.map((dest, index) => {
        const isHighlighted = index === highlightedIndex;
        const style = getLineStyle(dest.rank, isHighlighted, dest.itemType);

        return (
          <Polyline
            key={`connection-${dest.itemType || "item"}-${index}`}
            positions={[
              [origin.lat, origin.lon],
              [dest.lat, dest.lon],
            ]}
            pathOptions={{
              color: style.color,
              weight: style.weight,
              opacity: style.opacity,
              dashArray: style.dashArray,
              lineCap: "round",
              lineJoin: "round",
            }}
          />
        );
      })}
    </>
  );
}
