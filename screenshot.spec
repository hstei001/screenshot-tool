# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all numpy dependencies
numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')

a = Analysis(
    ['screenshot_app.py'],
    pathex=[],
    binaries=numpy_binaries,
    datas=numpy_datas,
    hiddenimports=numpy_hiddenimports + ['numpy.core._dtype_ctypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary binary files that might trigger AV
def remove_from_list(source, patterns):
    for file in list(source):
        for pattern in patterns:
            if pattern in str(file).lower():
                source.remove(file)
                break
    return source

# List of patterns to remove
patterns_to_remove = ['_test', 'test_', '.test']
a.binaries = remove_from_list(a.binaries, patterns_to_remove)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ScreenshotTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='whacky_icon.ico',
    version='file_version_info.txt',
    uac_admin=False,
)
