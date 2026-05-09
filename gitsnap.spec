# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import copy_metadata

datas_list = [
    ('gitsnap_icon.png', '.'),
    ('gitsnap_icon.ico', '.'),
]
datas_list += copy_metadata('imageio')
datas_list += copy_metadata('imageio_ffmpeg')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas_list,
    hiddenimports=['psutil', 'pystray', 'PIL', 'pynput', 'win11toast', 'requests', 'pyperclip', 'bs4', 'mss', 'imageio', 'imageio_ffmpeg'],
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
    name='gitsnap',
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
    icon='gitsnap_icon.ico',
)
