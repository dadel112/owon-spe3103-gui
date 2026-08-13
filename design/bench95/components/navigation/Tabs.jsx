import React from "react";

export function Tabs({ tabs = [], value, onChange, children, style, bodyStyle }) {
  const list = tabs.map((t) => (typeof t === "string" ? { value: t, label: t } : t));
  const active = value ?? list[0]?.value;
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: 0, ...style }}>
      <div style={{ display: "flex", gap: 1, position: "relative", zIndex: 2, paddingLeft: "var(--space-2)" }}>
        {list.map((t) => {
          const on = t.value === active;
          return (
            <button
              key={t.value}
              type="button"
              onClick={() => onChange && onChange(t.value)}
              style={{
                border: 0,
                height: "var(--tab-h)",
                marginTop: on ? 0 : 2,
                padding: `0 var(--space-8) ${on ? 2 : 0}px`,
                background: "var(--surface-window)",
                boxShadow: "inset 1px 1px 0 0 var(--grey-white),inset -1px 0 0 0 var(--grey-500),inset -2px 0 0 0 var(--black)",
                font: "var(--type-menu)",
                cursor: "default",
                position: "relative",
                top: on ? 0 : 0,
              }}
            >
              {t.label}
            </button>
          );
        })}
      </div>
      <div style={{ flex: "1 1 auto", minHeight: 0, marginTop: -2, boxShadow: "var(--bevel-out-thin)", background: "var(--surface-window)", padding: "var(--space-8)", ...bodyStyle }}>
        {children}
      </div>
    </div>
  );
}
