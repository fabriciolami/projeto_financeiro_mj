# -*- mode: python ; coding: utf-8 -*-
import ast
import base64
import json
from pathlib import Path

# Inclui somente a configuração pública necessária nas outras máquinas.
config_path = Path('config/local_config.py')
if not config_path.exists():
    config_path = Path('config/local.config.py')
if not config_path.exists():
    raise RuntimeError('Configure o Supabase local antes de gerar o executável.')
config_values = {}
for node in ast.parse(config_path.read_text(encoding='utf-8-sig')).body:
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
        for target in node.targets:
            if isinstance(target, ast.Name):
                config_values[target.id] = node.value.value
key = config_values.get('SUPABASE_KEY', '')
public_key = key.startswith('sb_publishable_')
if not public_key and key.count('.') == 2:
    encoded = key.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)))
    public_key = claims.get('role') == 'anon'
if not public_key or not config_values.get('SUPABASE_URL'):
    raise RuntimeError('O aplicativo distribuído exige URL e chave pública do Supabase.')
public_config = Path('build/public_config/local.config.py')
public_config.parent.mkdir(parents=True, exist_ok=True)
public_config.write_text(
    'SUPABASE_URL = ' + repr(config_values['SUPABASE_URL']) + '\n'
    + 'SUPABASE_KEY = ' + repr(key) + '\n', encoding='utf-8')


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        (str(public_config), 'config'),
        ('img', 'img'),
    ],
    hiddenimports=['openpyxl'],
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
