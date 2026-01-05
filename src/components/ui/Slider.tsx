import { type InputHTMLAttributes, forwardRef } from "react";

interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
  valueLabel?: string;
  min?: number;
  max?: number;
}

export const Slider = forwardRef<HTMLInputElement, SliderProps>(
  ({ label, valueLabel, min = 0, max = 100, className = "", ...props }, ref) => {
    return (
      <div className={`flex flex-col gap-1 ${className}`}>
        {(label || valueLabel) && (
          <div className="flex justify-between text-xs text-text-muted font-medium">
            {label && <span>{label}</span>}
            {valueLabel && (
              <span className="text-accent-primary font-semibold">
                {valueLabel}
              </span>
            )}
          </div>
        )}
        <input
          ref={ref}
          type="range"
          min={min}
          max={max}
          className={`
            w-full h-1.5 
            bg-bg-tertiary 
            rounded-full 
            appearance-none
            cursor-pointer
            
            [&::-webkit-slider-thumb]:appearance-none
            [&::-webkit-slider-thumb]:w-4
            [&::-webkit-slider-thumb]:h-4
            [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-gradient-to-r
            [&::-webkit-slider-thumb]:from-accent-primary
            [&::-webkit-slider-thumb]:to-accent-tertiary
            [&::-webkit-slider-thumb]:shadow-glow-pink
            [&::-webkit-slider-thumb]:cursor-pointer
            [&::-webkit-slider-thumb]:transition-transform
            [&::-webkit-slider-thumb]:duration-200
            [&::-webkit-slider-thumb]:hover:scale-110
            
            [&::-moz-range-thumb]:w-4
            [&::-moz-range-thumb]:h-4
            [&::-moz-range-thumb]:rounded-full
            [&::-moz-range-thumb]:bg-gradient-to-r
            [&::-moz-range-thumb]:from-accent-primary
            [&::-moz-range-thumb]:to-accent-tertiary
            [&::-moz-range-thumb]:border-none
            [&::-moz-range-thumb]:cursor-pointer
          `}
          {...props}
        />
      </div>
    );
  }
);

Slider.displayName = "Slider";

