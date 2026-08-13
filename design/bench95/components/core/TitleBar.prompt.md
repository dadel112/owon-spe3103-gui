The window caption bar: gradient fill, bold 11px white label, bevelled 14px control buttons.

```jsx
<TitleBar title="Supply — COM3" icon="zap" onButton={(b) => b === "close" && close()} />
```

Used inside `Window`; only mount it directly for custom shells (palettes, floating toolbars). `active={false}` for background windows.
