# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/core/*.py', 'src/core'),
        ('src/gui/*.py', 'src/gui'),
        ('src/utils/*.py', 'src/utils'),
        ('*.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'oracledb',
        'psycopg2',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'cryptography',
        'cryptography.fernet',
        'keyring',
        'keyring.backends',
        'keyring.backends.OS_X',
        'dotenv',
        'yaml',
        'colorlog',
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
    [],
    exclude_binaries=True,
    name='OracleToPgSQL',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OracleToPgSQL',
)

app = BUNDLE(
    coll,
    name='OracleToPgSQL.app',
    icon=None,
    bundle_identifier='com.oratopgsql.migration',
)
