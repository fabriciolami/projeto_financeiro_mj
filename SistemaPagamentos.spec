# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Supabase core
        "supabase",

        # Auth
        "gotrue",
        "gotrue.errors",

        # Database
        "postgrest",
        "postgrest.errors",

        # Realtime / storage
        "realtime",
        "storage3",

        # HTTP stack
        "httpx",
        "httpcore",
        "anyio",

        # Websocket (usado pelo realtime)
        "websockets",
    ],
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
    name='SistemaPagamentos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
