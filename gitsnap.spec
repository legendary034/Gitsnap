# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import copy_metadata, collect_all

datas_list = [
    ('gitsnap_icon.png', '.'),
    ('gitsnap_icon.ico', '.'),
]
datas_list += copy_metadata('imageio')
datas_list += copy_metadata('imageio_ffmpeg')

# Collect all mss files/submodules so PyInstaller bundles them reliably
mss_datas, mss_binaries, mss_hidden = collect_all('mss')
datas_list += mss_datas

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=mss_binaries,
    datas=datas_list,
    hiddenimports=[
        'psutil', 'pystray', 'PIL', 'pynput', 'win11toast',
        'requests', 'pyperclip', 'bs4',
        'imageio', 'imageio_ffmpeg',
        'mss', 'mss.base', 'mss.exception', 'mss.factory',
        'mss.models', 'mss.screenshot', 'mss.tools',
        'mss.windows', 'mss.windows.gdi',
    ] + mss_hidden,
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
