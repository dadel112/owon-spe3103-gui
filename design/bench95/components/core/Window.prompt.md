The application frame: raised 2px bevel, caption bar, 2px inner gutter. Every screen starts here.

```jsx
<Window title="Bench95 Supply" icon="zap" width={640} padded>
  <MenuBar menus={menus} />
  <Panel label="Output">…</Panel>
  <StatusBar panes={["Ready", { text: "COM3", width: 70 }]} />
</Window>
```

Children lay out in a column. `padded` for dialogs and property sheets; leave it off when the window contains a menu bar or a full-bleed list.
