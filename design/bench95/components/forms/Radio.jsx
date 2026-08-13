import React from "react";

export function Radio({ checked = false, onChange, label, name, disabled = false, style }) {
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
        role="radio"
        aria-checked={checked}
        data-name={name}
        onClick={() => !disabled && onChange && onChange(true)}
        style={{
          width: 12,
          height: 12,
          flex: "0 0 auto",
          borderRadius: "50%",
          background: disabled ? "var(--surface-field-disabled)" : "var(--surface-field)",
          boxShadow: "inset 1px 1px 0 0 var(--grey-500),inset -1px -1px 0 0 var(--grey-white),inset 2px 2px 0 0 var(--black),inset -2px -2px 0 0 var(--grey-100)",
          display: "grid",
          placeItems: "center",
        }}
      >
        {checked ? (
          <span style={{ width: 4, height: 4, borderRadius: "50%", background: disabled ? "var(--grey-500)" : "var(--black)" }} />
        ) : null}
      </span>
      {label}
    </label>
  );
}
