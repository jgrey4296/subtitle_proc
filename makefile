

build:
	python setup.py build

win:
	python setup.py bdist_msi

mac:
	python setup.py bdist_dmg

pyinstaller:
	pyinstaller sub_processor.py
