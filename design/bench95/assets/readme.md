# Assets

**There is no logo file, and none was invented.** No brand mark was supplied with the brief, so wherever a mark would go the product name is set in type — Silkscreen, letter-spaced, black on grey chrome or white on navy. See `guidelines/wordmark.card.html`.

**No image assets are shipped.** The reference material supplied with the brief is third-party product screenshots (Windows 95/XP interfaces and their icon art), which cannot be extracted or redistributed, so nothing was copied out of them. Backdrops that look like wallpaper — the teal field and the sky/grass gradient — are CSS gradients (`--desktop-teal`, `--gradient-hill`), not files.

**Icons are loaded from CDN**, not stored here: pixelarticons 1.8.1 (MIT), `https://cdn.jsdelivr.net/npm/pixelarticons@1.8.1/svg/<name>.svg`, wrapped by `components/core/Icon.jsx`. Tinted variants route through `https://api.iconify.design/pixelarticons/<name>.svg?color=…`. To vendor them, npm-install `pixelarticons`, copy `svg/` into this folder, and point `BASE` in `Icon.jsx` at the local path.

**Fonts** — `fonts/MS_Sans_Serif.ttf` is self-hosted and wired into `tokens/fonts.css`, leading `--font-ui`. Silkscreen, VT323 and Pixelify Sans load from Google Fonts.

If you have real assets — a program icon, an instrument photo, your own wordmark — drop them here and tell the agent; the readme's Iconography and Brand sections should be updated to match.
