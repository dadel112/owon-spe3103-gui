import React from "react";

const BASE = "https://cdn.jsdelivr.net/npm/pixelarticons@1.8.1/svg/";
const TINTED = "https://api.iconify.design/pixelarticons/";

export function Icon({ name, size = 16, color, title, style, ...rest }) {
  const src = color
    ? `${TINTED}${name}.svg?color=${encodeURIComponent(color)}`
    : `${BASE}${name}.svg`;
  return (
    <img
      src={src}
      alt={title || ""}
      title={title}
      width={size}
      height={size}
      draggable={false}
      style={{ display: "block", width: size, height: size, imageRendering: "pixelated", flex: "0 0 auto", ...style }}
      {...rest}
    />
  );
}
