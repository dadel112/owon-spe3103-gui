# Bench95 Design System

A desktop-software design system in the idiom of mid-90s / early-2000s Windows GUIs, built for **Bench95 Supply** — a small Python program that drives a programmable bench power supply over a serial link (SCPI / Modbus). Grey chrome, 1px bevels, 11px UI type, LED readouts, no radii, no soft shadows.

`Bench95` is a working name chosen for this system, not a brand supplied by the user. No logo or brand mark was provided, so the wordmark is **set in type** (Silkscreen) wherever a mark would go — nothing has been drawn or reconstructed. Rename freely.

## Sources given

- `uploads/1a0bcf007418782beb41ab3d025b625e.jpg` — a paint program in a classic window (title bar, menu bar, tool palette, palette strip, status bar).
- `uploads/557e670b362698d4e9688ac4e135b454.jpg` — a full desktop: 32px labelled icons on a sky/grass wallpaper, task bar with launch button and tray.
- `uploads/Herunterladen.png` — a collage of era UI ephemera: stacked "Error / Fail / OK" message boxes, start menu, tool palette, glossy avatars, pixel cursors.
- `uploads/Herunterladen (1).png` — a second collage: property sheets with tabs, list boxes with scroll arrows, an inbox tree view, a minesweeper grid, a CD-player transport with an LED time display.
- Written brief: "Simple program written in python to control programmable psu"; "win xp style, old school, pixelated".

No codebase, Figma file, or deck was attached. **The reference images are third-party product screenshots**, so nothing was traced or extracted from them: they were read for *conventions* (bevel construction, control metrics, gradient title bars, teal desktop, LED transport displays), and every pixel in this system is authored here. Icons come from the MIT-licensed **pixelarticons** set over CDN — flagged as a substitution below.

If you have the actual Python program (Tk / Qt / PySimpleGUI source, screenshots of your own build, or a device manual), attach it: the UI kit is currently a plausible reconstruction of such a program, not a recreation of yours.

## Product context

One product, one surface: a single-user desktop utility, run locally, talking to one instrument.

- **Bench95 Supply** — the control program. A main window (measured values + setpoints + protection), a connect dialog, a sequence editor, a data log, and a SCPI console. Modelled as a 30 V / 5 A single-channel supply ("PSU-3005") at 3-decimal resolution.

The audience is one engineer at a bench who wants the numbers large, the state unambiguous, and no chrome between them and the instrument.

---

## Content fundamentals

**Voice.** Instrument-panel plain. The program states facts and consequences; it never sells, apologises, or jokes. Nouns over gerunds for labels ("Voltage", not "Setting voltage"). No exclamation marks, no emoji anywhere, ever.

**Casing.** Sentence case in every sentence-like place — buttons, checkboxes, labels, menu items, status text ("Output enabled", "Open Profile…", "Enable OVP"). Title Case only for window titles and menu titles ("Data log", "Connect to device", "File / Device / View / Help"). ALL CAPS is reserved for two things: pixel captions inside LED readouts (`VOLTS`, `AMPS`, `WATTS`) and indicator lamp labels (`LINK`, `CC`, `TRIP`).

**Person.** Second person only when instructing, and rarely: "Disable the output before disconnecting the load." The program never says "I". It does not narrate its own actions in first person plural ("We couldn't connect") — it reports state: "No response from COM3."

**Length.** One line per label. Dialogs get one sentence of message plus at most one sentence of detail:

> **Output is still enabled.**
> Disable the output before disconnecting the load.

**Units and numbers.** Always show the instrument's real resolution — `12.004 V`, `1.250 A`, `15.01 W`. Space between number and unit in prose, no space inside a readout's own unit slot. Time is 24-hour, `14:31:02`. Ports and commands are shown verbatim in mono: `COM3 · 9600 8N1`, `MEAS:VOLT?`.

**Menus and shortcuts.** First letter underlined as the mnemonic. Items that open a dialog end in an ellipsis ("Connect…", "Export Log…"). Shortcuts right-aligned in the drop menu (`Ctrl+S`).

