# Virgool clone

A clone of [virgool](https://virgool.io) blog written in django

## Installation

first rename the .env.sample to .env and fill it.

### with docker

- `docker-compose up --build` to build the images and run the project in dev mode.

### without docker

1. create a virtualenv by running `virtualenv -p python3 .venv`. if you don't have virtualenv, install it by
   pip `pip install virtualenv`
2. activate the virtualenv `source .venv/bin/activate` in Linux/Mac or `.venv\Scripts\activate` in Windows.
3. install the dependencies by running `pip install -r requirements.txt`.
4. migrate the migration files by running `python manage.py migrate`
5. run the server on localhost by running `python manage.py runserver`


##Endpoints
you can see the project endpoints in **/swagger** or **/redoc**