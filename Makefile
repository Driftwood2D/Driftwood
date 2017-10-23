# Makefile for Driftwood 2D

all: bin/driftwood

run: bin/driftwood
	bin/driftwood

bin: bin/driftwood

bin/driftwood: $(shell test -f bin/driftwood && find src/ -newer bin/driftwood)
	mkdir -p bin
	echo '#!/usr/bin/env python3' > bin/driftwood
	cd src && python3 -m compileall -b .
	cd src && rm -f driftwood.pyz
	cd src && zip -q driftwood.pyz `find . ! -name __pycache__ ! -name '*.py'`
	cat src/driftwood.pyz >> bin/driftwood
	chmod +x bin/driftwood

release: release/driftwood
	mkdir -p release/db/
	cp -R data/ tools/ config.json CREDITS.md README.md LICENSE release/

release/driftwood: $(shell test -f release/driftwood && find src/ -newer release/driftwood)
	mkdir -p release
	echo '#!/usr/bin/env python3' > release/driftwood
	cd src && rm -f driftwood.pyz
	cd src && zip -q driftwood.pyz `find . ! -name __pycache__ ! -name '*.pyc'`
	cat src/driftwood.pyz >> release/driftwood
	chmod +x release/driftwood

docs: $(shell test -f docs/index.html && find docsrc/ -newer docs/index.html)
	daux --source=docsrc --destination=docs

clean:
	rm -f bin/driftwood release/driftwood src/driftwood.pyz
	rm -rf bin/
	rm -rf release/
	rm -rf docs/
	find . -name __pycache__ -delete -or -name \*.pyc -delete

.PHONY: run clean
