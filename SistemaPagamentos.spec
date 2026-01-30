# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

project_dir = os.getcwd()

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        ("img", "img"),
    ],
    hiddenimports=collect_submodules("supabase"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SistemaPagamentos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # mude para False depois
)
