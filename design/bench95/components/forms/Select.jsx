import React from "react";

export function Select({ value, options = [], onChange, disabled = false, width = 140, style }) {
  const [open, setOpen] = React.useState(false);
  const list = options.map((o) => (typeof o === "string" ? { value: o, label: o } : o));
  const current = list.find((o) => o.value === value) || list[0] || { label: "" };
  return (
    <span style={{ position: "relative", display: "inline-block", width, ...style }}>
      <span
        onClick={() => !disabled && setOpen(!open)}
        style={{
          display: "flex",
          alignItems: "center",
          height: "var(--control-h)",
          background: disabled ? "var(--surface-field-disabled)" : "var(--surface-field)",
          boxShadow: "var(--bevel-in)",
          cursor: "default",
          padding: "0 0 0 var(--space-3)",
        }}
      >
        <span
          style={{
            flex: 1,
            font: "var(--type-label)",
            color: disabled ? "var(--text-disabled)" : "var(--text-body)",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {current.label}
        </span>
        <span
          style={{
            width: 17,
            height: 17,
            margin: 2,
            background: "var(--surface-window)",
            boxShadow: open ? "var(--bevel-out-pressed)" : "var(--bevel-out)",
            display: "grid",
            placeItems: "center",
            flex: "0 0 auto",
          }}
        >
          <span style={{ width: 0, height: 0, borderLeft: "3px solid transparent", borderRight: "3px solid transparent", borderTop: "3px solid var(--black)" }} />
        </span>
      </span>
      {open && !disabled ? (
        <span
          style={{
            position: "absolute",
            top: "calc(var(--control-h) - 1px)",
            left: 0,
            right: 0,
            zIndex: 20,
            background: "var(--surface-field)",
            boxShadow: "var(--bevel-outline)",
            maxHeight: 132,
            overflowY: "auto",
            display: "block",
          }}
        >
          {list.map((o) => {
            const sel = o.value === current.value;
            return (
              <span
                key={o.value}
                onClick={() => {
                  setOpen(false);
                  onChange && onChange(o.value);
                }}
                style={{
                  display: "block",
                  font: "var(--type-label)",
                  padding: "var(--space-2) var(--space-3)",
                  background: sel ? "var(--surface-selected)" : "transparent",
                  color: sel ? "var(--text-on-selected)" : "var(--text-body)",
                  cursor: "default",
                }}
              >
                {o.label}
              </span>
            );
          })}
        </span>
      ) : null}
    </span>
  );
}
