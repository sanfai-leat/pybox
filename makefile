# pybox

play: .venv
	.venv/bin/python pybox.py

.venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade -r requirements.txt

log:
	tail -f pybox.log

kill:
	pkill python

clear:
	echo > pybox.log

sync:
	rsync -azvCPL --exclude .venv . rpifour:pybox

clean:
	rm -fr pybox.log
	rm -fr id.lock

distclean: clean
	rm -fr .venv
	rm -fr __pycache__
