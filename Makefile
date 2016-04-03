PHONY: run migrate test clean
run: PATH  := venv/bin/:$(PATH)
run: migrate venv
	venv/bin/python fugl/manage.py runserver

migrate: venv
	venv/bin/python fugl/manage.py makemigrations
	venv/bin/python fugl/manage.py migrate

test: migrate venv
	cd fugl && ../venv/bin/python manage.py test

coverage: migrate venv
	cd fugl && ../venv/bin/coverage run --source=fugl,main --omit=\*/migrations/\*,\*/management/\*,fugl/wsgi.py manage.py test
	cd fugl && ../venv/bin/coverage html -d ../htmlcov

venv:
	virtualenv -p python3 venv
	venv/bin/pip install -r requirements.txt

wipe-cache:
	find ./ -type d -name '__pycache__' | xargs rm -rf

clean: wipe-cache
	rm -rf venv/
