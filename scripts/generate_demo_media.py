"""Generate stable synthetic demo media for the GitHub README."""

from __future__ import annotations

from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "docs" / "assets"
WIDTH = 1280
HEIGHT = 720


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for name in names:
        path = Path(name)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str) -> None:
    draw.rounded_rectangle(box, radius=18, fill=fill)


def label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    size: int,
    color: str,
    bold: bool = False,
) -> None:
    draw.text(xy, text, fill=color, font=font(size, bold))


def render_frame() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#f6f7fb")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH, 92), fill="#16233f")
    label(draw, (44, 28), "rad-peer-review-analytics", 34, "#ffffff", True)
    label(draw, (890, 34), "Synthetic peer review demo", 20, "#c8d3e8")

    rounded(draw, (44, 122, 382, 300), "#ffffff")
    label(draw, (72, 148), "Reviews", 22, "#5b6475", True)
    label(draw, (72, 188), "50", 62, "#1b315e", True)
    label(draw, (178, 212), "synthetic cases", 22, "#5b6475")
    label(draw, (72, 260), "5 reviewers  |  RADPEER + standard scores", 20, "#667085")

    rounded(draw, (416, 122, 754, 300), "#ffffff")
    label(draw, (444, 148), "Agreement Rate", 22, "#5b6475", True)
    label(draw, (444, 188), "60.0%", 62, "#157347", True)
    label(draw, (444, 260), "30 agreement scores in the demo cohort", 20, "#667085")

    rounded(draw, (788, 122, 1126, 300), "#ffffff")
    label(draw, (816, 148), "Major Discrepancy", 22, "#5b6475", True)
    label(draw, (816, 188), "10.0%", 62, "#b42318", True)
    label(draw, (816, 260), "5 high-priority reviews surfaced", 20, "#667085")

    rounded(draw, (44, 330, 620, 650), "#ffffff")
    label(draw, (72, 358), "Reviewer performance", 25, "#243b67", True)
    rows = [
        ("Reviewer", "Reviews", "Agreement", "Trend"),
        ("R001001", "13", "69.2%", "up"),
        ("R001002", "10", "60.0%", "stable"),
        ("R001003", "9", "55.6%", "down"),
        ("R001004", "8", "62.5%", "stable"),
    ]
    y = 410
    for index, row in enumerate(rows):
        fill = "#eef2f7" if index == 0 else "#ffffff"
        draw.rectangle((72, y - 9, 590, y + 34), fill=fill)
        label(draw, (88, y), row[0], 17, "#2f3a4f", index == 0)
        label(draw, (240, y), row[1], 17, "#2f3a4f", index == 0)
        label(draw, (356, y), row[2], 17, "#2f3a4f", index == 0)
        label(draw, (500, y), row[3], 17, "#2f3a4f", index == 0)
        y += 50

    rounded(draw, (660, 330, 1236, 650), "#ffffff")
    label(draw, (688, 358), "Monthly discrepancy trend", 25, "#243b67", True)
    chart = (708, 430, 1188, 594)
    draw.rectangle(chart, outline="#d8dee9", width=2)
    points = [(724, 548), (800, 516), (876, 530), (952, 488), (1028, 500), (1104, 454), (1172, 466)]
    draw.line(points, fill="#b42318", width=5)
    for x, y_coord in points:
        draw.ellipse((x - 7, y_coord - 7, x + 7, y_coord + 7), fill="#b42318")
    label(draw, (708, 610), "Jan", 16, "#667085")
    label(draw, (862, 610), "Mar", 16, "#667085")
    label(draw, (1018, 610), "May", 16, "#667085")
    label(draw, (1150, 610), "Jul", 16, "#667085")

    label(
        draw,
        (44, 676),
        "Reproducible synthetic data only - no patient or institutional records.",
        18,
        "#667085",
    )
    return image


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    frame = render_frame()
    frame.save(ASSET_DIR / "demo-poster.png")
    frames = [frame.copy() for _ in range(4)]
    frames[0].save(
        ASSET_DIR / "demo.gif", save_all=True, append_images=frames[1:], duration=650, loop=0
    )
    with imageio.get_writer(ASSET_DIR / "demo.mp4", fps=1, codec="libx264", quality=8) as writer:
        for still in frames:
            writer.append_data(np.asarray(still))


if __name__ == "__main__":
    main()
