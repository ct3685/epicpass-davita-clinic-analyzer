interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeStyles = {
  sm: "w-4 h-4 border-2",
  md: "w-6 h-6 border-2",
  lg: "w-8 h-8 border-3",
};

export function Spinner({ size = "md", className = "" }: SpinnerProps) {
  return (
    <div
      className={`
        ${sizeStyles[size]}
        border-accent-clinic
        border-t-transparent
        rounded-full
        animate-spin
        ${className}
      `}
      role="status"
      aria-label="Loading"
    />
  );
}

/**
 * Full-page loading spinner
 */
export function LoadingScreen({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-bg-primary">
      <Spinner size="lg" />
      <p className="mt-4 text-text-muted animate-pulse">{message}</p>
    </div>
  );
}

