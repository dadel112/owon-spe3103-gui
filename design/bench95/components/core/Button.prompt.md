The push button: 23px tall, 75px minimum width, bevel flips on press with a 1px label nudge.

```jsx
<Button isDefault onClick={apply}>OK</Button>
<Button icon="power" onClick={toggle}>Output ON</Button>
<Button disabled>Apply</Button>
```

Labels are sentence case, no ellipsis unless the action opens a dialog ("Save As…"). Disabled labels get the grey + white-emboss treatment automatically.
