import React from "react";

export function ListView({ columns = [], rows = [], selectedIndex = -1, onSelect, height, mono = false, style }) {
  return (
    <div
      style={{
        background: "var(--surface-field)",
        boxShadow: "var(--bevel-in)",
        height,
        overflow: "auto",
        padding: 2,
        ...style,
      }}
    >
      <table style={{ width: "100%", borderCollapse: "collapse", font: mono ? "var(--weight-normal) var(--text-lg)/1.1 var(--font-mono)" : "var(--type-label)" }}>
        <thead>
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                style={{
                  position: "sticky",
                  top: 0,
                  background: "var(--surface-window)",
                  boxShadow: "var(--bevel-out-thin)",
                  font: "var(--type-label)",
                  textAlign: c.align || "left",
                  padding: "var(--space-2) var(--space-4)",
                  width: c.width,
                  whiteSpace: "nowrap",
                }}
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => {
            const sel = i === selectedIndex;
            return (
              <tr
                key={i}
                onClick={() => onSelect && onSelect(i)}
                style={{ background: sel ? "var(--surface-selected)" : "transparent", color: sel ? "var(--text-on-selected)" : "var(--text-body)", cursor: "default" }}
              >
                {columns.map((c) => (
                  <td key={c.key} style={{ padding: "1px var(--space-4)", textAlign: c.align || "left", whiteSpace: "nowrap" }}>
                    {r[c.key]}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
