import React from "react";
import { Icon } from "../core/Icon.jsx";

export function TaskBar({ startLabel = "Start", tasks = [], activeTask, onTask, onStart, tray = [], clock = "14:32", style }) {
  return (
    <div
      style={{
        height: "var(--taskbar-h)",
        display: "flex",
        alignItems: "center",
        gap: "var(--space-4)",
        padding: "var(--space-2)",
        background: "var(--surface-window)",
        boxShadow: "var(--bevel-out-thin)",
        ...style,
      }}
    >
      <button
        type="button"
        onClick={onStart}
        style={{
          height: 22,
          border: 0,
          padding: "0 var(--space-6)",
          display: "flex",
          alignItems: "center",
          gap: "var(--space-4)",
          background: "var(--surface-window)",
          boxShadow: "var(--bevel-out)",
          font: "var(--weight-bold) var(--text-sm)/1 var(--font-ui)",
          cursor: "default",
        }}
      >
        <Icon name="dashboard" size={16} />
        {startLabel}
      </button>
      <span style={{ width: 3, alignSelf: "stretch", boxShadow: "var(--bevel-in-thin)", margin: "0 var(--space-2)" }} />
      <div style={{ flex: 1, display: "flex", gap: "var(--space-3)", minWidth: 0 }}>
        {tasks.map((t) => {
          const name = typeof t === "string" ? t : t.label;
          const on = name === activeTask;
          return (
            <button
              key={name}
              type="button"
              onClick={() => onTask && onTask(name)}
              style={{
                height: 22,
                maxWidth: 160,
                flex: "0 1 160px",
                border: 0,
                display: "flex",
                alignItems: "center",
                gap: "var(--space-4)",
                padding: "0 var(--space-6)",
                background: on ? "var(--pattern-checker)" : "var(--surface-window)",
                boxShadow: on ? "var(--bevel-out-pressed)" : "var(--bevel-out)",
                font: on ? "var(--weight-bold) var(--text-sm)/1 var(--font-ui)" : "var(--type-menu)",
                cursor: "default",
                overflow: "hidden",
                whiteSpace: "nowrap",
              }}
            >
              {typeof t === "object" && t.icon ? <Icon name={t.icon} size={16} /> : null}
              <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>{name}</span>
            </button>
          );
        })}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "var(--space-6)", padding: "0 var(--space-6)", height: 20, boxShadow: "var(--bevel-in-thin)" }}>
        {tray.map((t) => (
          <Icon key={t} name={t} size={16} />
        ))}
        <span style={{ font: "var(--type-statusbar)" }}>{clock}</span>
      </div>
    </div>
  );
}
