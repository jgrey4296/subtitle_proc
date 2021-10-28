#!/usr/bin/env python3

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "subtitle_processor",
    version = "0.1",
    description = "Cleans SRT caption files",
    options = {"build_exe": build_exe_options},
    executables = [Executable("sub_processor.py", base=base)]
)
