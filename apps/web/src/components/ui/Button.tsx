import * as React from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger" | "subtle";
  size?: "sm" | "md" | "lg" | "icon";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading = false, children, disabled, ...props }, ref) => {
    const variants = {
      primary: "bg-indigo-600 text-white hover:bg-indigo-700 active:bg-indigo-800 shadow-sm disabled:bg-indigo-300",
      secondary: "bg-slate-900 text-white hover:bg-slate-800 active:bg-slate-950 disabled:bg-slate-400",
      outline: "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 active:bg-slate-100 disabled:opacity-50",
      ghost: "text-slate-600 hover:bg-slate-100 active:bg-slate-200 hover:text-slate-900 disabled:opacity-50",
      danger: "bg-rose-600 text-white hover:bg-rose-700 active:bg-rose-800 disabled:bg-rose-300",
      subtle: "bg-indigo-50 text-indigo-700 hover:bg-indigo-100 active:bg-indigo-200 disabled:opacity-50",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs font-medium rounded-md",
      md: "h-9 px-4 text-sm font-medium rounded-lg",
      lg: "h-11 px-6 text-base font-medium rounded-lg",
      icon: "h-9 w-9 p-0 flex items-center justify-center rounded-lg",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          "inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed select-none gap-2",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {isLoading && <Loader2 className="w-4 h-4 animate-spin text-current" />}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
