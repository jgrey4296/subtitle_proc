

build:
	python setup.py build

win:
	python setup.py bdist_msi

mac:
	python setup.py bdist_dmg

pyinstaller:
	pyinstaller -F --collect-all tkinterdnd2 -w sub_processor.py
