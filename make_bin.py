#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Convert TTF/OTF fonts into stock-XTEINK BIN fonts with adjustable strokes."""
import argparse
import re
import ctypes
import unicodedata
from pathlib import Path

import freetype
from PIL import Image, ImageDraw, ImageFilter, ImageOps

WEIGHTS = (450, 480, 500, 550)
STROKES = (0, .25, .5)

# Fan Zhongyan, Yueyang Lou Ji (岳阳楼记), closing passage.
SAMPLE = ('嗟夫！予尝求古仁人之心，或异二者之为，何哉？',
          '不以物喜，不以己悲；居庙堂之高则忧其民；',
          '处江湖之远则忧其君。是进亦忧，退亦忧。',
          '然则何时而乐耶？其必曰：“先天下之忧而忧，',
          '后天下之乐而乐”乎！噫！微斯人，吾谁与归？')


class Renderer:
    def __init__(self, font, weight, stroke, size=36, width=40, height=48):
        self.face = freetype.Face(str(font))
        if self.face.has_multiple_masters:
            axes = self.face.get_variation_info().axes
            coords = [a.default for a in axes]
            for index, axis in enumerate(axes):
                if axis.tag == "wght":
                    if not axis.minimum <= weight <= axis.maximum:
                        raise ValueError(f"Weight must be {axis.minimum:g}–{axis.maximum:g}")
                    coords[index] = weight
            self.face.set_var_design_coords(coords)
        self.scale = 4
        self.face.set_pixel_sizes(0, size * self.scale)
        self.width, self.height = width, height
        self.baseline = size
        self.radius = round(stroke * self.scale)
        self.characters = {cp for cp, _ in self.face.get_chars() if cp < 65536}

    def glyph(self, codepoint):
        scale = self.scale
        canvas = Image.new('L', (self.width * scale, self.height * scale))
        if codepoint not in self.characters or chr(codepoint).isspace() or codepoint < 32:
            return canvas.resize((self.width, self.height))
        self.face.load_char(chr(codepoint), freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
        glyph = self.face.glyph
        bitmap = glyph.bitmap
        if bitmap.width and bitmap.rows:
            raw = ctypes.string_at(bitmap._FT_Bitmap.buffer, abs(bitmap.pitch) * bitmap.rows)
            mask = Image.frombytes('L', (bitmap.width, bitmap.rows), raw,
                                   'raw', 'L', bitmap.pitch)
            x = (self.width * scale - bitmap.width) // 2
            char = chr(codepoint)
            if (unicodedata.category(char).startswith('P')
                    and (unicodedata.east_asian_width(char) in ('W', 'F')
                         or char in '“”‘’')):
                # Preserve punctuation's side bearings inside its advance box.
                # Opening marks sit toward the following text; closing marks
                # and SC pause/stop marks sit toward the preceding text.
                advance = glyph.advance.x / 64
                x = round((self.width * scale - advance) / 2) + glyph.bitmap_left
            y = self.baseline * scale - glyph.bitmap_top
            canvas.paste(mask, (x, y))
        if self.radius:
            canvas = canvas.filter(ImageFilter.MaxFilter(2 * self.radius + 1))
        canvas = canvas.resize((self.width, self.height), Image.Resampling.LANCZOS)
        # Coverage, not luminance: 1 bits represent ink. Each row is byte padded.
        return canvas.point(lambda coverage: 255 if coverage >= 96 else 0, mode='1')

    def preview(self, title):
        image = Image.new('RGB', (max(840, 24 + max(map(len, SAMPLE))*self.width), 60 + len(SAMPLE)*self.height), 'white')
        draw = ImageDraw.Draw(image)
        draw.text((12, 10), title, fill='black')
        for row, text in enumerate(SAMPLE):
            for col, char in enumerate(text):
                glyph = self.glyph(ord(char)).convert('L')
                image.paste(ImageOps.invert(glyph), (12 + col * self.width, 40 + row * self.height))
        return image

    def write(self, destination):
        stride = ((self.width + 7) // 8) * self.height
        temporary = destination.with_suffix(".bin.part")
        with open(temporary, 'wb') as output:
            for cp in range(65536):
                packed = self.glyph(cp).convert('1').tobytes()
                assert len(packed) == stride
                output.write(packed)
                if cp % 8192 == 0:
                    print(f'{destination.name}: {cp}/65536', flush=True)
        assert temporary.stat().st_size == stride * 65536
        temporary.replace(destination)
        # Decode sample slots from the actual file and compare to rendered glyphs.
        with open(destination, 'rb') as stream:
            for cp in map(ord, '天地国思源宋体Ag，。'):
                stream.seek(cp * stride)
                decoded = Image.frombytes('1', (self.width, self.height), stream.read(stride))
                assert decoded.tobytes() == self.glyph(cp).tobytes()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('font', type=Path)
    parser.add_argument('--preview-only', action='store_true')
    parser.add_argument('--weight', type=float, help='Generate one weight instead of the grid (single-font default: 500)')
    parser.add_argument('--stroke', type=float, help='Generate one expansion instead of the grid (single-font default: 0 px)')
    parser.add_argument('--size', type=int, default=36, help='Glyph size in pixels')
    parser.add_argument('--width', type=int, default=40, help='Cell width')
    parser.add_argument('--height', type=int, default=48, help='Cell height')
    parser.add_argument('--compare', action='store_true', help='Generate the default 4-row, 3-column weight/expansion grid')
    parser.add_argument('--output', type=Path, default=Path('output'))
    args = parser.parse_args()
    if not args.font.is_file():
        parser.error('Input font does not exist')
    if not 1 <= args.size <= 255 or not 1 <= args.width <= 255 or not 1 <= args.height <= 255:
        parser.error('Size and cell dimensions must be in 1–255')
    if args.stroke is not None and not 0 <= args.stroke <= 4:
        parser.error('Stroke must be in 0–4 pixels')
    if args.compare and (args.weight is not None or args.stroke is not None):
        parser.error('--compare cannot be combined with --weight or --stroke; omit --compare to generate a single font')
    grid = args.weight is None and args.stroke is None
    target = args.output
    target.mkdir(parents=True, exist_ok=True)
    variants = ([(weight, stroke) for weight in WEIGHTS for stroke in STROKES]
                if grid else [(args.weight if args.weight is not None else 500,
                               args.stroke if args.stroke is not None else 0)])
    family = re.sub(r'[^A-Za-z0-9_-]+', '_', args.font.stem)
    panels = []
    for weight, stroke in variants:
        stroke_tag = f'{stroke:g}'.replace('.', 'p')
        name = f'{family}_w{weight:g}_stroke{stroke_tag}_{args.width}x{args.height}'
        renderer = Renderer(args.font, weight, stroke, args.size, args.width, args.height)
        panels.append(renderer.preview(f'Weight {weight:g}, stroke {stroke}px, {args.size}px, cell {args.width}x{args.height}'))
        if not args.preview_only:
            renderer.write(target / (name + '.bin'))
    panel_width, panel_height = panels[0].size
    columns = len(STROKES) if grid else 1
    rows = len(WEIGHTS) if grid else 1
    preview = Image.new('RGB', (panel_width * columns, panel_height * rows), 'white')
    for index, panel in enumerate(panels):
        preview.paste(panel, (panel_width * (index % columns), panel_height * (index // columns)))
    draw = ImageDraw.Draw(preview)
    for column in range(1, columns):
        draw.line((column * panel_width, 0, column * panel_width, preview.height - 1), fill='#dddddd')
    for row in range(1, rows):
        draw.line((0, row * panel_height, preview.width - 1, row * panel_height), fill='#dddddd')
    preview.save(target / 'comparison.png')
    print('Saved comparison.png', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, freetype.FT_Exception) as exc:
        raise SystemExit(str(exc)) from exc
