The instrument readout: sunken near-black well, glowing VT323 digits, scanline overlay.

```jsx
<LedReadout label="VOLTS" value={12.004} digits={3} unit="V" size="lg" />
<LedReadout label="AMPS" value={0} digits={3} unit="A" color="amber" off />
```

Green = measured and live, amber = limit/secondary, red = fault or tripped. `off` when output is disabled — never blank the well.
