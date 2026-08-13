/* Dev-only fallback: if the compiled _ds_bundle.js is not present (fresh
   checkout, offline, or before the first compile), transpile the component
   sources in the browser and publish the same window namespace. Cards and UI
   kits poll for window[NS], so either path works. */
(function () {
  var NS = "Bench95DesignSystem_3e1c29";
  var script = document.currentScript;
  var root = (script && script.dataset.root) || ".";
  var FILES = [
    "components/core/Icon.jsx",
    "components/core/TitleBar.jsx",
    "components/core/Window.jsx",
    "components/core/Button.jsx",
    "components/core/IconButton.jsx",
    "components/core/Panel.jsx",
    "components/core/Toolbar.jsx",
    "components/forms/TextField.jsx",
    "components/forms/NumberSpinner.jsx",
    "components/forms/Select.jsx",
    "components/forms/Checkbox.jsx",
    "components/forms/Radio.jsx",
    "components/forms/Slider.jsx",
    "components/display/LedReadout.jsx",
    "components/display/Led.jsx",
    "components/display/ProgressBar.jsx",
    "components/display/StatusBar.jsx",
    "components/display/ListView.jsx",
    "components/display/PlotWell.jsx",
    "components/feedback/Dialog.jsx",
    "components/feedback/Tooltip.jsx",
    "components/navigation/Tabs.jsx",
    "components/navigation/MenuBar.jsx",
    "components/navigation/TaskBar.jsx",
  ];
  var NAMES = [
    "Icon","TitleBar","Window","Button","IconButton","Panel","Toolbar","ToolbarSeparator","ToolbarGrip",
    "TextField","NumberSpinner","Select","Checkbox","Radio","Slider",
    "LedReadout","Led","ProgressBar","StatusBar","ListView","PlotWell",
    "Dialog","Tooltip","Tabs","MenuBar","TaskBar",
  ];
  function boot() {
    if (window[NS]) return;
    if (!window.Babel || !window.React) return setTimeout(boot, 30);
    Promise.all(FILES.map(function (f) { return fetch(root + "/" + f).then(function (r) { return r.text(); }); }))
      .then(function (sources) {
        var src = sources
          .map(function (s) { return s.replace(/^\s*import[^;]+;\s*$/gm, "").replace(/export\s+function/g, "function"); })
          .join("\n");
        var out = window.Babel.transform(src, { presets: ["react"] }).code;
        window[NS] = new Function("React", out + "\nreturn {" + NAMES.join(",") + "};")(window.React);
      })
      .catch(function (e) { console.error("dev fallback failed", e); });
  }
  boot();
})();
