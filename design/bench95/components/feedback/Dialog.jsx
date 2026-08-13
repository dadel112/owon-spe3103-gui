import React from "react";
import { Button } from "../core/Button.jsx";
import { TitleBar } from "../core/TitleBar.jsx";
import { Icon } from "../core/Icon.jsx";

const GLYPH = { info: "info-box", warning: "alert", error: "close-box", question: "help" };

export function Dialog({
  title = "Message",
  kind = "info",
  message,
  detail,
  buttons = ["OK"],
  defaultButton = "OK",
  onButton,
  width = 340,
  children,
  style,
}) {
  const glyph = kind === "warning" ? "alert" : kind === "error" ? "close" : kind === "question" ? "device-tablet" : "info-box";
  const tint = kind === "warning" ? "var(--status-warn)" : kind === "error" ? "var(--status-danger)" : "var(--status-info)";
  return (
    <div
      role="dialog"
      style={{
        width,
        background: "var(--surface-dialog)",
        boxShadow: "var(--bevel-out), var(--shadow-hard)",
        display: "flex",
        flexDirection: "column",
        ...style,
      }}
    >
      <TitleBar title={title} active buttons={["close"]} onButton={() => onButton && onButton("close")} />
      <div style={{ padding: "var(--space-16) var(--space-11) var(--space-11)", display: "flex", gap: "var(--space-16)" }}>
        <span style={{ width: 32, height: 32, flex: "0 0 auto", display: "grid", placeItems: "center", background: tint, boxShadow: "var(--bevel-out-thin)" }}>
          <Icon name={glyph} size={24} color="#ffffff" />
        </span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ font: "var(--type-body)" }}>{message}</div>
          {detail ? <div style={{ font: "var(--type-body)", color: "var(--grey-700)", marginTop: "var(--space-6)" }}>{detail}</div> : null}
          {children}
        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "center", gap: "var(--space-8)", padding: "0 var(--space-11) var(--space-16)" }}>
        {buttons.map((b) => (
          <Button key={b} isDefault={b === defaultButton} onClick={() => onButton && onButton(b)}>
            {b}
          </Button>
        ))}
      </div>
    </div>
  );
}
