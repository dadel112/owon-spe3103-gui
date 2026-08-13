import React from "react";

export function Toolbar({ children, style }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "var(--space-2)",
        padding: "var(--space-2)",
        background: "var(--surface-window)",
        boxShadow: "var(--bevel-out-thin)",
        flex: "0 0 auto",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export function ToolbarSeparator() {
  return <span style={{ width: 2, alignSelf: "stretch", margin: "0 var(--space-3)", boxShadow: "var(--bevel-in-thin)" }} />;
}

export function ToolbarGrip() {
  return <span style={{ width: 3, alignSelf: "stretch", margin: "0 var(--space-3) 0 0", boxShadow: "var(--bevel-out-thin)" }} />;
}
