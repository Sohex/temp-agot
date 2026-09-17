"""Build the three Dragonlord concept icons from approved painted sources.

Generated source PNGs contain a baked checkerboard. Remove it with an
edge-connected flood fill, then apply one shared CK3-style black keyline and
soft outer shadow so all three ranks have identical visual weight.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
import struct

from PIL import Image, ImageChops, ImageFilter


MOD_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = MOD_ROOT / "art_source"
OUTPUT_DIR = MOD_ROOT / "gfx" / "interface" / "icons" / "game_concepts"

RANKS = {
    "bronze": (
        SOURCE_DIR / "dragonlord_rank_bronze_source.png",
        OUTPUT_DIR / "dragonlord_dragonlords.dds",
    ),
    "silver": (
        SOURCE_DIR / "dragonlord_rank_silver_source.png",
        OUTPUT_DIR / "dragonlord_fourteen_dragonlords.dds",
    ),
    "gold": (
        SOURCE_DIR / "dragonlord_rank_gold_source.png",
        OUTPUT_DIR / "dragonlord_chief_dragonlord.dds",
    ),
}


def is_background(pixel: tuple[int, int, int]) -> bool:
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

    # Laurel branches can enclose pockets of the baked checkerboard. They are
    # not connected to the canvas edge, so remove only large enclosed neutral
    # components; the painted metal highlights are textured into much smaller
    # disconnected regions and remain intact.
    visited = bytearray(background)
    for start_y in range(height):
        for start_x in range(width):
            start_index = start_y * width + start_x
            if visited[start_index] or not is_background(pixels[start_x, start_y]):
                continue
            component: list[tuple[int, int]] = []
            component_queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
            visited[start_index] = 1
            while component_queue:
                x, y = component_queue.popleft()
                component.append((x, y))
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if nx < 0 or nx >= width or ny < 0 or ny >= height:
                        continue
                    index = ny * width + nx
                    if visited[index] or not is_background(pixels[nx, ny]):
                        continue
                    visited[index] = 1
                    component_queue.append((nx, ny))
            if len(component) >= 2000:
                for x, y in component:
                    background[y * width + x] = 1

    rgba = rgb.convert("RGBA")
    output = rgba.load()
    for y in range(height):
        row = y * width
        for x in range(width):
            if background[row + x]:
                output[x, y] = (0, 0, 0, 0)

    bbox = rgba.getbbox()
    if bbox is None:
        raise RuntimeError("Background extraction removed the entire image")
    return rgba.crop(bbox)


def fit_icon(cutout: Image.Image, size: int = 120, max_extent: int = 98) -> Image.Image:
    scale = min(max_extent / cutout.width, max_extent / cutout.height)
    target = (
        max(1, round(cutout.width * scale)),
        max(1, round(cutout.height * scale)),
    )
    resized = cutout.resize(target, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    position = ((size - target[0]) // 2, (size - target[1]) // 2)
    canvas.alpha_composite(resized, position)
    return canvas


def add_keyline_and_shadow(icon: Image.Image) -> Image.Image:
    """Add a solid black outline plus a wider fading black outer shadow."""
    alpha = icon.getchannel("A")

    outline_dilated = alpha.filter(ImageFilter.MaxFilter(5))
    outline_alpha = ImageChops.subtract(outline_dilated, alpha)
    outline_alpha = outline_alpha.point(lambda value: value * 235 // 255)
    outline = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    outline.putalpha(outline_alpha)

    shadow_alpha = alpha.filter(ImageFilter.MaxFilter(11))
    shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(3.0))
    shifted = Image.new("L", icon.size, 0)
    shifted.paste(shadow_alpha, (0, 2))
    shifted = shifted.point(lambda value: value * 115 // 255)
    shadow = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    shadow.putalpha(shifted)

    result = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    result.alpha_composite(shadow)
    result.alpha_composite(outline)
    result.alpha_composite(icon)
    return result


def save_uncompressed_bgra_dds(image: Image.Image, path: Path) -> None:
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
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    built: dict[str, Image.Image] = {}

    for rank, (source_path, output_path) in RANKS.items():
        cutout = extract_cutout(Image.open(source_path))
        cutout.save(SOURCE_DIR / f"dragonlord_rank_{rank}_cutout.png")
        icon = add_keyline_and_shadow(fit_icon(cutout))
        icon.save(SOURCE_DIR / f"dragonlord_rank_{rank}_preview_120.png")
        icon.resize((60, 60), Image.Resampling.LANCZOS).save(
            SOURCE_DIR / f"dragonlord_rank_{rank}_preview_60.png"
        )
        save_uncompressed_bgra_dds(icon, output_path)
        built[rank] = icon
        print(f"{rank}: source={source_path.name} output={output_path}")

    strip = Image.new("RGBA", (390, 150), (22, 25, 31, 255))
    for index, rank in enumerate(("bronze", "silver", "gold")):
        strip.alpha_composite(built[rank], (15 + index * 130, 15))
    strip.save(SOURCE_DIR / "dragonlord_rank_icons_preview.png")


if __name__ == "__main__":
    main()
