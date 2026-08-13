The modal message box: warm grey face, 32px tinted glyph, centred button row, hard offset shadow.

```jsx
<Dialog kind="warning" title="Bench95" message="Output is still enabled." detail="Disable the output before disconnecting." buttons={["OK","Cancel"]} onButton={handle} />
```

One sentence of `message`, one of `detail`. Buttons are OK / Cancel / Retry / Ignore — verbs only when the action is destructive ("Discard").
