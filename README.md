# XTEINK Font Maker

Convert TTF/OTF fonts to stock-XTEINK `.bin` fonts, with adjustable weight and
stroke thickening. Useful when XTF fonts cannot be used in Bluetooth mode.

## Run

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
uv run make_bin.py /path/to/font.otf
```

The BIN and a PNG preview are saved in `output/`. Copy the BIN into your reader's
font folder. Keep the width/height suffix in its filename.

Defaults: weight **500**, stroke expansion **0.5 px**, glyph size **36 px**,
cell **40×48 px**. For a lighter result:

```sh
uv run make_bin.py /path/to/font.otf --weight 450 --stroke 0.25
```

Preview three thickness options before converting:

```sh
uv run make_bin.py /path/to/font.otf --compare --preview-only
```

Remove `--preview-only` to generate all three BINs. See `--help` for size,
cell dimensions, and output-folder options. Weight adjusts the `wght` axis of
variable fonts; static fonts retain their original weight. Stroke expansion
works with both. Leave enough room in the cell to avoid clipping glyphs.

BIN output is 1-bit, with 65,536 Unicode BMP slots. Characters absent from the
source font are blank; non-BMP characters are not included. A 40×48 BIN is 15 MiB.
Unlike a threshold slider alone, this converter can expand the rendered strokes.

The packing layout was checked against the official web font maker; generated
fonts still need a visual check on your reader. Linux needs the FreeType shared
library (`sudo apt install libfreetype6` if missing).

Your fonts and generated files stay local and are ignored by Git. No source fonts,
downloaded website code, tests, or CI workflows are included. Not affiliated with
XTEINK. Licensed under [GPLv3](LICENSE).
