# whats-my-paper

I find it really annoying that downloaded articles from publishers will have some randomly generated names for the download which makes it a nightmare to find them after downloading (im too lazy to rename them)

So this renames them to their actual title:

```
1706.03762v7.pdf  ->  attention-is-all-you-need.pdf
```

The title comes from the PDF's metadata where it has any, and otherwise from a layout parse of
the first page, taking the title/heading with the most words.

## Install

```sh
uv tool install .
```

## Usage

See which files in a folder look auto-generated:

```sh
whats-my-paper scan ~/Downloads
```

Preview the renames without touching anything:

```sh
whats-my-paper rename ~/Downloads --dry-run
```

Do it:

```sh
whats-my-paper rename ~/Downloads
```

Each rename is printed as it happens. Pointed at a directory, `rename` only touches the files `scan` flags. Pointed at a single file it
always renames it. Existing files are never overwritten — a clash gets a `-2` suffix — and a PDF
whose title can't be read is skipped rather than failing the batch.

## Notes

Only files whose name is at least 3/4 digits are flagged, so `Download.pdf` is left alone. Adjust
`numeric_percentage_strategy` in `titles.py` if you want a different rule.

The first PDF that falls back to the layout parse downloads docling's models (a few hundred MB, to
`~/.cache/docling/models`); after that it runs offline.
