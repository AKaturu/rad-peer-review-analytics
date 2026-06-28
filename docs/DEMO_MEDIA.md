# Demo Media

The repository demo assets are synthetic-only and safe for public GitHub use.

## Files

- `docs/assets/demo.gif` - README animation
- `docs/assets/demo.mp4` - downloadable demo clip
- `docs/assets/demo-poster.png` - static preview frame

## Regenerate

```bash
python -m pip install -e ".[media]"
python scripts/generate_demo_media.py
```

The generator renders a stable final frame and duplicates it for the GIF/MP4 so the demo does not flicker on GitHub.
