import { type ButtonHTMLAttributes, forwardRef } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-gradient-to-r from-accent-primary to-accent-tertiary text-white shadow-glow-pink hover:brightness-110",
  secondary:
    "bg-bg-tertiary border border-border text-text-primary hover:bg-bg-card hover:border-accent-primary",
  ghost:
    "bg-transparent text-text-secondary hover:bg-bg-tertiary hover:text-text-primary",
  danger:
    "bg-accent-danger text-white hover:brightness-110",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "px-3 py-2 text-xs gap-1.5 min-h-[36px]",
  md: "px-4 py-2.5 text-sm gap-2 min-h-[44px]", // WCAG 2.5.5 touch target
  lg: "px-6 py-3 text-base gap-2.5 min-h-[48px]",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "secondary",
      size = "md",
      isLoading = false,
      leftIcon,
      rightIcon,
      disabled,
      className = "",
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`
          inline-flex items-center justify-center
          font-medium rounded-lg
          transition-all duration-200
          disabled:opacity-50 disabled:cursor-not-allowed
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${className}
        `}
        {...props}
      >
        {isLoading ? (
          <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        ) : (
          <>
            {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = "Button";

