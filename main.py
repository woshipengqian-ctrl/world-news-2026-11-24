#!/usr/bin/env python3
"""make.fun entry for "Sum up 24 November's world news in one image".

Copies the committed news.png (a newspaper-style front page of Tuesday
24 November 2026) to /output/entry.png. Standard library only.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "news.png")


def main():
    out_dir = "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        out_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    try:
        shutil.copyfile(SRC, dst)
    except OSError:
        out_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(out_dir, exist_ok=True)
        dst = os.path.join(out_dir, "entry.png")
        shutil.copyfile(SRC, dst)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
