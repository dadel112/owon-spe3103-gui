import React from "react";

/* A sunken plot well: grid drawn with gradients, series drawn as an inline
   polyline. Pass points as [{x,y}] in 0..1 space. */
export function PlotWell({ series = [], height = 140, grid = 10, color = "var(--led-green)", style, children }) {
  const path = (pts) => pts.map((p, i) => `${i ? "L" : "M"}${(p.x * 100).toFixed(2)},${(100 - p.y * 100).toFixed(2)}`).join(" ");
  return (
    <div
      style={{
        position: "relative",
        height,
        background: "var(--surface-readout)",
        boxShadow: "var(--bevel-in)",
        backgroundImage: `repeating-linear-gradient(to right,rgba(34,255,102,.16) 0 1px,transparent 1px ${100 / grid}%),repeating-linear-gradient(to bottom,rgba(34,255,102,.16) 0 1px,transparent 1px ${100 / grid}%)`,
        ...style,
      }}
    >
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: "absolute", inset: 2, width: "calc(100% - 4px)", height: "calc(100% - 4px)", imageRendering: "auto" }}>
        {series.map((s, i) => (
          <path key={i} d={path(s.points || [])} fill="none" stroke={s.color || color} strokeWidth={s.width || 1} vectorEffect="non-scaling-stroke" shapeRendering="crispEdges" />
        ))}
      </svg>
      <span style={{ position: "absolute", inset: 2, pointerEvents: "none", background: "var(--pattern-scanlines)" }} />
      {children}
    </div>
  );
}
