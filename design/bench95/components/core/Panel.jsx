import React from "react";

export function Panel({ label, children, inset = false, style, bodyStyle }) {
  return (
    <div style={{ position: "relative", minWidth: 0, ...style }}>
      <div
        style={{
          position: "relative",
          boxShadow: inset ? "var(--bevel-in-thin)" : "var(--bevel-out-thin)",
          padding: "var(--space-8)",
          paddingTop: label ? "var(--space-11)" : "var(--space-8)",
          ...bodyStyle,
        }}
      >
        {label ? (
          <span
            style={{
              position: "absolute",
              top: -6,
              left: "var(--space-8)",
              padding: "0 var(--space-4)",
              background: "var(--surface-window)",
              font: "var(--type-groupbox)",
              whiteSpace: "nowrap",
            }}
          >
            {label}
          </span>
        ) : null}
        {children}
      </div>
    </div>
  );
}
