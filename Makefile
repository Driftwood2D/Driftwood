# Makefile for Project Driftwood

all: bin/driftwood

bin:
	mkdir -p bin

bin/driftwood: bin $(shell test -d bin && find src/ -newer bin/driftwood)
	echo '#!/usr/bin/env python' > bin/driftwood
	cd src && zip -r driftwood.pyz *.py `find . -type d -mindepth 1`
	cat src/driftwood.pyz >> bin/driftwood
	rm src/driftwood.pyz
	chmod +x bin/driftwood

clean:
	rm -f bin/driftwood src/driftwood.pyz
	find src -name \*.pyc -delete

