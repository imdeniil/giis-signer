# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file для GIIS DМДК XML Signer CLI
Создает standalone exe-файл со всеми зависимостями
"""

import sys
from pathlib import Path

block_cipher = None

# Определяем путь к проекту
project_root = Path.cwd()

a = Analysis(
    ['giis_signer\\cli.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Добавляем примеры XML (опционально)
        ('examples\\*.xml', 'examples'),
    ],
    hiddenimports=[
        'giis_signer',
        'giis_signer.cryptopro_signer',
        'giis_signer.xml_signer',
        'giis_signer.diagnostics',
        'xmlcanon',
        'smev_transform',
        'win32com',
        'win32com.client',
        'win32api',
        'win32con',
        'pywintypes',
        'pythoncom',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GIIS-Signer-CLI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # С консольным окном для CLI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)
