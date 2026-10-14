# Demo recording notes (reproducible, <8 MB)

GitHub READMEs autoplay GIFs and strip raw `<video>` tags. Commit small GIFs; link MP4s.

## Terminal benchmark (vhs — preferred, re-runnable)

`docs/demo.tape` (create if missing):

```tape
Output docs/demo.gif
Set FontSize 14
Set Width 900
Set Height 520
Type "python3 src/run_all.py" Enter
Sleep 3s
```

```bash
vhs docs/demo.tape          # needs: vhs + ttyd + ffmpeg on PATH
gifsicle -O3 docs/demo.gif -o docs/demo.gif   # size pass, target <8 MB
```

Embed: `![demo](docs/demo.gif)`

## Browser preview (Playwright — for docs/preview.html)

See `docs/record_preview.py`:

```bash
python3 docs/record_preview.py
# screenshots -> docs/preview_shots/*.png (+ preview.gif if ffmpeg present)
```

## asciinema fallback (no GIF weight)

```bash
asciinema rec docs/demo.cast -c "python3 src/run_all.py"
# Share page -> "Share -> preview image link" SVG snippet for README
```

## Size rules

- GIF: width ≤960, ≤15 fps, <8 MB (GitHub soft cap).
- MP4 (docs site / Pages): `<video controls muted loop playsinline>` with poster PNG.
- Raw `.mp4` on `raw.githubusercontent.com` serves as octet-stream — use the **Pages** URL for `<video>` playback, raw URL for GIF/still fallback.
- Camo proxy caches README images (minutes–hours); bump `?v=` only when you must force refresh.
