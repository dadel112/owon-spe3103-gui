Report-view list: sunken white well, raised sticky headers, full-row navy selection.

```jsx
<ListView mono height={160} columns={[{key:"t",label:"Time",width:70},{key:"v",label:"V",align:"right"}]} rows={rows} selectedIndex={i} onSelect={setI} />
```

`mono` for anything numeric so columns align. Rows are 1px-padded — dense is correct here.
