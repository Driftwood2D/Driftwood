# Makefile for Project Driftwood

all: driftwood.pyz

driftwood.pyz: $(shell find src/*.py src/basedata/ -newer driftwood.pyz)
	cd src && zip -r driftwood.pyz *.py basedata/
	mv src/driftwood.pyz ./

clean:
	rm -f driftwood.pyz
	rm -f src/*.pyc

