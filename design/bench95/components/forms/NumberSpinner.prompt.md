The up/down edit box for setpoints: right-aligned mono value, unit suffix, stacked arrow buttons.

```jsx
<NumberSpinner value={volts} onChange={setVolts} step={0.1} max={30} decimals={3} unit="V" />
```

Always show the instrument's real resolution (3 decimals for a 30V/5A bench supply). This is the primary input in the product — prefer it over a plain TextField for any number.
