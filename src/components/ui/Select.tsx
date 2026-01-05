import { type SelectHTMLAttributes, forwardRef } from "react";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options: { value: string; label: string }[];
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ options, placeholder, className = "", ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={`
          w-full
          px-3 py-2.5
          bg-bg-tertiary
          border border-border
          rounded-lg
          text-text-primary
          text-sm
          cursor-pointer
          transition-all duration-200
          focus:outline-none
          focus:border-accent-primary
          focus:ring-2
          focus:ring-accent-primary/20
          ${className}
        `}
        {...props}
      >
        {placeholder && (
          <option value="" className="bg-bg-secondary text-text-muted">
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            className="bg-bg-secondary text-text-primary"
          >
            {option.label}
          </option>
        ))}
      </select>
    );
  }
);

Select.displayName = "Select";

