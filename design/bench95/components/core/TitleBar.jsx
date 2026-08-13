import React from "react";
import { Icon } from "./Icon.jsx";

const btn = {
  width: "var(--titlebar-btn)",
  height: "var(--titlebar-btn)",
  padding: 0,
  border: 0,
  background: "var(--surface-window)",
  boxShadow: "var(--bevel-out)",
  display: "grid",
  placeItems: "center",
  cursor: "default",
  transition: "var(--transition-none)",
};

function Glyph({ kind }) {
  const bar = { background: "var(--black)", position: "absolute" };
  if (kind === "minimize") return <span style={{ ...bar, width: 6, height: 2, bottom: 2 }} />;
  if (kind === "maximize")
    return <span style={{ position: "absolute", width: 8, height: 7, borderLeft: "1px solid var(--black)", borderRight: "1px solid var(--black)", borderBottom: "1px solid var(--black)", borderTop: "2px solid var(--black)" }} />;
  return <Icon name="close" size={8} />;
}

export function TitleBar({
  title,
  icon,
  active = true,
  variant = "classic",
  buttons = ["minimize", "maximize", "close"],
  onButton,
  children,
}) {
  const bg =
    !active
      ? "var(--gradient-titlebar-inactive)"
      : variant === "xp"
      ? "var(--gradient-titlebar-xp)"
      : "var(--gradient-titlebar)";
  return (
    <div
      style={{
        height: variant === "xp" ? 22 : "var(--titlebar-h)",
        flex: "0 0 auto",
        background: bg,
        display: "flex",
        alignItems: "center",
        gap: "var(--space-3)",
        padding: "0 var(--space-2) 0 var(--space-2)",
        margin: "var(--space-2)",
        marginBottom: 0,
        userSelect: "none",
      }}
    >
      {icon ? <Icon name={icon} size={12} color="#ffffff" /> : null}
      <span
        style={{
          font: "var(--type-titlebar)",
          color: active ? "var(--text-on-titlebar)" : "var(--grey-100)",
          textShadow: variant === "xp" ? "1px 1px 0 rgba(0,0,0,.5)" : "none",
          flex: "1 1 auto",
          overflow: "hidden",
          whiteSpace: "nowrap",
          textOverflow: "ellipsis",
        }}
      >
        {title}
      </span>
      {children}
      <span style={{ display: "flex", gap: 2 }}>
        {buttons.map((b) => (
          <button
            key={b}
            type="button"
            aria-label={b}
            onClick={() => onButton && onButton(b)}
            style={{ ...btn, position: "relative", marginLeft: b === "close" ? 2 : 0 }}
          >
            <Glyph kind={b} />
          </button>
        ))}
      </span>
    </div>
  );
}
