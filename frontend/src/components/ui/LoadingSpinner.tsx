import React from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  label?: string;
}

export function LoadingSpinner({ size = "md", label }: LoadingSpinnerProps) {
  // TODO: implement with CSS animation or Tailwind animate-spin
  return <div className={`spinner spinner--${size}`} aria-label={label ?? "Loading"} />;
}