**Errors.** Name the thing that failed, then the next action. "No response from COM3." / "Check the cable and the baud rate, then retry." Never "Oops", never "Something went wrong".

**Status bar copy.** Two words maximum per pane: `Ready`, `Logging`, `Output enabled`, `Not connected`, `CV`, `62%`.

**Tooltips.** Noun phrase plus optional shortcut, no full stop: "Save profile (Ctrl+S)".

---

## Visual foundations

**Depth is the whole system.** Every surface is either raised or sunken, drawn with hard 1px and 2px edges — outer highlight `#ffffff`, inner highlight `#dfdfdf`, inner shadow `#808080`, outer shadow `#000000`. Implemented as inset `box-shadow` tokens (`--bevel-out`, `--bevel-in`, and their 1px `-thin` variants) so any element can take the treatment. **No blur, no alpha, no radius.** Raised = interactive (button, toolbar, task bar, window frame). Sunken = content you read or type into (field, list, readout, plot).

**Colour.** One neutral chrome (`#c0c0c0`, warmer `#d4d0c8` in dialogs) carries 95% of the pixels. Colour appears in exactly four places: the title bar gradient (navy → blue, or the XP-leaning vertical blue), the navy selection fill, the LED readouts (green measured / amber limit / red fault), and status text when something is wrong (`--status-danger`). No tints, no brand accent, no gradients on buttons. Never a bluish-purple gradient.

**Backgrounds.** Windows are flat `#c0c0c0`. The desktop behind them is either flat teal `#008080` or the sky-to-grass gradient (`--gradient-hill`) — a nod to the reference wallpaper, built from a CSS gradient, not an image. No photography, no illustration, no texture on interface surfaces. The only patterns are functional: a 2px checkerboard for a latched button face (`--pattern-checker`) and 1-in-3 scanlines over LED wells (`--pattern-scanlines`).

**Type.** MS Sans Serif (self-hosted) at 11px for the entire interface, 1.2 line-height in controls and 1.45 in prose. Bold only in title bars and the active task-bar button. Silkscreen (pixel) for readout captions and the wordmark; VT323 (mono) for readouts, tables, SCPI traffic and any editable number. Antialiasing is switched off (`-webkit-font-smoothing:none`) so type stays crunchy. Minimum size in the UI is 9px, used only for pixel captions.

**Corner radii.** `0` everywhere. The one permitted exception is a 3px top-corner on an XP-leaning window (`--radius-titlebar`), off by default. Round shapes exist only where the hardware does: indicator lamps and radio buttons.

**Shadows.** There is no elevation system. Menus and modals get `--shadow-hard` — a 2px offset, zero-blur, 35% black rectangle — and nothing else does. LED digits get a 6px coloured glow, the only soft effect in the system, because a lit segment bleeds.

**Cards.** There are none. Grouping is the etched group box (`Panel`): a 1px sunken/raised hairline frame with an optional caption interrupting the top edge. No shadowed card, no rounded container, and never a rounded container with a coloured left border.

**Borders and separators.** 2px etched rules (`--bevel-in-thin`) for separators, group frames and status panes; a hard black 1px outline (`--bevel-outline`) for popovers and tooltips; a 1px black ring for the default button.

**Spacing.** A 1px grid, not a 4px one — copy the era's real metrics rather than snapping. Bevels 1–2px, control gaps 4–6px, group padding 8px, dialog inset 11px, button gutter 8px. Control heights are fixed: 18 / 21 / 23 / 26px; buttons are minimum 75px wide; title bar 18px; menu bar 19px; status bar 20px; task bar 28px; scrollbars 16px.

**Layout rules.** Windows are fixed-width and left-aligned inside; nothing is centred except a dialog's button row and the dialog itself on screen. Menu bar pinned to the top of the window, toolbar directly beneath it with no gap, status bar pinned to the bottom. Content sits in a 2px inner gutter inside the frame. Screens do not reflow responsively — this is a desktop utility at a known size.

