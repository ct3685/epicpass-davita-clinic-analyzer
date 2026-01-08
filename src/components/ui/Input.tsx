import { type InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  leftIcon?: React.ReactNode;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ leftIcon, error, className = "", ...props }, ref) => {
    return (
      <div className="relative">
        {leftIcon && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted">
            {leftIcon}
          </span>
        )}
        <input
          ref={ref}
          className={`
            w-full
            px-4 py-3
            min-h-[44px]
            ${leftIcon ? "pl-10" : ""}
            bg-bg-tertiary
            border border-border
            rounded-lg
            text-text-primary
            placeholder:text-text-muted
            transition-all duration-200
            focus:outline-none
            focus:border-accent-primary
            focus:ring-2
            focus:ring-accent-primary/20
            ${error ? "border-accent-danger focus:border-accent-danger focus:ring-accent-danger/20" : ""}
            ${className}
          `}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-accent-danger">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

/**
 * Search input with magnifying glass icon
 */
export const SearchInput = forwardRef<
  HTMLInputElement,
  Omit<InputProps, "leftIcon">
>(({ placeholder = "Search...", ...props }, ref) => {
  return (
    <Input ref={ref} leftIcon="🔍" placeholder={placeholder} {...props} />
  );
});

SearchInput.displayName = "SearchInput";

