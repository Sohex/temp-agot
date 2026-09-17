from pathlib import Path
from math import cos, pi, sin

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


MOD_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = MOD_ROOT.parent
ICON_DIR = MOD_ROOT / "gfx/interface/icons/dragonlord_council"
BACKGROUND_DIR = MOD_ROOT / "gfx/interface/illustrations/dragonlord_council"
CARD_EXPORT_DIR = SOURCE_ROOT / "卡片裁切输出"

RESAMPLE = Image.Resampling.LANCZOS
ICON_FRAME_SIZE = 160
ICON_ATLAS_SIZE = (ICON_FRAME_SIZE * 3, ICON_FRAME_SIZE)
# The custom council cards are 250x700. Matching that aspect ratio here keeps
# the UI renderer from squeezing the artwork horizontally.
BACKGROUND_SIZE = (560, 1568)


def irregular_circle_points(
    center: int,
    radius: float,
    scale: int,
    phase: float,
    roughness: float,
    start_angle: float = 0.0,
    end_angle: float = 2 * pi,
    steps: int = 240,
) -> list[tuple[float, float]]:
    """Create a repeatable, hand-worked circular edge without random output."""
    points = []
    for index in range(steps + 1):
        angle = start_angle + (end_angle - start_angle) * index / steps
        wobble = (
            sin(angle * 5 + phase) * 0.48
            + sin(angle * 11 + phase * 1.7) * 0.32
            + sin(angle * 23 - phase * 0.8) * 0.20
        )
        local_radius = (radius + roughness * wobble) * scale
        points.append(
            (
                center + cos(angle) * local_radius,
                center + sin(angle) * local_radius,
            )
        )
    return points


def irregular_ring_mask(
    size: int,
    center: int,
    scale: int,
    outer_radius: float,
    inner_radius: float,
    phase: float,
    outer_roughness: float,
    inner_roughness: float,
) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(
        irregular_circle_points(center, outer_radius, scale, phase, outer_roughness),
        fill=255,
    )
    draw.polygon(
        irregular_circle_points(center, inner_radius, scale, phase + 0.9, inner_roughness),
        fill=0,
    )
    return mask


def fit_background(
    source: Path,
    destination: Path,
    horizontal_anchor: float,
    brightness: float = 1.0,
) -> None:
    with Image.open(source) as image:
        image = image.convert("RGB")
        fitted = ImageOps.fit(
            image,
            BACKGROUND_SIZE,
            method=RESAMPLE,
            centering=(horizontal_anchor, 0.5),
        )
        if brightness != 1.0:
            fitted = ImageEnhance.Brightness(fitted).enhance(brightness)
        fitted.save(destination, format="DDS", pixel_format="DXT1")


def export_background(source: Path, destination: Path, horizontal_anchor: float) -> None:
    """Export the exact untinted card crop as a lossless PNG for manual editing."""
    with Image.open(source) as image:
        fitted = ImageOps.fit(
            image.convert("RGB"),
            BACKGROUND_SIZE,
            method=RESAMPLE,
            centering=(horizontal_anchor, 0.5),
        )
        fitted.save(destination, format="PNG", optimize=True)


