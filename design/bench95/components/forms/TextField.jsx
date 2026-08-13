import React from "react";

export function TextField({
  value,
  onChange,
  placeholder,
  disabled = false,
  readOnly = false,
  align = "left",
  mono = false,
  width,
  style,
  ...rest
}) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: "var(--control-h)",
        width,
        background: disabled ? "var(--surface-field-disabled)" : "var(--surface-field)",
        boxShadow: "var(--bevel-in)",
        padding: "0 var(--space-2)",
        ...style,
      }}
    >
      <input
        value={value}
        onChange={(e) => onChange && onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        readOnly={readOnly}
        style={{
          width: "100%",
          border: 0,
          outline: 0,
          background: "transparent",
          font: mono ? "var(--weight-normal) var(--text-lg)/1 var(--font-mono)" : "var(--type-label)",
          color: disabled ? "var(--text-disabled)" : "var(--text-body)",
          textAlign: align,
          padding: "0 var(--space-1)",
        }}
        {...rest}
      />
    </span>
  );
}
