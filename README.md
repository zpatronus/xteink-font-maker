# XTEINK Font Maker

Convert TTF/OTF fonts to 1-bit BIN fonts for stock XTEINK firmware, with
adjustable variable-font weight and stroke expansion.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uv run make_bin.py /path/to/font.otf
```

By default, generate 12 BINs and a 4×3 comparison: rows are weights 450, 480,
500, and 550; columns are stroke expansions of 0, 0.25, and 0.5 px.
Glyph size is 36 px, in 40×48 cells.
BINs and PNG previews go to `output/`. Copy the BIN to your reader's font folder;
preserve the `_40x48.bin` suffix because the reader uses the dimensions.
Linux requires the FreeType shared library (`libfreetype6`). See `--help` for options.
Chinese punctuation preserves the source font's side bearings within each cell;
other glyphs retain their existing centering. BIN cells remain fixed-width.

Generate a single font by specifying a weight and/or stroke expansion:

```sh
uv run make_bin.py /path/to/font.otf --weight 480 --stroke 0.25
```

Preview them without generating BINs:

```sh
uv run make_bin.py /path/to/font.otf --preview-only
```

`--compare` explicitly selects the same default grid. Single-font defaults are
weight 500 and stroke expansion 0 px when only one of the two is specified.

![Four rows: weights 450, 480, 500, and 550. Three columns: stroke expansion 0, 0.25, and 0.5 px.](examples/comparison.png)

The sample is the closing passage of Fan Zhongyan's
[*岳阳楼记*](https://jjc.mku.edu.cn/info/1071/1971.htm), set in simplified Chinese
with modern punctuation. The same passage appears in each panel to compare
fine strokes, dense characters, and punctuation in normal reading.

These examples were generated from Source Han Serif SC version 2.003 at 36 px,
in 40×48 cells, as 1-bit fonts for stock XTEINK firmware. Each contains 65,536
Unicode BMP slots and is 15,728,640 bytes (15 MiB); missing characters are blank.
The download table follows the same rows and columns as the preview.

| Weight | 0 px expansion | 0.25 px expansion | 0.5 px expansion |
| ---: | --- | --- | --- |
| 450 | [BIN](examples/fonts/SourceHanSerifSC_w450_stroke0_40x48.bin) | [BIN](examples/fonts/SourceHanSerifSC_w450_stroke0p25_40x48.bin) | [BIN](examples/fonts/SourceHanSerifSC_w450_stroke0p5_40x48.bin) |
| 480 | [BIN](examples/fonts/SourceHanSerifSC_w480_stroke0_40x48.bin) | [BIN](examples/fonts/SourceHanSerifSC_w480_stroke0p25_40x48.bin) | [BIN](examples/fonts/SourceHanSerifSC_w480_stroke0p5_40x48.bin) |
| 500 | [BIN](examples/fonts/SourceHanSerifSC_w500_stroke0_40x48.bin) | [BIN](examples/fonts/SourceHanSerifSC_w500_stroke0p25_40x48.bin) | [BIN](examples/fonts/SourceHanSerifSC_w500_stroke0p5_40x48.bin) |
| 550 | [BIN](examples/fonts/SourceHanSerifSC_w550_stroke0_40x48.bin) | [BIN](examples/fonts/SourceHanSerifSC_w550_stroke0p25_40x48.bin) | [BIN](examples/fonts/SourceHanSerifSC_w550_stroke0p5_40x48.bin) |

The Python app is [GPL-3.0-only](LICENSE). The converted example fonts are
separately licensed under [SIL OFL 1.1](examples/fonts/OFL.txt); see their
[notices](examples/fonts/NOTICE.md). Source OTF files are not included.