def make_icon_frame(source: Image.Image, ring_color: tuple[int, int, int], state: int) -> Image.Image:
    scale = 4
    size = ICON_FRAME_SIZE * scale
    center = size // 2

    brightness = (1.0, 0.72, 1.08)[state]
    ring_brightness = (1.0, 0.72, 1.30)[state]
    content = ImageOps.fit(source, (136 * scale, 136 * scale), method=RESAMPLE)
    content = ImageEnhance.Brightness(content).enhance(brightness)

    circular_mask = Image.new("L", (136 * scale, 136 * scale), 0)
    ImageDraw.Draw(circular_mask).ellipse((0, 0, 136 * scale - 1, 136 * scale - 1), fill=255)

    frame = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse(
        (5 * scale, 7 * scale, 155 * scale, 157 * scale),
        fill=(0, 0, 0, 190),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(3 * scale))
    frame.alpha_composite(shadow)

    content_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    content_layer.paste(content, (12 * scale, 12 * scale), circular_mask)
    frame.alpha_composite(content_layer)

    ring = tuple(min(255, round(channel * ring_brightness)) for channel in ring_color)

    # Vanilla lifestyle icons use a painted, uneven rim baked into each frame.
    # Reproduce that character with several independently roughened metal bands
    # rather than a mathematically perfect ellipse.
    ring_specs = (
        (75.0, 67.0, 0.35, 1.8, 1.25, (18, 16, 15, 255)),
        (72.8, 67.8, 1.65, 1.45, 1.15, (*ring, 255)),
        (69.3, 66.0, 2.80, 1.00, 0.80, (18, 17, 17, 225)),
    )
    for outer_radius, inner_radius, phase, outer_roughness, inner_roughness, color in ring_specs:
        ring_layer = Image.new("RGBA", (size, size), color)
        ring_mask = irregular_ring_mask(
            size,
            center,
            scale,
            outer_radius,
            inner_radius,
            phase,
            outer_roughness,
            inner_roughness,
        )
        frame.alpha_composite(Image.composite(ring_layer, Image.new("RGBA", (size, size)), ring_mask))

    # Broken highlights and darker wear marks keep the rim from reading as a
    # vector stroke after it is reduced to the final 160px frame.
    wear = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    wear_draw = ImageDraw.Draw(wear)
    highlight = tuple(min(255, channel + 58) for channel in ring)
    wear_draw.line(
        irregular_circle_points(
            center, 70.7, scale, 0.8, 0.55,
            start_angle=pi * 1.08,
            end_angle=pi * 1.58,
            steps=70,
        ),
        fill=(*highlight, 150),
        width=1 * scale,
        joint="curve",
    )
    wear_draw.line(
        irregular_circle_points(
            center, 71.1, scale, 2.1, 0.70,
            start_angle=pi * 0.02,
            end_angle=pi * 0.48,
            steps=65,
        ),
        fill=(8, 7, 7, 125),
        width=2 * scale,
        joint="curve",
    )
    for angle, radius, shade in (
        (0.64, 71.8, 0),
        (1.92, 69.8, 1),
        (2.75, 72.2, 0),
        (3.73, 70.1, 1),
        (4.55, 72.0, 1),
        (5.62, 69.7, 0),
    ):
        x = center + cos(angle) * radius * scale
        y = center + sin(angle) * radius * scale
        spot_color = (*highlight, 120) if shade else (9, 8, 8, 155)
        spot_radius = (1.0 if shade else 1.5) * scale
        wear_draw.ellipse(
            (x - spot_radius, y - spot_radius, x + spot_radius, y + spot_radius),
            fill=spot_color,
        )
    frame.alpha_composite(wear)

    return frame.resize((ICON_FRAME_SIZE, ICON_FRAME_SIZE), RESAMPLE)


def build_icon(
    source: Path,
    destination: Path,
    ring_color: tuple[int, int, int],
    crop_box: tuple[int, int, int, int] | None = None,
) -> None:
    with Image.open(source) as image:
        source_image = image.convert("RGB")
        if crop_box is not None:
            source_image = source_image.crop(crop_box)
        atlas = Image.new("RGBA", ICON_ATLAS_SIZE, (0, 0, 0, 0))
        for state in range(3):
            atlas.alpha_composite(make_icon_frame(source_image, ring_color, state), (state * 160, 0))
        atlas.save(destination, format="DDS", pixel_format="DXT5")


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    BACKGROUND_DIR.mkdir(parents=True, exist_ok=True)
    CARD_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    build_icon(SOURCE_ROOT / "图标-征服.png", ICON_DIR / "conquest.dds", (112, 45, 38))
    build_icon(SOURCE_ROOT / "图标-发展.png", ICON_DIR / "development.dds", (82, 108, 148))
    build_icon(SOURCE_ROOT / "图标-祭祀.png", ICON_DIR / "ritual.dds", (105, 63, 39))
    # Tight square crop centered on the question mark, with a neutral gray ring.
    build_icon(
        SOURCE_ROOT / "等待开发.png",
        ICON_DIR / "in_development.dds",
        (92, 92, 92),
        crop_box=(283, 480, 803, 1000),
    )

    # The manually graded files already have the final 560x1568 crop.
    fit_background(CARD_EXPORT_DIR / "议会-征服_调色.png", BACKGROUND_DIR / "conquest.dds", 0.50)
    fit_background(CARD_EXPORT_DIR / "议会-祭祀_调色.png", BACKGROUND_DIR / "ritual.dds", 0.50)
    fit_background(
        SOURCE_ROOT / "等待开发.png",
        BACKGROUND_DIR / "in_development.dds",
        0.50,
        brightness=0.60,
    )
    fit_background(CARD_EXPORT_DIR / "议会-发展_调色.png", BACKGROUND_DIR / "development.dds", 0.50)

    export_background(SOURCE_ROOT / "议会-征服.png", CARD_EXPORT_DIR / "议会-征服_裁切.png", 0.25)
    export_background(SOURCE_ROOT / "议会-发展.png", CARD_EXPORT_DIR / "议会-发展_裁切.png", 0.62)
    export_background(SOURCE_ROOT / "议会-祭祀.png", CARD_EXPORT_DIR / "议会-祭祀_裁切.png", 0.50)
    export_background(SOURCE_ROOT / "等待开发.png", CARD_EXPORT_DIR / "等待开发_裁切.png", 0.50)


if __name__ == "__main__":
    main()
