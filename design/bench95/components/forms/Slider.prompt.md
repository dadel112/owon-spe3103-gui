The trackbar: 4px etched groove, 11×20 bevelled thumb, hairline ticks below.

```jsx
<Slider value={volts} min={0} max={30} step={0.1} ticks={7} onChange={setVolts} />
```

Pair it with a NumberSpinner showing the exact value — the slider is for coarse motion, never the only readout.
