import React from "react";

const arrow = (dir) => (
  <span
    style={{
      width: 0,
      height: 0,
      borderLeft: "3px solid transparent",
      borderRight: "3px solid transparent",
      [dir === "up" ? "borderBottom" : "borderTop"]: "3px solid var(--black)",
    }}
  />
);

export function NumberSpinner({
  value = 0,
  onChange,
  step = 0.1,
  min = 0,
  max = 100,
  decimals = 3,
  unit,
  disabled = false,
  width = 96,
  style,
}) {
  const clamp = (n) => Math.min(max, Math.max(min, Number(n.toFixed(decimals))));
  const bump = (d) => !disabled && onChange && onChange(clamp(Number(value) + d * step));
  return (
    <span style={{ display: "inline-flex", height: "var(--control-h)", width, ...style }}>
      <span
        style={{
          flex: "1 1 auto",
          display: "flex",
          alignItems: "center",
          justifyContent: "flex-end",
          gap: "var(--space-2)",
          background: disabled ? "var(--surface-field-disabled)" : "var(--surface-field)",
          boxShadow: "var(--bevel-in)",
          padding: "0 var(--space-3)",
        }}
      >
        <input
          value={Number(value).toFixed(decimals)}
          disabled={disabled}
          onChange={(e) => onChange && onChange(clamp(Number(e.target.value) || 0))}
          style={{
            width: "100%",
            minWidth: 0,
            border: 0,
            outline: 0,
            background: "transparent",
            textAlign: "right",
            font: "var(--weight-normal) var(--text-lg)/1 var(--font-mono)",
            color: disabled ? "var(--text-disabled)" : "var(--text-body)",
          }}
        />
        {unit ? <span style={{ font: "var(--type-label)", color: "var(--grey-700)" }}>{unit}</span> : null}
      </span>
      <span style={{ display: "flex", flexDirection: "column", width: 17, flex: "0 0 auto" }}>
        {["up", "down"].map((d) => (
          <button
            key={d}
            type="button"
            aria-label={d}
            disabled={disabled}
            onClick={() => bump(d === "up" ? 1 : -1)}
            style={{
              flex: 1,
              border: 0,
              padding: 0,
              background: "var(--surface-window)",
              boxShadow: "var(--bevel-out)",
              display: "grid",
              placeItems: "center",
              cursor: "default",
            }}
          >
            {arrow(d)}
          </button>
        ))}
      </span>
    </span>
  );
}
