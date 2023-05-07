#!/bin/bash

# Initialise DB
cd migrations
alembic upgrade head
cd ..

# Run server
gunicorn -c gun.py flask_app:app --chdir chatgpt_wrapper

echo 'server is UP ^_^!'