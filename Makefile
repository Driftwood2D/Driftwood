# Makefile for Driftwood 2D

all: bin/driftwood

run: bin/driftwood
	bin/driftwood

bin:
	mkdir -p bin

bin/driftwood: bin $(shell test -f bin/driftwood && find src/ -newer bin/driftwood)
	echo '#!/usr/bin/env python3' > bin/driftwood
	cd src && python3 -m compileall -b .
	cd src && zip -q driftwood.pyz `find . ! -name __pycache__ ! -name '*.py'`
	cat src/driftwood.pyz >> bin/driftwood
	chmod +x bin/driftwood

clean:
	rm -f bin/driftwood src/driftwood.pyz
	find . -name __pycache__ -delete -or -name \*.pyc -delete

.PHONY: run clean
