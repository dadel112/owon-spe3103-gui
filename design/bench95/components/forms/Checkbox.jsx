import React from "react";

export function Checkbox({ checked = false, onChange, label, disabled = false, style }) {
  return (
    <label
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "var(--space-6)",
        font: "var(--type-label)",
        color: disabled ? "var(--text-disabled)" : "var(--text-body)",
        textShadow: disabled ? "1px 1px 0 var(--text-disabled-emboss)" : "none",
        cursor: "default",
        userSelect: "none",
        ...style,
      }}
    >
      <span
        onClick={() => !disabled && onChange && onChange(!checked)}
        style={{
          width: 13,
          height: 13,
          flex: "0 0 auto",
          background: disabled ? "var(--surface-field-disabled)" : "var(--surface-field)",
          boxShadow: "var(--bevel-in)",
          display: "grid",
          placeItems: "center",
          position: "relative",
        }}
      >
        {checked ? (
          <span
            style={{
              width: 7,
              height: 4,
              borderLeft: "2px solid var(--black)",
              borderBottom: "2px solid var(--black)",
              transform: "rotate(-45deg) translate(1px,-1px)",
              opacity: disabled ? 0.45 : 1,
            }}
          />
        ) : null}
      </span>
      {label}
    </label>
  );
}
