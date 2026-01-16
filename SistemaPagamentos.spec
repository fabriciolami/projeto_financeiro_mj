# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# --------------------------------------------------
# COLETA DE LIBS DINÂMICAS
# --------------------------------------------------
datas_sb, binaries_sb, hidden_sb = collect_all("supabase")
datas_pg, binaries_pg, hidden_pg = collect_all("postgrest")
datas_rt, binaries_rt, hidden_rt = collect_all("realtime")
datas_st, binaries_st, hidden_st = collect_all("storage3")
datas_rl, binaries_rl, hidden_rl = collect_all("reportlab")

# --------------------------------------------------
# HIDDEN IMPORTS
# --------------------------------------------------
hidden_imports = list(set(
    hidden_sb +
    hidden_pg +
    hidden_rt +
    hidden_st +
    hidden_rl + [
        "tkinter",
        "PIL",
        "PIL.ImageTk",
        "qrcode",
        "pandas",
        "psycopg2",
        "psycopg2.extensions",
        "openpyxl",
        "openpyxl.cell",
        "openpyxl.styles",
        "openpyxl.worksheet",
    ]
))

# --------------------------------------------------
# DADOS EXTERNOS
# --------------------------------------------------
datas = (
    datas_sb +
    datas_pg +
    datas_rt +
    datas_st +
    datas_rl + [
        (".env", "."),
        ("img", "img"),
        ("logs", "logs"),
    ]
)

# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------
a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=(
        binaries_sb +
        binaries_pg +
        binaries_rt +
        binaries_st +
        binaries_rl
    ),
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --------------------------------------------------
# EXECUTÁVEL
# --------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SistemaPagamentos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

# --------------------------------------------------
# COLETA FINAL
# --------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="SistemaPagamentos",
)
