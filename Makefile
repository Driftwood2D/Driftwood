# Makefile for Project Driftwood

all: driftwood.pyz

driftwood.pyz:
	cd src && zip -r driftwood.pyz *.py basedata/ filetype/
	mv src/driftwood.pyz ./

clean:
	rm -f driftwood.pyz

