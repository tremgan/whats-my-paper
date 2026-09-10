# whats-my-paper

I find it really annoying that downloaded articles from publishers will have some randomly generated names for the download which makes it a nightmare to find them after downloading (im too lazy to rename them)

So this renames them to their actual title:

```
1706.03762v7.pdf  ->  attention-is-all-you-need.pdf
```

The title comes from the PDF's metadata where it has any, and otherwise from a layout parse of
the first page, taking the title/heading with the most words.

## Install

Needs [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer. If you don't have uv:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install straight from GitHub — no need to clone:

```sh
uv tool install git+https://github.com/tremgan/whats-my-paper
```

That puts a `whats-my-paper` command on your PATH, in its own isolated environment, so it
won't touch any other Python you have installed. Check it worked:

```sh
whats-my-paper --help
```

If the command isn't found, run `uv tool update-shell` and open a new terminal.

To upgrade later, or to remove it:

```sh
uv tool upgrade whats-my-paper
uv tool uninstall whats-my-paper
```

### From a clone

If you've cloned the repo, install it the same way from the project root:

```sh
uv tool install .
```

### Working on it

To hack on the code instead, `uv sync` sets up a `.venv` with the dependencies, and `uv run`
runs your working copy without installing anything:

```sh
uv sync
uv run whats-my-paper scan ~/Downloads
```

### A note on size

There are two separate downloads, and both are large:

1. **Installing** pulls in docling, which depends on PyTorch — roughly a gigabyte of packages.
   Expect it to take a few minutes.
2. **The first PDF that needs the layout parse** downloads docling's model weights, about 500 MB,
   into `~/.cache/huggingface/hub`. This happens on first use, not at install time, so that run
   will stall for a while with no obvious explanation. Later runs use the cache and work offline.

PDFs whose title is in their metadata never touch the layout parse, so if you're lucky you may
never trigger the second download at all.

## Usage

See which files in a folder look auto-generated:

```sh
whats-my-paper scan ~/Downloads
```

Preview the renames without touching anything:

```sh
whats-my-paper rename ~/Downloads --preview
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

The first PDF that falls back to the layout parse downloads docling's model weights (~500 MB, into
`~/.cache/huggingface/hub`); after that it runs offline.
