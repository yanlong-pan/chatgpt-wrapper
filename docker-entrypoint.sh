#!/bin/bash

# Initialise DB
flask db upgrade

# Run server
gunicorn -c gun.py flask_app:app --chdir chatgpt_wrapper

echo 'server is UP ^_^!'