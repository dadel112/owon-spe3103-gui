import React from "react";
import { TitleBar } from "./TitleBar.jsx";

export function Window({
  title,
  icon,
  active = true,
  variant = "classic",
  buttons,
  onButton,
  width,
  height,
  padded = false,
  style,
  children,
}) {
  return (
    <div
      style={{
        width,
        height,
        background: "var(--surface-window)",
        boxShadow: "var(--bevel-out)",
        display: "flex",
        flexDirection: "column",
        font: "var(--type-body)",
        color: "var(--text-body)",
        ...style,
      }}
    >
      {title !== undefined && (
        <TitleBar title={title} icon={icon} active={active} variant={variant} buttons={buttons} onButton={onButton} />
      )}
      <div
        style={{
          flex: "1 1 auto",
          minHeight: 0,
          display: "flex",
          flexDirection: "column",
          padding: padded ? "var(--space-8)" : 0,
          margin: "var(--space-2)",
          marginTop: title !== undefined ? "var(--space-2)" : "var(--space-2)",
        }}
      >
        {children}
      </div>
    </div>
  );
}
