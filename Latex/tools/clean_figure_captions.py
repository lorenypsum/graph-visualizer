#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove \\caption{...} and \\label{...} from standalone figure .tex files in Latex/figures"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
CAPTION_RE = re.compile(r"\\caption\{.*?\}\s*", re.DOTALL)
LABEL_RE = re.compile(r"\\label\{[^}]+\}\s*")


def main():
    for tex in FIG_DIR.glob("*.tex"):
        s = tex.read_text(encoding="utf-8")
        s2 = CAPTION_RE.sub("", s)
        s2 = LABEL_RE.sub("", s2)
        if s2 != s:
            tex.write_text(s2, encoding="utf-8")
            print(f"Cleaned captions/labels: {tex.name}")


if __name__ == "__main__":
    main()
