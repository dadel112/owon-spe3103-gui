The bottom bar of etched panes: first pane grows, the rest are fixed width.

```jsx
<StatusBar panes={["Ready", { text: "CV", width: 44 }, { text: "COM3 · 9600", width: 110 }]} />
```

Copy is terse and factual: "Ready", "Connected", "Output disabled". Put connection state and mode here, not in a toast.
