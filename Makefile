PHONY: run migrate test clean
run: migrate venv
	venv/bin/python corvid/manage.py runserver

migrate: venv
	venv/bin/python corvid/manage.py migrate

test: migrate venv
	cd corvid && ../venv/bin/python manage.py test

venv:
	virtualenv -p python3 venv
	venv/bin/pip install -r requirements.txt

clean:
	rm -rf venv/
	find ./ -type d -name '__pycache__' | xargs rm -rf
