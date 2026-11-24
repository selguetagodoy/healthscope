#!/usr/bin/env python3
"""Assemble the small, dependency-free GitHub Pages publication directory."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dist"


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for name in ("index.html", "events.json", "robots.txt", "sitemap.xml", ".nojekyll", "README.md", "METHODOLOGY.md", "SOURCES.md", "DATA_DICTIONARY.md", "STATUS.md"):
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, DEST / name)
    for name in ("assets", "data"):
        source = ROOT / name
        if source.exists():
            shutil.copytree(source, DEST / name)
    print("Publicación preparada en dist/.")


if __name__ == "__main__":
    main()
