from genericpath import isdir
import sys
import os
import os.path as op
import shutil
from lib2to3.main import main


# read sources
SOURCE_DIR = r"../Scripts/"
DEST_DIR = r"../python3/"

ITEMS = [
    r"rhinoscript/",
    r"rhinoscriptsyntax.py",
    r"scriptcontext.py",
]


THIS_DIR = op.dirname(__file__)
print(f"{THIS_DIR=}")
ROOT_DIR = op.dirname(THIS_DIR)
print(f"{ROOT_DIR=}")

for item in ITEMS:
    source = op.normpath(op.join(THIS_DIR, SOURCE_DIR, item))
    dest = op.normpath(op.join(THIS_DIR, DEST_DIR, item))

    if op.exists(dest):
        print(f"Deleting {dest}")
        if op.isdir(dest):
            shutil.rmtree(dest)
        else:
            os.remove(dest)

    print(f"Copying to {dest}")
    if op.isdir(source):
        shutil.copytree(source, dest)
    else:
        shutil.copy(source, dest)

    # apply fixes
    print(f"Converting {dest}")
    main("lib2to3.fixes", args=["--write", "--nobackups", "--no-diffs", dest])
