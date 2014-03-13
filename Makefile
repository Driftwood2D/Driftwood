# Makefile for Driftwood 2D

all: bin/driftwood

run: bin/driftwood
	bin/driftwood

bin:
	mkdir -p bin

bin/driftwood: bin $(shell test -f bin/driftwood && find src/ -newer bin/driftwood)
	echo '#!/usr/bin/env python3' > bin/driftwood
	cd src && zip -q -r driftwood.pyz *.py `find . -mindepth 1 -type d`
	cat src/driftwood.pyz >> bin/driftwood
	rm src/driftwood.pyz
	chmod +x bin/driftwood

clean:
	rm -f bin/driftwood src/driftwood.pyz
	find . -name __pycache__ -delete -or -name \*.pyc -delete

.PHONY: run clean
