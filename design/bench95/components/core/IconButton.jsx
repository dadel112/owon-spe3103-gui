import React from "react";
import { Icon } from "./Icon.jsx";

export function IconButton({ icon, label, size = 24, active = false, disabled = false, onClick, style, ...rest }) {
  const [down, setDown] = React.useState(false);
  const isDown = down || active;
  return (
    <button
      type="button"
      title={label}
      aria-label={label}
      disabled={disabled}
      onClick={onClick}
      onMouseDown={() => !disabled && setDown(true)}
      onMouseUp={() => setDown(false)}
      onMouseLeave={() => setDown(false)}
      style={{
        width: size,
        height: size,
        padding: 0,
        border: 0,
        display: "grid",
        placeItems: "center",
        background: active ? "var(--pattern-checker)" : "var(--surface-window)",
        boxShadow: isDown && !disabled ? "var(--bevel-out-pressed)" : "var(--bevel-out)",
        cursor: "default",
        transition: "var(--transition-none)",
        ...style,
      }}
      {...rest}
    >
      <Icon name={icon} size={16} style={{ opacity: disabled ? 0.35 : 1, transform: isDown ? "translate(1px,1px)" : "none" }} />
    </button>
  );
}
