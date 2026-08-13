import React from "react";
import { Icon } from "./Icon.jsx";

export function Button({
  children,
  icon,
  onClick,
  disabled = false,
  isDefault = false,
  pressed = false,
  size = "md",
  block = false,
  type = "button",
  style,
  ...rest
}) {
  const [down, setDown] = React.useState(false);
  const isDown = down || pressed;
  const h = size === "sm" ? "var(--control-h-sm)" : size === "lg" ? "var(--control-h-lg)" : "var(--control-h-btn)";
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      onMouseDown={() => !disabled && setDown(true)}
      onMouseUp={() => setDown(false)}
      onMouseLeave={() => setDown(false)}
      style={{
        minWidth: size === "sm" ? 0 : "var(--btn-min-w)",
        width: block ? "100%" : undefined,
        height: h,
        padding: `0 ${size === "sm" ? "var(--space-4)" : "var(--space-8)"}`,
        border: 0,
        background: "var(--surface-window)",
        color: disabled ? "var(--text-disabled)" : "var(--text-body)",
        textShadow: disabled ? "1px 1px 0 var(--text-disabled-emboss)" : "none",
        font: "var(--type-button)",
        boxShadow: isDown && !disabled ? "var(--bevel-out-pressed)" : "var(--bevel-out)",
        outline: isDefault && !isDown ? "1px solid var(--black)" : "none",
        outlineOffset: 0,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "var(--space-4)",
        cursor: "default",
        transition: "var(--transition-none)",
        paddingTop: isDown && !disabled ? 2 : 0,
        paddingLeft: isDown && !disabled ? "calc(var(--space-8) + 1px)" : undefined,
        ...style,
      }}
      {...rest}
    >
      {icon ? <Icon name={icon} size={16} style={{ opacity: disabled ? 0.4 : 1 }} /> : null}
      {children}
    </button>
  );
}
