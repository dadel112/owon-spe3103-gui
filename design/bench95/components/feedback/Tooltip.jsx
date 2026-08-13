import React from "react";

/* The pale-yellow balloon. Appears instantly, never animates. */
export function Tooltip({ text, children, side = "bottom" }) {
  const [show, setShow] = React.useState(false);
  const pos =
    side === "top"
      ? { bottom: "100%", left: 0, marginBottom: 3 }
      : side === "right"
      ? { left: "100%", top: 0, marginLeft: 3 }
      : { top: "100%", left: 0, marginTop: 3 };
  return (
    <span style={{ position: "relative", display: "inline-flex" }} onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show ? (
        <span
          role="tooltip"
          style={{
            position: "absolute",
            ...pos,
            zIndex: 60,
            whiteSpace: "nowrap",
            background: "#ffffe1",
            color: "var(--text-body)",
            font: "var(--type-label)",
            padding: "1px var(--space-4) 2px",
            boxShadow: "var(--bevel-outline)",
          }}
        >
          {text}
        </span>
      ) : null}
    </span>
  );
}
