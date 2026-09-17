"""Build the Dragonlord government icons from the user-approved crown art.

The supplied PNG contains a baked white/grey checkerboard.  Background pixels
are removed with an edge-connected flood fill so the crown's near-white metal
highlights are preserved exactly.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
import struct

from PIL import Image, ImageFilter


MOD_ROOT = Path(__file__).resolve().parent.parent
SOURCE = MOD_ROOT / "art_source" / "dragonlord_oligarchy_government_icon_user_source.png"
CUTOUT = MOD_ROOT / "art_source" / "dragonlord_oligarchy_government_icon_user_cutout.png"
PREVIEW = MOD_ROOT / "art_source" / "dragonlord_oligarchy_government_icon_user_preview_70.png"
INLINE = MOD_ROOT / "gfx" / "interface" / "icons" / "government_types" / "dragonlord_oligarchy_government.png"
PANEL = MOD_ROOT / "gfx" / "interface" / "icons" / "government_types" / "dragonlord_oligarchy_government.dds"


def is_background(pixel: tuple[int, int, int]) -> bool:
    """Accept the antialiased near-neutral shades used by the checkerboard."""
    lo = min(pixel)
    hi = max(pixel)
    return lo >= 185 and hi - lo <= 36


def extract_cutout(source: Image.Image) -> Image.Image:
    rgb = source.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    background = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def enqueue(x: int, y: int) -> None:
        index = y * width + x
        if not background[index] and is_background(pixels[x, y]):
            background[index] = 1
            queue.append((x, y))

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(height):
        enqueue(0, y)
        enqueue(width - 1, y)

    while queue:
        x, y = queue.popleft()
        if x:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)

    rgba = rgb.convert("RGBA")
    output = rgba.load()
    for y in range(height):
        row = y * width
        for x in range(width):
            if background[row + x]:
                # Transparent white RGB produces a bright fringe when the icon
                # is downsampled. Zero it before resampling so the alpha edge
                # blends toward black/transparent instead.
                output[x, y] = (0, 0, 0, 0)

    # The source was antialiased against the bright checkerboard, leaving a
    # narrow grey-white matte around its black outer shadow. Reconstruct those
    # pixels as translucent black instead of carrying the bright matte into the
    # 70px resample. Only pixels within twelve source pixels of transparency
    # are touched; the crown's own black gutter keeps the silver rim farther
    # inside and therefore unchanged.
    alpha = rgba.getchannel("A")
    transparent = alpha.point(lambda value: 255 if value == 0 else 0)
    near_transparency = transparent.filter(ImageFilter.MaxFilter(25))
    near_pixels = near_transparency.load()
    assumed_background = 242
    for y in range(height):
        for x in range(width):
            r, g, b, a = output[x, y]
            if not a or not near_pixels[x, y]:
                continue
            if max(r, g, b) - min(r, g, b) > 36:
                continue
            luminance = (r + g + b) // 3
            matte_alpha = round(255 * (1 - luminance / assumed_background))
            output[x, y] = (0, 0, 0, max(0, min(255, matte_alpha)))

    bbox = rgba.getbbox()
    if bbox is None:
        raise RuntimeError("Background extraction removed the entire image")
    return rgba.crop(bbox)


def fit_icon(cutout: Image.Image, size: int, max_width: int, max_height: int) -> Image.Image:
    scale = min(max_width / cutout.width, max_height / cutout.height)
    target = (
        max(1, round(cutout.width * scale)),
        max(1, round(cutout.height * scale)),
    )
    resized = cutout.resize(target, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    position = ((size - target[0]) // 2, (size - target[1]) // 2)
    canvas.alpha_composite(resized, position)
    return canvas


def add_recessed_shadow(
    icon: Image.Image,
    *,
    spread: int,
    blur: float,
    offset_y: int,
    opacity: int,
) -> Image.Image:
    """Add CK3-style black gutter and a small downward soft shadow."""
    alpha = icon.getchannel("A")
    expanded = alpha.filter(ImageFilter.MaxFilter(spread * 2 + 1)) if spread else alpha
    softened = expanded.filter(ImageFilter.GaussianBlur(blur))
    shifted = Image.new("L", icon.size, 0)
    shifted.paste(softened, (0, offset_y))
    shifted = shifted.point(lambda value: value * opacity // 255)

    shadow = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    shadow.putalpha(shifted)
    shadow.alpha_composite(icon)
    return shadow


def save_uncompressed_bgra_dds(image: Image.Image, path: Path) -> None:
    """Reuse the existing CK3-compatible header and replace its BGRA pixels."""
    template = path.read_bytes()
    if template[:4] != b"DDS " or len(template) < 128:
        raise RuntimeError(f"Not a usable DDS template: {path}")
    width = struct.unpack_from("<I", template, 16)[0]
    height = struct.unpack_from("<I", template, 12)[0]
    if image.size != (width, height):
        raise RuntimeError(f"DDS template is {width}x{height}, image is {image.size}")
    pixels = image.convert("RGBA").tobytes("raw", "BGRA")
    path.write_bytes(template[:128] + pixels)


def main() -> None:
    cutout = extract_cutout(Image.open(SOURCE))
    cutout.save(CUTOUT)

    inline = add_recessed_shadow(
        fit_icon(cutout, size=28, max_width=26, max_height=20),
        spread=0,
        blur=1.15,
        offset_y=1,
        opacity=120,
    )
    panel = add_recessed_shadow(
        fit_icon(cutout, size=70, max_width=64, max_height=48),
        spread=0,
        blur=2.8,
        offset_y=2,
        opacity=105,
    )
    inline.save(INLINE)
    panel.save(PREVIEW)
    save_uncompressed_bgra_dds(panel, PANEL)

    print(f"cutout={CUTOUT} {cutout.size}")
    print(f"inline={INLINE} {inline.size}")
    print(f"panel={PANEL} {panel.size}")


if __name__ == "__main__":
    main()
