import React from "react";

export function Slider({ value = 0, min = 0, max = 100, step = 1, onChange, ticks = 5, disabled = false, width = 180, style }) {
  const pct = ((value - min) / (max - min)) * 100;
  const ref = React.useRef(null);
  const set = (clientX) => {
    const r = ref.current.getBoundingClientRect();
    const raw = min + ((clientX - r.left) / r.width) * (max - min);
    const snapped = Math.round(raw / step) * step;
    onChange && onChange(Math.min(max, Math.max(min, Number(snapped.toFixed(4)))));
  };
  return (
    <span style={{ display: "inline-block", width, userSelect: "none", ...style }}>
      <span
        ref={ref}
        onMouseDown={(e) => {
          if (disabled) return;
          set(e.clientX);
          const move = (ev) => set(ev.clientX);
          const up = () => {
            window.removeEventListener("mousemove", move);
            window.removeEventListener("mouseup", up);
          };
          window.addEventListener("mousemove", move);
          window.addEventListener("mouseup", up);
        }}
        style={{ display: "block", position: "relative", height: 20, cursor: "default" }}
      >
        <span style={{ position: "absolute", left: 0, right: 0, top: 8, height: 4, boxShadow: "var(--bevel-in-thin)", background: "var(--surface-trough)" }} />
        <span
          style={{
            position: "absolute",
            left: `calc(${pct}% - 5px)`,
            top: 0,
            width: 11,
            height: 20,
            background: "var(--surface-window)",
            boxShadow: "var(--bevel-out)",
            opacity: disabled ? 0.6 : 1,
          }}
        />
      </span>
      {ticks ? (
        <span style={{ display: "flex", justifyContent: "space-between", height: 4, marginTop: 1 }}>
          {Array.from({ length: ticks }).map((_, i) => (
            <span key={i} style={{ width: 1, height: 4, background: "var(--grey-700)" }} />
          ))}
        </span>
      ) : null}
    </span>
  );
}
