The 19px menu bar with drop menus: navy hover, etched separators, first letter underlined as the mnemonic.

```jsx
<MenuBar menus={[{label:"File",items:[{label:"Open Profile…",shortcut:"Ctrl+O"},"-",{label:"Exit"}]}]} onSelect={run} />
```

Every window with more than one action gets a menu bar — File, Device, View, Help is the product's standard set. Items that open a dialog end in an ellipsis.
