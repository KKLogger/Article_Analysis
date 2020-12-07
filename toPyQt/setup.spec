# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['PyQt.py'],
             pathex=['C:\\SPIDERKIM\\ArticleAnalysis',
             'C:\\Python38\\Lib\\site-packages\\PyQt5\\Qt\\bin'
             'C:\\SPIDERKIM\\ArticleAnalysis\\JPype1-1.2.0-cp38-cp38-win_amd64.whl',
	'C:\Python38\Lib\site-packages\wordcloud',
             'C:\\Users\\secho\\AppData\\Roaming\\nltk_data'],
             binaries=[],
             datas=[('C:\\SPIDERKIM\\ArticleAnalysis\\result', 'result')],
             hiddenimports=['requests',
                            'PyQt5',
                            'bs4',
                            'nltk',
                            'konlpy',
                            'pandas',
                            'csv',
                            'tqdm',
                            'matplotlib',
                            'wordcloud',
		'stopwords',
                            'networkx',
                            'mlxtend',
                            'scholarly'],
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
