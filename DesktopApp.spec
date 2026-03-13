# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas = []
binaries = []
hiddenimports = []

# TensorFlow
tf_datas, tf_binaries, tf_hiddenimports = collect_all("tensorflow")
datas += tf_datas
binaries += tf_binaries
hiddenimports += tf_hiddenimports

# matplotlib
mpl_datas, mpl_binaries, mpl_hiddenimports = collect_all("matplotlib")
datas += mpl_datas
binaries += mpl_binaries
hiddenimports += mpl_hiddenimports

# seaborn
sns_datas, sns_binaries, sns_hiddenimports = collect_all("seaborn")
datas += sns_datas
binaries += sns_binaries
hiddenimports += sns_hiddenimports

# openpyxl
oxl_datas, oxl_binaries, oxl_hiddenimports = collect_all("openpyxl")
datas += oxl_datas
binaries += oxl_binaries
hiddenimports += oxl_hiddenimports

hiddenimports += [
    "cv2",
    "PyQt5.sip",
    "matplotlib.backends.backend_qt5agg",
]

datas += [
    ("assets", "assets"),
    ("database", "database"),
    ("model", "model"),
    ("style", "style"),
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "keras.src.backend.torch",
        "torch",
        "jax",
        "jaxlib",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DesktopApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="DesktopApp",
)