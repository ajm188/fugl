# Fugl [![Build Status](https://travis-ci.org/ajm188/fugl.svg?branch=master)](https://travis-ci.org/ajm188/fugl) [![Coverage Status](https://coveralls.io/repos/github/ajm188/fugl/badge.svg?branch=master)](https://coveralls.io/github/ajm188/fugl?branch=master)

User-friendly static site generation as a service. Powered by [Pelican](http://blog.getpelican.com/).

# Installation

## Postgresql
- Use your package manager. Be sure to get development headers.
  + On Ubuntu, run `sudo apt-get install postgresql-9.4 postgresql-server-dev-9.4`
- The settings given in the repo are expecting a role named `fugl` that owns
  a database with the same name. To set this up, enter the Postgres REPL with
  `sudo -u postgres psql` and enter the following commands:
- When doing development, you need `CREATEDB` to run tests, but during deploy we
  will shut that off.

```sql
    CREATE ROLE fugl PASSWORD '<password>' NOSUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;
    CREATE DATABASE fugl OWNER fugl;
```

- Edit `postgresql.conf` (found on Ubuntu under `/etc/postgresql/9.4/main/postgresql.conf`),
  and uncomment the line: `listen_addresses = 'localhost'`. Now you will only be
  able to access Postgres from your machine. (Better for development, but you
  will not want this for deployment.)

## Python
### VirtualEnv
- install virtualenv
- create virtualenv under project root: `virtualenv -p python3 venv`
- activate: `. venv/bin/activate`
- (when done, deactivate with `deactivate`)

### Packages
- With virtualenv active, install required packages:
  `pip install -r requirements.txt`
- This may fail due to lack of development headers when installing native
  extensions (particularly psycopg2 and lxml).  So then you'll probably want
  `sudo apt-get install python3-dev libxml2-dev libxslt1-dev lib32z1-dev`.

# Development

- To populate the database:
  - The basics (**you must do this**) `python manage.py populate ../themes/`
  - Taylor swift user/project (good for demo) `python manage.py tswizzle`
- To launch the test server: `make run`
- To run tests: `make test`

# Themes

To get themes added to the database (you should have gotten everything prior to
this done):

```bash
git submodule init
git submodule update
# wait a little while
cd pelican-themes
git submodule init
git submodule update
# wait a lot longer
cd ../fugl
./manage.py loadthemes
```

# Deployment

To deploy a new version, the following procedure should be used:

- (as root) Stop the uWSGI application server: `service uwsgi stop fugl`.
- (as django) Go to `/home/django/fugl` and do your `git pull`.
- (still as django, in virtualenv) Make sure to do `./manage.py makemigrations`
  and `./manage.py migrate`.
- (as root, in virtualenv) Do `./manage.py collectstatic`!
- (as root) Start the uWSGI application server: `service uwsgi start fugl`.

And you should have successfully deployed a new Fugl!
