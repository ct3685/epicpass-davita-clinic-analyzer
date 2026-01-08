/**
 * Data freshness indicator showing when data was last verified
 */

interface FreshnessIndicatorProps {
  lastVerified?: string;
  sourceUrl?: string;
  className?: string;
}

/**
 * Calculate freshness level based on date
 */
function getFreshnessLevel(dateStr: string): "fresh" | "stale" | "old" {
  const date = new Date(dateStr);
  const now = new Date();
  const daysDiff = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  
  if (daysDiff < 30) return "fresh";
  if (daysDiff < 90) return "stale";
  return "old";
}

export function FreshnessIndicator({
  lastVerified,
  sourceUrl,
  className = "",
}: FreshnessIndicatorProps) {
  if (!lastVerified) {
    return (
      <span className={`text-xs text-text-muted ${className}`}>
        ⚠️ Not yet verified
      </span>
    );
  }

  const level = getFreshnessLevel(lastVerified);
  
  const levelConfig = {
    fresh: {
      icon: "✓",
      color: "text-green-400",
      label: "Recently verified",
    },
    stale: {
      icon: "⏳",
      color: "text-yellow-400", 
      label: "May be outdated",
    },
    old: {
      icon: "⚠️",
      color: "text-orange-400",
      label: "Verify before use",
    },
  };

  const config = levelConfig[level];

  return (
    <span className={`text-xs ${config.color} ${className}`}>
      {config.icon} Verified: {lastVerified}
      {sourceUrl && (
        <>
          {" "}•{" "}
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="hover:underline"
          >
            Source
          </a>
        </>
      )}
    </span>
  );
}

/**
 * Compact badge variant
 */
export function FreshnessBadge({ lastVerified }: { lastVerified?: string }) {
  if (!lastVerified) {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 text-xs rounded bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
        ⚠️ Unverified
      </span>
    );
  }

  const level = getFreshnessLevel(lastVerified);
  
  const styles = {
    fresh: "bg-green-500/20 text-green-400 border-green-500/30",
    stale: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    old: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  };

  const icons = {
    fresh: "✓",
    stale: "⏳",
    old: "⚠️",
  };

  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 text-xs rounded border ${styles[level]}`}>
      {icons[level]} {lastVerified}
    </span>
  );
}
