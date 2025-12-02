#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract each LaTeX figure environment from Latex/main.tex into its own standalone .tex file
(compilable with latexmk into a PDF), and replace the original figure with an \\includegraphics
that includes the generated PDF in main.tex.

- Output directory: Latex/figures
- Figure filename: uses label if present (e.g., fig:organismos -> fig_organismos.tex/pdf),
    otherwise figure_001.tex/pdf, figure_002.tex/pdf, ...
- Keeps the original caption and label in main.tex; the figure body is replaced by \\includegraphics.
- Assumes figures are TikZ pictures; the standalone figure uses the standalone class and loads
    the same TikZ libs seen in the preamble.

Edge cases handled:
- Optional placement [..] in \\begin{figure}[...]
- Nested environments within figure
- Multiple \\label inside: uses the first figure-scoped label

Limitations:
- Only processes environments strictly delimited by \\begin{figure} ... \\end{figure} (case-sensitive)
- Requires Python 3.9+
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.tex"
OUT_DIR = ROOT / "figures"

STANDALONE_TEMPLATE = r"""%% !TEX program = latexmk
\documentclass[tikz,border=2pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage{microtype}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,fit,calc}

\begin{document}
%s
\end{document}
"""

INCLUDE_TEMPLATE = r"""
\begin{figure}%s
    \centering
    \includegraphics{%s}
%s%s\end{figure}
"""

LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
CAPTION_RE = re.compile(r"\\caption\{(.*?)\}", re.DOTALL)

BEGIN_RE = re.compile(r"^\\begin\{figure\}(\[[^\]]*\])?", re.MULTILINE)
END_RE = re.compile(r"^\\end\{figure\}", re.MULTILINE)


def sanitize_label(label: str) -> str:
    # Convert LaTeX label like fig:foo-bar to file-friendly fig_foo_bar
    base = re.sub(r"[^a-zA-Z0-9:_-]", "_", label)
    base = base.replace(":", "_")
    base = base.replace("-", "_")
    base = re.sub(r"_+", "_", base).strip("_")
    return base


def extract_figures(tex: str):
    figures = []
    pos = 0
    idx = 1
    while True:
        m = BEGIN_RE.search(tex, pos)
        if not m:
            break
        start = m.start()
        opt = m.group(1) or ""
        # Find matching end by scanning, accounting for nested figures (rare) but safe
        nest = 1
        i = m.end()
        while nest > 0:
            m2 = BEGIN_RE.search(tex, i)
            e2 = END_RE.search(tex, i)
            if not e2:
                raise RuntimeError("Unmatched \\begin{figure} without \\end{figure}")
            if m2 and m2.start() < e2.start():
                nest += 1
                i = m2.end()
            else:
                nest -= 1
                i = e2.end()
        end = i
        block = tex[
            m.end() : e2.start()
        ]  # content inside figure, excluding begin/end lines

        # Capture caption and label within the block
        cap_m = CAPTION_RE.search(block)
        caption = cap_m.group(0) if cap_m else ""
        label_m = LABEL_RE.search(block)
        label = label_m.group(1) if label_m else None

        if label:
            stem = sanitize_label(label)
        else:
            stem = f"figure_{idx:03d}"
        idx += 1

        figures.append(
            {
                "range": (start, end),
                "opt": opt,
                "content": block.strip(),
                "caption": caption,
                "label": (label_m.group(0) if label_m else ""),
                "stem": stem,
            }
        )
        pos = end
    return figures


def main():
    if not MAIN.exists():
        print(f"main.tex not found at {MAIN}", file=sys.stderr)
        sys.exit(1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tex = MAIN.read_text(encoding="utf-8")
    figures = extract_figures(tex)
    if not figures:
        print("No figure environments found.")
        return

    # Write standalone files and build replacement blocks
    replacements = []
    for fig in figures:
        # Remove caption/label from standalone content; they will live in main.tex include
        content_clean = CAPTION_RE.sub("", fig["content"])
        content_clean = LABEL_RE.sub("", content_clean)
        standalone_tex = STANDALONE_TEMPLATE % content_clean
        fig_path = OUT_DIR / f"{fig['stem']}.tex"
        fig_path.write_text(standalone_tex, encoding="utf-8")
        # Path to include is relative to main: figures/<stem>.pdf
        pdf_rel = f"figures/{fig['stem']}.pdf"
        # Build optional caption and label lines (caption first, then label if present)
        cap_line = "\n    " + fig["caption"] if fig["caption"] else ""
        lab_line = "\n    " + fig["label"] if fig["label"] else ""
        repl = INCLUDE_TEMPLATE % (fig["opt"], pdf_rel, cap_line, lab_line)
        # Ensure endline alignment
        replacements.append((fig["range"], repl))

    # Apply replacements in reverse order to preserve indices
    new_tex = tex
    for (start, end), repl in sorted(replacements, key=lambda x: x[0][0], reverse=True):
        new_tex = new_tex[:start] + repl + new_tex[end:]

    MAIN.write_text(new_tex, encoding="utf-8")
    print(
        f"Extracted {len(figures)} figures to {OUT_DIR.relative_to(ROOT)} and rewrote main.tex"
    )


if __name__ == "__main__":
    main()
