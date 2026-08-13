import React from "react";

export function Led({ on = false, color = "green", label, blink = false, size = 10, style }) {
  const lit = color === "amber" ? "var(--led-amber)" : color === "red" ? "var(--led-red)" : "var(--led-green)";
  const dim = color === "amber" ? "var(--led-amber-dim)" : color === "red" ? "var(--led-red-dim)" : "var(--led-green-dim)";
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "var(--space-6)", font: "var(--type-label)", ...style }}>
      <span
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          flex: "0 0 auto",
          background: on ? lit : dim,
          boxShadow: on ? `0 0 5px ${lit}, inset 1px 1px 0 rgba(255,255,255,.55)` : "inset 1px 1px 0 rgba(0,0,0,.5)",
          outline: "1px solid var(--grey-500)",
          animation: on && blink ? `bench-led-blink var(--dur-blink) var(--ease-step) infinite` : "none",
        }}
      />
      {label}
      <style>{"@keyframes bench-led-blink{50%{opacity:.15}}"}</style>
    </span>
  );
}
