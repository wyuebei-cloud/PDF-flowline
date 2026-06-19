# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.utils.hooks import collect_all

datas = [('flowline_checker', 'flowline_checker')]
datas += collect_data_files('paddleocr')
datas += collect_data_files('paddlex')
datas += collect_data_files('PyQt6')
datas += copy_metadata('python-bidi')

# paddlex checks dependency availability via importlib.metadata.version(),
# so the dist-info metadata for these packages MUST be bundled, otherwise
# its PDFReaderBackend reports pypdfium2 / opencv-contrib-python as missing
# even though the modules are physically present.
datas += copy_metadata('pypdfium2')
datas += copy_metadata('opencv-contrib-python')
datas += copy_metadata('opencv-python')
datas += copy_metadata('paddleocr')
datas += copy_metadata('paddlex')

binaries = []

# pypdfium2 ships a native pdfium DLL (in pypdfium2_raw) that the PDF backend
# loads at runtime — collect module data + binaries + hidden imports.
for pkg in ('pypdfium2', 'pypdfium2_raw'):
    _d, _b, _h = collect_all(pkg)
    datas += _d
    binaries += _b

a = Analysis(
    ['flowline_checker\\main.py'],
    pathex=['flowline_checker'],
    binaries=binaries,
    datas=datas,
    hiddenimports=['cv2', 'PIL', 'numpy', 'onnxruntime', 'bidi',
                   'pypdfium2', 'pypdfium2_raw'],
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
    name='FlowlineChecker',
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
