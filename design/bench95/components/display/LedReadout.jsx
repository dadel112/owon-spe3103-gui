import React from "react";

export function LedReadout({
  value,
  unit,
  label,
  color = "green",
  size = "md",
  digits,
  off = false,
  style,
}) {
  const fg = off
    ? `var(--led-${color}-dim)`
    : color === "amber"
    ? "var(--led-amber)"
    : color === "red"
    ? "var(--led-red)"
    : "var(--led-green)";
  const fontSize = size === "lg" ? "var(--text-readout-lg)" : size === "sm" ? "var(--text-readout-sm)" : "var(--text-readout-md)";
  const text = digits && typeof value === "number" ? value.toFixed(digits) : String(value);
  return (
    <span
      style={{
        display: "inline-block",
        position: "relative",
        background: color === "amber" ? "var(--readout-bg-amber)" : "var(--surface-readout)",
        boxShadow: "var(--bevel-in)",
        padding: "var(--space-4) var(--space-8)",
        ...style,
      }}
    >
      {label ? (
        <span style={{ display: "block", font: "var(--weight-normal) var(--text-pixel-sm)/1 var(--font-pixel)", letterSpacing: "var(--tracking-pixel)", color: fg, opacity: 0.65, marginBottom: 2 }}>
          {label}
        </span>
      ) : null}
      <span style={{ display: "flex", alignItems: "baseline", justifyContent: "flex-end", gap: "var(--space-6)" }}>
        <span style={{ font: `var(--weight-normal) ${fontSize}/1 var(--font-readout)`, letterSpacing: "var(--tracking-readout)", color: fg, textShadow: off ? "none" : `0 0 6px ${fg}` }}>
          {text}
        </span>
        {unit ? (
          <span style={{ font: "var(--weight-normal) var(--text-readout-sm)/1 var(--font-readout)", color: fg, opacity: 0.8 }}>{unit}</span>
        ) : null}
      </span>
      <span style={{ position: "absolute", inset: 2, pointerEvents: "none", background: "var(--pattern-scanlines)" }} />
    </span>
  );
}
