Sunken 21px text field, white well, 2px text inset.

```jsx
<TextField value={cmd} onChange={setCmd} mono width={220} />
```

Use `mono` for anything machine-facing (SCPI strings, ports, IDs). Labels sit to the left, 6px away, never floating inside.
