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

The generator creates a three-step guided walkthrough of cohort summary, reviewer-level performance, and the monthly discrepancy trend. The GIF is the inline GitHub preview; the MP4 is the full browser-playable clip.
