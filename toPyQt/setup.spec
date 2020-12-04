# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['PyQt.py'],
             pathex=['C:\Users\hckim\Desktop\ArticleAnalysis',
             'C:\Users\hckim\Desktop\ArticleAnalysis\JPype1-1.2.0-cp38-cp38-win_amd64.whl'],
             binaries=[],
             datas=[('C:\Users\hckim\Desktop\ArticleAnalysis\result', 'result')
                    ],
             hiddenimports=[
                            'sys',
                            'webbrowser',
                            'requests',
                            'PyQt5',
                            'bs4',
                            'nltk',
                            're',
                            'collections',
                            'tensorflow',
                            'konlpy',
                            'requests',
                            'pandas',
                            'datetime',
                            'os',
                            'json',
                            'csv',
                            'random',
                            'logging',
                            'tqdm',
                            'matplotlib',
                            'wordcloud',
                            'networkx',
                            'mlxtend',
                            'uuid',
                            'scholarly'
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ArticleAnalysis.exe',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True
          )
