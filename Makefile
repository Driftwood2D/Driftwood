# Makefile for Project Driftwood

all: driftwood.pyz

driftwood.pyz: $(shell find src/ -newer driftwood.pyz)
	cd src && zip -r driftwood.pyz *.py basedata/ libs/
	mv src/driftwood.pyz ./

clean:
	rm -f driftwood.pyz
	find src -name \*.pyc -delete

