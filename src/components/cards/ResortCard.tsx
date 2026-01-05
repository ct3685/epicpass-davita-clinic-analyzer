import type { Resort, ClinicWithDistance, HospitalWithDistance } from "@/types";
import { useSelectionStore } from "@/stores";
import { useSettingsStore } from "@/stores/settingsStore";
import { Badge, DistanceBadge, PassBadge } from "@/components/ui/Badge";
import { formatDistance } from "@/utils/formatters";
import { trackItemSelect } from "@/utils/analytics";

interface ResortCardProps {
  resort: Resort;
  userDistance?: number;
  nearestClinics?: ClinicWithDistance[];
  nearestHospitals?: HospitalWithDistance[];
  onDirectionsClick?: (
    fromLat: number,
    fromLon: number,
    toLat: number,
    toLon: number,
    fromName: string,
    toName: string,
    distance: number
  ) => void;
}

export function ResortCard({
  resort,
  userDistance,
  nearestClinics = [],
  nearestHospitals = [],
  onDirectionsClick,
}: ResortCardProps) {
  const { expandedId, toggleExpand } = useSelectionStore();
  const { distanceUnit } = useSettingsStore();

  const isExpanded = expandedId === resort.id;
  const nearestClinic = nearestClinics[0];
  const nearestHospital = nearestHospitals[0];

  const handleClick = () => {
    toggleExpand(resort.id);
    if (!isExpanded) {
      trackItemSelect("resort", resort.name, resort.state);
    }
  };

  const handleClinicClick = (
    e: React.MouseEvent,
    clinic: ClinicWithDistance
  ) => {
    e.stopPropagation();
    if (onDirectionsClick) {
      onDirectionsClick(
        resort.lat,
        resort.lon,
        clinic.lat,
        clinic.lon,
        resort.name,
        clinic.facility,
        clinic.distance
      );
    }
  };

  const handleHospitalClick = (
    e: React.MouseEvent,
    hospital: HospitalWithDistance
  ) => {
    e.stopPropagation();
    if (onDirectionsClick) {
      onDirectionsClick(
        resort.lat,
        resort.lon,
        hospital.lat,
        hospital.lon,
        resort.name,
        hospital.name,
        hospital.distance
      );
    }
  };

  return (
    <div
      data-resort-id={resort.id}
      onClick={handleClick}
      className={`
        p-4 rounded-lg
        bg-bg-card border border-border
        cursor-pointer
        transition-all duration-200
        hover:border-accent-primary
        ${
          isExpanded
            ? "border-accent-primary ring-1 ring-accent-primary/20"
            : ""
        }
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 min-w-0">
          <span className="font-semibold text-text-primary">
            🏔️ {resort.name}
          </span>
          <span
            className={`text-xs transition-transform duration-200 flex-shrink-0 mt-0.5 ${
              isExpanded ? "rotate-180" : ""
            }`}
          >
            ▼
          </span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <PassBadge pass={resort.passNetwork} />
          <Badge>{resort.state}</Badge>
        </div>
      </div>

      {/* Meta */}
      <div className="mt-2 flex flex-wrap items-center gap-2 text-sm">
        {userDistance !== undefined && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-accent-clinic/20 border border-accent-clinic/30 text-accent-clinic text-xs font-semibold">
            📍 {formatDistance(userDistance, distanceUnit)} away
          </span>
        )}
        {nearestClinic && (
          <DistanceBadge miles={nearestClinic.distance} icon="🏥" />
        )}
        {nearestHospital && (
          <DistanceBadge miles={nearestHospital.distance} icon="🚑" />
        )}
      </div>

      {/* Expanded Content */}
      {isExpanded &&
        (nearestClinics.length > 0 || nearestHospitals.length > 0) && (
          <div className="mt-4 pt-4 border-t border-border space-y-4">
            {/* Nearest Clinics */}
            {nearestClinics.length > 0 && (
              <div>
                <p className="text-xs text-text-muted mb-2 font-medium flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  Nearest Dialysis Clinics:
                </p>
                <div className="space-y-2">
                  {nearestClinics.slice(0, 3).map((clinic, i) => (
                    <div
                      key={clinic.ccn}
                      onClick={(e) => handleClinicClick(e, clinic)}
                      className="flex items-center justify-between p-2 rounded-lg 
                      transition-all duration-200 cursor-pointer
                      bg-bg-tertiary hover:bg-cyan-500/10 border border-transparent hover:border-cyan-500/30"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-text-primary truncate">
                          {i + 1}. {clinic.facility}
                        </div>
                        <div className="text-xs text-text-muted">
                          {clinic.city}, {clinic.state}
                        </div>
                      </div>
                      <span className="text-sm font-semibold ml-2 text-cyan-400">
                        {formatDistance(clinic.distance, distanceUnit)} →
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Nearest Hospitals */}
            {nearestHospitals.length > 0 && (
              <div>
                <p className="text-xs text-text-muted mb-2 font-medium flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-red-400"></span>
                  Nearest Hospitals:
                </p>
                <div className="space-y-2">
                  {nearestHospitals.slice(0, 3).map((hospital, i) => (
                    <div
                      key={hospital.id}
                      onClick={(e) => handleHospitalClick(e, hospital)}
                      className="flex items-center justify-between p-2 rounded-lg 
                      transition-all duration-200 cursor-pointer
                      bg-bg-tertiary hover:bg-red-500/10 border border-transparent hover:border-red-500/30"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-text-primary truncate">
                          {i + 1}. {hospital.name}
                        </div>
                        <div className="text-xs text-text-muted">
                          {hospital.city}, {hospital.state}
                          {hospital.traumaLevel && (
                            <span className="ml-1 text-red-400">
                              • Level {hospital.traumaLevel} Trauma
                            </span>
                          )}
                        </div>
                      </div>
                      <span className="text-sm font-semibold ml-2 text-red-400">
                        {formatDistance(hospital.distance, distanceUnit)} →
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
    </div>
  );
}
