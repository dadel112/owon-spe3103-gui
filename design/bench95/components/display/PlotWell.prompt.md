Sunken oscilloscope-style well: dark ground, green grid, crisp non-scaling traces, scanlines.

```jsx
<PlotWell height={150} series={[{ points: volts }, { points: amps, color: "var(--led-amber)" }]} />
```

Normalise data to 0..1 before passing. Axis labels go outside the well in 11px UI type.
