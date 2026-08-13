import React from "react";

export function StatusBar({ panes = [], style }) {
  return (
    <div
      style={{
        display: "flex",
        gap: "var(--space-2)",
        height: "var(--statusbar-h)",
        flex: "0 0 auto",
        alignItems: "stretch",
        marginTop: "var(--space-2)",
        ...style,
      }}
    >
      {panes.map((p, i) => {
        const pane = typeof p === "string" ? { text: p } : p;
        return (
          <div
            key={i}
            style={{
              flex: pane.grow ?? (i === 0 ? "1 1 auto" : "0 0 auto"),
              minWidth: pane.width || 0,
              width: pane.width,
              boxShadow: "var(--bevel-in-thin)",
              font: "var(--type-statusbar)",
              display: "flex",
              alignItems: "center",
              gap: "var(--space-4)",
              padding: "0 var(--space-4)",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              color: pane.tone === "danger" ? "var(--status-danger)" : "var(--text-body)",
            }}
          >
            {pane.icon}
            {pane.text}
          </div>
        );
      })}
    </div>
  );
}
