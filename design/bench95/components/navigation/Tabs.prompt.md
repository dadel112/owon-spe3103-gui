Property-sheet tabs: the active tab is 2px taller and merges into the page below it.

```jsx
<Tabs tabs={["Output","Protection","Logging"]} value={tab} onChange={setTab}>{body}</Tabs>
```

Tab labels are one word where possible. Four tabs is a comfortable maximum at 640px.
