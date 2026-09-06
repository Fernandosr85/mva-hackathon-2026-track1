#!/usr/bin/env python3
"""Remove all cell outputs from a Jupyter notebook, or verify that none remain.

Why this exists
---------------
Executed cells in this analysis embed per-variant genotype tables (position,
ref/alt, GT, DP, VAF, PID/PGT) in the notebook JSON. That is DELETE-list
material under the challenge Data Use terms, and this repository becomes
public after the hackathon closes. A notebook is only safe to commit when
every code cell has ``outputs == []`` and ``execution_count is None``.

Cell source and markdown are preserved exactly: only output-bearing keys are
touched, and the file is rewritten with the same JSON structure.

Usage
-----
    python scripts/strip_outputs.py in.ipynb out.ipynb   # strip
    python scripts/strip_outputs.py --check nb.ipynb     # verify, exit 1 if dirty

``--check`` exits non-zero when any output or execution_count remains, so it
can be wired into a pre-commit hook:

    python scripts/strip_outputs.py --check notebooks/mva_track1_analysis.ipynb

Standard library only -- no nbconvert, no third-party imports.
"""

import argparse
import json
import sys
from pathlib import Path

# Keys that carry execution state. Anything here is removed or reset.
_EXECUTION_KEYS = ("execution_count", "outputs")


def load_notebook(path):
    """Read a notebook, failing with a clear message rather than a traceback."""
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"error: no such notebook: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {path} is not valid JSON ({exc})")


def dirty_cells(nb):
    """Return [(index, n_outputs, execution_count)] for cells carrying state.

    Indices are into the full cell list -- markdown cells included -- so they
    line up with what a notebook editor shows.
    """
    found = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        outputs = cell.get("outputs") or []
        count = cell.get("execution_count")
        if outputs or count is not None:
            found.append((i, len(outputs), count))
    return found


def strip(nb):
    """Clear outputs and execution_count in place. Returns cells changed."""
    changed = 0
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        if (cell.get("outputs") or []) or cell.get("execution_count") is not None:
            changed += 1
        cell["outputs"] = []
        cell["execution_count"] = None
        # Transient per-execution metadata (scroll state, timing, colab ids)
        # is dropped too; it can echo output size but carries no source.
        meta = cell.get("metadata", {})
        for key in ("collapsed", "scrolled", "execution", "ExecuteTime"):
            meta.pop(key, None)
    # Kernel state recorded at the notebook level, not in any cell.
    nb.get("metadata", {}).pop("widgets", None)
    return changed


def write_notebook(nb, path):
    """Write the notebook back as UTF-8 JSON with a trailing newline."""
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(nb, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Strip Jupyter notebook outputs, or verify none remain.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify only; exit non-zero if any output or execution_count remains",
    )
    parser.add_argument("notebook", type=Path, help="input notebook (.ipynb)")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="output notebook; omit to overwrite the input",
    )
    args = parser.parse_args(argv)

    if args.check and args.output is not None:
        parser.error("--check takes a single notebook and writes nothing")

    nb = load_notebook(args.notebook)

    if args.check:
        found = dirty_cells(nb)
        if not found:
            n_code = sum(
                1 for c in nb.get("cells", []) if c.get("cell_type") == "code"
            )
            print(f"clean: {args.notebook} ({n_code} code cells, no outputs)")
            return 0
        print(f"DIRTY: {args.notebook} has {len(found)} cell(s) with saved state:")
        for index, n_out, count in found:
            print(f"  cell {index}: {n_out} output(s), execution_count={count}")
        print("outputs may contain patient-derived genotype data; do not commit")
        return 1

    changed = strip(nb)
    destination = args.output or args.notebook
    write_notebook(nb, destination)
    print(f"stripped {changed} cell(s) -> {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
