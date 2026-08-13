import React from "react";

export function ProgressBar({ value = 0, max = 100, chunky = true, height = 18, label, style }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const chunks = Math.round((pct / 100) * 20);
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "var(--space-6)", ...style }}>
      <span
        style={{
          position: "relative",
          flex: "1 1 auto",
          height,
          background: "var(--surface-trough)",
          boxShadow: "var(--bevel-in)",
          padding: 3,
          display: "flex",
          gap: 2,
          overflow: "hidden",
        }}
      >
        {chunky ? (
          Array.from({ length: 20 }).map((_, i) => (
            <span key={i} style={{ flex: "1 1 0", background: i < chunks ? "var(--surface-titlebar)" : "transparent" }} />
          ))
        ) : (
          <span style={{ position: "absolute", left: 3, top: 3, bottom: 3, width: `calc(${pct}% - 6px)`, background: "var(--surface-titlebar)" }} />
        )}
      </span>
      {label !== undefined ? <span style={{ font: "var(--type-label)", minWidth: 32, textAlign: "right" }}>{label}</span> : null}
    </span>
  );
}
