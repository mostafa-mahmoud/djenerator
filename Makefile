clean:
	@find . -name "__pycache__" -exec rm -rfv {} +
	@find . -name "migrations" -exec rm -rfv {} +
	@find . -name "db.sqlite3" -exec rm -rfv {} +
	@rm -vfr files images

migrations:
	python3 manage.py makemigrations testapp
	python3 manage.py migrate

test:
	python3 manage.py test

lint:
	flake8 djenerator/core testapp/models.py testapp/tests.py --import-order-style smarkets --show-source --statistics --application-import-names djenerator,testapp

all: clean migrations
	python3 manage.py jenerate testapp 50

shell:
	python3 manage.py shell
