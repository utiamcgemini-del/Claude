# UTI AMC Password Policy — Wallpaper & Screensaver

Assets communicating the updated password policy (stricter complexity rules,
same 90-day reset cycle), styled in UTI Mutual Fund's brand colors
(`#044EA3` blue / `#F68122` orange).

## Files

- **`uti-amc-password-policy-wallpaper.png`** — 1920×1080 desktop wallpaper.
  Ready to set directly as a desktop background. Content is anchored to the
  right third of the frame, leaving the left/lower-left clear for desktop
  icons.
- **`wallpaper.html`** — source for the wallpaper. Open in a browser and
  screenshot, or re-render at a different resolution (see below).
- **`screensaver.html`** — fullscreen animated screensaver (ambient drifting
  network backdrop, staged text reveal). Any key press or click exits, matching
  standard screensaver behavior. Respects `prefers-reduced-motion`.
- **`screensaver-preview.png`** — static preview frame of the screensaver.

## Re-rendering the wallpaper PNG at a different resolution

```bash
node render.js wallpaper.html output.png
```

using a small Playwright script that opens the HTML at the target viewport
size and takes a screenshot (see the render commands used to generate the
1920×1080 PNG in this change's commit history).

## Using the screensaver

`screensaver.html` is a static page — open it fullscreen in any browser
(F11 / kiosk mode) to run it as a screensaver, or wrap it with a tool like
Lively Wallpaper / Screensaver Factory / plasma's HTML screensaver support if
your OS needs it packaged into a native `.scr`/`.desktop` format.
