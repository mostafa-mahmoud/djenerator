VERSION=1.1.2

docker-build:
	docker build -t djen .

docker-test: docker-build
	docker run -it djen

# change tag here and in djenerator/__init__.py
tag:
	git tag -a v${VERSION} -m "Version ${VERSION}" && git push origin v${VERSION}

rm-tag:
	git tag -d v${VERSION} && git push origin --delete v${VERSION}

clean:
	@find . -name "__pycache__" -exec rm -rfv {} +
	@find . -name "migrations" -exec rm -rfv {} +
	@find . -name "db.sqlite3" -exec rm -rfv {} +
	@rm -vfr files images build dist djenerator.egg-info media
	@find . -name "__pycache__ 2" -exec rm -rfv {} +
	@find . -name "migrations 2" -exec rm -rfv {} +
	@find . -name "db.sqlite3 2" -exec rm -rfv {} +
	@rm -vfr "files 2" "images 2"

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

coverage:
	coverage run --source "djenerator.core,testapp.models" manage.py test && coverage report

release:
	python3 setup.py sdist && twine upload dist/* --verbose
