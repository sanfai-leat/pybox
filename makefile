# pybox

play: .venv
	./pybox.sh

.PHONY: download
download:
	mkdir -p download
	./download.sh

.venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade -r requirements/requirements.in -c requirements/requirements.txt

log:
	tail -f pybox.log

kill:
	pkill python
	pkill bash

clear:
	echo > pybox.log

clean:
	rm -fr pybox.log
	rm -fr pybox.lock
	rm -fr pybox.tmp

distclean: clean
	rm -fr .venv
	rm -fr __pycache__
