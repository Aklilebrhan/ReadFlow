import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info" | "outline";
}

export function Badge({ className, variant = "default", children, ...props }: BadgeProps) {
  const variants = {
    default: "bg-slate-100 text-slate-800 border-slate-200",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    danger: "bg-rose-50 text-rose-700 border-rose-200",
    info: "bg-indigo-50 text-indigo-700 border-indigo-200",
    outline: "bg-transparent text-slate-700 border-slate-300",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function ProcessingStatusBadge({ status, progress }: { status: string; progress?: number }) {
  switch (status) {
    case "Ready":
      return (
        <Badge variant="success">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          Ready
        </Badge>
      );
    case "Failed":
      return (
        <Badge variant="danger">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
          Failed
        </Badge>
      );
    case "Extracting":
    case "Processing":
    case "Indexing":
    case "Uploaded":
      return (
        <Badge variant="info">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-ping" />
          {status} {progress ? `(${progress}%)` : ""}
        </Badge>
      );
    default:
      return <Badge>{status}</Badge>;
  }
}
