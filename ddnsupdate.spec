# -*- mode: python ; coding: utf-8 -*-

# Fixes for Kivy
import os
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path
path = os.path.abspath(".")

block_cipher = None

a = Analysis(
    ['ddnsupdate.pyw'],
    pathex=[path],
    binaries=[],
    datas=[('ddnsupdate.kv', '.')],
    hiddenimports=[],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['docutils'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ddnsupdate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['favicon.256x256.ico'],
)

coll = COLLECT(
    exe,
    Tree(path),
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ddnsupdate',
)