**Interaction states.** Hover does *nothing* on buttons (period-correct): only menu items and list rows highlight, and they do it with a navy fill and white text, instantly. Press inverts the bevel and nudges the label 1px right and down. Latched/toggled controls stay inverted with a checkered face. Focus is a 1px dotted black rectangle inset 4px, never a glow. Disabled text is `#808080` with a `1px 1px 0 #ffffff` emboss, and disabled icons drop to 35% opacity.

**Motion.** Effectively none. State changes are instant (`--dur-instant: 0ms`, `--transition-none`). Where something must move it moves in steps: progress fills in 20 discrete chunks, alarm lamps blink at 530ms with `steps(1,end)`. No fades, no easing curves, no bounces, no skeleton shimmer. `prefers-reduced-motion` stops the blink.

**Transparency and blur.** Never. There is no `backdrop-filter`, no translucent panel, no protection gradient over imagery — a caption sits on a solid fill or on nothing.

**Imagery.** The system ships no photography or illustration. If a screenshot or diagram is needed it goes into a sunken well at 1:1 pixel scale, `image-rendering: pixelated`, no rounding and no shadow. Colour vibe when imagery is unavoidable: saturated, dithered, slightly cool — never warm film grain.

---

## Iconography

- **Set:** [pixelarticons](https://github.com/halfmage/pixelarticons) — 24×24 grid, no anti-aliasing, MIT licensed, loaded from `https://cdn.jsdelivr.net/npm/pixelarticons@1.8.1/svg/<name>.svg`. **This is a substitution, flagged:** the reference images are Microsoft's own icon art, which is not reusable, and no icon assets were supplied. pixelarticons matches the grid discipline and pixel weight of the era; swap in your own set by changing `BASE` in `components/core/Icon.jsx`.
- **Wrapper:** `Icon` (an intentional addition — see below). 16px inside chrome (toolbars, title bars, menus, status bar), 24px in dialog glyph plates, 32px for desktop icons. Multiples of 8 only, so pixels stay square.
- **Colour:** black glyphs on grey chrome — the default. White (`color="#ffffff"`) on navy title bars, desktop icons and dialog glyph plates; that path routes through the Iconify tinting CDN because SVG-in-`<img>` cannot inherit `currentColor`.
- **Not used:** emoji (never, in any surface), Unicode dingbats as icons, icon fonts, colour-filled or duotone icons, and hand-drawn SVG. A glyph either exists in the set or the UI uses a word instead. Two ASCII exceptions carried over from the era: `▶` marks the running row in the sequence list, and `»`/`«` prefix SCPI console lines.
- **Vocabulary in use:** `power` (connect), `zap` (output enable / product), `sliders` (sequence), `chart` (log), `code` (console), `save`, `reload` (read from device), `play` / `pause`, `plus` / `minus`, `arrow-up` / `arrow-down`, `trash`, `download` (export), `alert` / `info-box` (dialog glyphs), `clock`, `lock`. Verify a name exists before using it — `terminal`, `settings`, `cog`, `wrench`, `gauge`, `stop` and `printer` are **not** in the free set.
- **Window controls** (minimize / maximize / close) are drawn from CSS boxes at 14px, not icons, because they need to be exactly 6–8px of black on a 14px bevel.
- **No logo.** `assets/` holds no mark. See `assets/readme.md`.

---

## Components

React primitives, one file each, styled entirely with the token custom properties. Grouped by concern under `components/`.

**`components/core/`**
- `Window` — the application frame (bevel, caption bar, 2px inner gutter). *Starting point.*
- `TitleBar` — caption bar with gradient, label and 14px control buttons; `classic` and `xp` variants.
- `Button` — the 23px push button; default ring, pressed bevel, disabled emboss.
- `IconButton` — square bevelled tool button, latches with a checkered face.
- `Panel` — the etched group box with a caption breaking its top rule.
- `Toolbar` (+ `ToolbarSeparator`, `ToolbarGrip`) — the strip under the menu bar.
- `Icon` — pixelarticons wrapper. **Intentional addition:** the reference material has no component library, and a glyph set needs one wrapper so sizes and the tinting path stay consistent.

**`components/forms/`**
- `TextField` — sunken 21px field, optional mono mode.
- `NumberSpinner` — the setpoint control: mono right-aligned value, unit suffix, stacked arrows. The primary input of the product.
- `Select` — combo box with hard-outlined drop list.
- `Checkbox` — 13px sunken box, 2px tick.
- `Radio` — 12px round bevel, 4px dot.
- `Slider` — trackbar with 11×20 thumb and hairline ticks.

**`components/display/`**
- `LedReadout` — sunken LED well: glowing VT323 digits, pixel caption, scanlines, `off` state.
- `Led` — indicator lamp with dim/lit/blink states.
- `ProgressBar` — 20-chunk navy fill in a sunken trough.
- `StatusBar` — etched panes along the window's bottom edge.
- `ListView` — report-view list: sticky raised headers, navy full-row selection, mono rows.
- `PlotWell` — sunken scope well with a green grid and crisp traces.

**`components/feedback/`**
- `Dialog` — modal message box: tinted 32px glyph plate, centred button row, hard shadow. *Starting point.*
- `Tooltip` — pale-yellow balloon with a 1px black outline, instant.

**`components/navigation/`**
- `Tabs` — property-sheet tabs; the active tab grows 2px into the page.
- `MenuBar` — 19px menu bar with mnemonic underlines and drop menus.
- `TaskBar` — desktop task bar: launch button, latched window buttons, etched tray and clock.

Each directory carries a `*.card.html` specimen, and every component has a sibling `.d.ts` (props contract) and `.prompt.md` (what/when + example).

There is deliberately **no** Switch, Avatar, Toast, Accordion, Breadcrumb or Skeleton: the era has no vocabulary for them, and the product has no use for them. A boolean is a `Checkbox`; a transient message is a `Dialog` or a `StatusBar` pane.

---

## Index

| Path | What |
| --- | --- |
| `styles.css` | The only file consumers link. `@import`s everything below. |
| `tokens/fonts.css` | Google Fonts import (Silkscreen, VT323, Pixelify Sans). |
| `tokens/colors.css` | Chrome greys, title blues, desktop backdrops, LED colours, semantic aliases. |
| `tokens/typography.css` | Families, 9–48px sizes, composed `--type-*` roles. |
| `tokens/spacing.css` | 1px spacing scale and the era's fixed control metrics. |
| `tokens/bevels.css` | The bevel/shadow/pattern/gradient system. Radii live here too (all `0`). |
| `tokens/motion.css` | Stepped durations and easings. |
| `tokens/base.css` | Element defaults, link colours, and class versions of the bevels. |
| `components/{core,forms,display,feedback,navigation}/` | 24 primitives + `.d.ts` + `.prompt.md` + one specimen card each. |
| `ui_kits/bench-supply/` | The product recreation: desktop shell, five screens, interactive. See its `README.md`. |
| `guidelines/*.card.html` | 17 foundation specimen cards (Colors, Type, Bevels, Spacing, Motion, Brand). |
| `assets/readme.md` | Asset inventory — and why there is no logo file. |
| `thumbnail.html` | Homepage tile. |
| `SKILL.md` | Agent-skill entry point for using this system elsewhere. |
| `_dev_fallback.js` | Dev convenience: transpiles the component sources in-browser when `_ds_bundle.js` has not been compiled yet. Not part of the public API. |

Generated by the compiler, never edit: `_ds_bundle.js`, `_ds_manifest.json`, `_adherence.oxlintrc.json`.

## Substitutions to confirm

1. **Fonts.** MS Sans Serif is now self-hosted from `fonts/MS_Sans_Serif.ttf` (`@font-face` in `tokens/fonts.css`) and leads `--font-ui`, with Tahoma and Verdana behind it. Silkscreen, VT323 and Pixelify Sans still load from Google Fonts.
2. **Icons.** pixelarticons stands in for an unavailable icon set (see Iconography).
3. **Instrument model.** "PSU-3005", 30 V / 5 A, 3 decimals, SCPI over 9600 8N1 — plausible defaults. Replace with your real device's limits and command set.
