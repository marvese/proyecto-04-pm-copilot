import React from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  label?: string;
}

export function LoadingSpinner({ size = "md", label }: LoadingSpinnerProps) {
  const px = { sm: 16, md: 24, lg: 40 }[size];
  const border = Math.max(2, Math.round(px / 8));
  return (
    <div
      style={{ display: "inline-flex", alignItems: "center", gap: 8 }}
      aria-label={label ?? "Loading"}
    >
      <div
        style={{
          width: px,
          height: px,
          border: `${border}px solid #e0e0e0`,
          borderTopColor: "#0066cc",
          borderRadius: "50%",
          animation: "pmcp-spin 0.8s linear infinite",
        }}
      />
      {label && <span style={{ color: "#666", fontSize: 14 }}>{label}</span>}
      <style>{`@keyframes pmcp-spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
