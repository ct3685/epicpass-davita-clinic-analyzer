interface ConnectionLegendProps {
  itemType: "clinics" | "resorts" | "facilities";
  count: number;
  clinicCount?: number;
  hospitalCount?: number;
}

/**
 * Legend showing connection line color meanings
 * Appears in bottom-left corner when connections are displayed
 */
export function ConnectionLegend({
  itemType,
  count,
  clinicCount,
  hospitalCount,
}: ConnectionLegendProps) {
  if (count === 0) return null;

  const isFacilities = itemType === "facilities";

  return (
    <div className="absolute bottom-4 left-4 z-[1000] map-legend">
      <div className="text-xs font-medium text-text-primary mb-2">
        {count} nearby {itemType}
      </div>
      <div className="space-y-1.5">
        {isFacilities ? (
          // Show clinic/hospital color coding for facilities
          <>
            {(clinicCount ?? 0) > 0 && (
              <div className="map-legend-item">
                <div
                  className="map-legend-line"
                  style={{ backgroundColor: "#22d3ee" }}
                />
                <span>🏥 Clinics ({clinicCount})</span>
              </div>
            )}
            {(hospitalCount ?? 0) > 0 && (
              <div className="map-legend-item">
                <div
                  className="map-legend-line"
                  style={{ backgroundColor: "#f87171" }}
                />
                <span>🚑 Hospitals ({hospitalCount})</span>
              </div>
            )}
          </>
        ) : (
          // Show rank-based legend for resorts
          <>
            <div className="map-legend-item">
              <div className="map-legend-line map-legend-line--nearest" />
              <span>Nearest</span>
            </div>
            {count > 1 && (
              <div className="map-legend-item">
                <div className="map-legend-line map-legend-line--close" />
                <span>2nd-3rd closest</span>
              </div>
            )}
            {count > 3 && (
              <div className="map-legend-item">
                <div className="map-legend-line map-legend-line--other" />
                <span>Others</span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
