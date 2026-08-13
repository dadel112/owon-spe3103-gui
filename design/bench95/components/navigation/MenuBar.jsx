import React from "react";

export function MenuBar({ menus = [], onSelect, style }) {
  const [open, setOpen] = React.useState(null);
  return (
    <div
      onMouseLeave={() => setOpen(null)}
      style={{
        display: "flex",
        height: "var(--menubar-h)",
        alignItems: "stretch",
        background: "var(--surface-menu)",
        flex: "0 0 auto",
        position: "relative",
        zIndex: 40,
        ...style,
      }}
    >
      {menus.map((m) => {
        const on = open === m.label;
        return (
          <div key={m.label} style={{ position: "relative" }}>
            <button
              type="button"
              onClick={() => setOpen(on ? null : m.label)}
              onMouseEnter={() => open && setOpen(m.label)}
              style={{
                height: "100%",
                border: 0,
                padding: "0 var(--space-8)",
                font: "var(--type-menu)",
                background: on ? "var(--surface-selected)" : "transparent",
                color: on ? "var(--text-on-selected)" : "var(--text-body)",
                cursor: "default",
              }}
            >
              <span style={{ textDecoration: "underline", textDecorationSkipInk: "none" }}>{m.label.slice(0, 1)}</span>
              {m.label.slice(1)}
            </button>
            {on ? (
              <div
                style={{
                  position: "absolute",
                  top: "100%",
                  left: 0,
                  minWidth: 148,
                  background: "var(--surface-menu)",
                  boxShadow: "var(--bevel-out), var(--shadow-hard)",
                  padding: "var(--space-2)",
                }}
              >
                {(m.items || []).map((it, i) =>
                  it === "-" ? (
                    <div key={i} style={{ height: 2, margin: "var(--space-2) var(--space-1)", boxShadow: "var(--bevel-in-thin)" }} />
                  ) : (
                    <button
                      key={i}
                      type="button"
                      disabled={it.disabled}
                      onClick={() => {
                        setOpen(null);
                        onSelect && onSelect(m.label, it.label ?? it);
                      }}
                      style={{
                        display: "flex",
                        width: "100%",
                        border: 0,
                        background: "transparent",
                        font: "var(--type-menu)",
                        color: it.disabled ? "var(--text-disabled)" : "var(--text-body)",
                        textShadow: it.disabled ? "1px 1px 0 var(--text-disabled-emboss)" : "none",
                        padding: "var(--space-3) var(--space-16) var(--space-3) var(--space-8)",
                        alignItems: "center",
                        gap: "var(--space-16)",
                        cursor: "default",
                        textAlign: "left",
                      }}
                      onMouseEnter={(e) => {
                        if (it.disabled) return;
                        e.currentTarget.style.background = "var(--surface-selected)";
                        e.currentTarget.style.color = "var(--text-on-selected)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = "transparent";
                        e.currentTarget.style.color = it.disabled ? "var(--text-disabled)" : "var(--text-body)";
                      }}
                    >
                      <span style={{ flex: 1 }}>{it.label ?? it}</span>
                      {it.shortcut ? <span style={{ opacity: 0.75 }}>{it.shortcut}</span> : null}
                    </button>
                  )
                )}
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
