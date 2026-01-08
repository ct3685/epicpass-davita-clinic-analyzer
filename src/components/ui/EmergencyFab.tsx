import { useState } from "react";
import { track911Call } from "@/utils/analytics";

/**
 * Floating Action Button for emergency quick access
 * Always visible on mobile for instant 911 access
 */
export function EmergencyFab() {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCall911 = (e: React.MouseEvent) => {
    e.stopPropagation();
    track911Call("emergency_fab");
    window.location.href = "tel:911";
  };

  return (
    <div className="fixed bottom-20 right-4 z-40 md:hidden">
      {/* Expanded Menu */}
      {isExpanded && (
        <div className="absolute bottom-16 right-0 flex flex-col gap-2 animate-slide-up">
          {/* 911 Button */}
          <button
            onClick={handleCall911}
            className="flex items-center gap-2 px-4 py-3 rounded-full
              bg-red-600 text-white font-bold shadow-lg shadow-red-500/30
              hover:bg-red-500 active:scale-95 transition-all"
          >
            <span className="text-lg">🚨</span>
            <span>Call 911</span>
          </button>
        </div>
      )}

      {/* Main FAB */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        aria-label="Emergency options"
        aria-expanded={isExpanded}
        className={`
          w-14 h-14 rounded-full
          flex items-center justify-center
          shadow-lg transition-all duration-300
          ${isExpanded 
            ? "bg-bg-tertiary text-text-primary rotate-45" 
            : "bg-red-600 text-white shadow-red-500/30"
          }
        `}
      >
        <span className="text-2xl">{isExpanded ? "✕" : "🆘"}</span>
      </button>
    </div>
  );
}
