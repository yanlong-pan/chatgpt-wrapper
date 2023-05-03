#!/bin/bash
echo "----- Please follow these steps -----"
echo '1) Run command `docker exec -it chatgpt-wrapper-container /bin/bash -c \"chatgpt\"`'
echo '2) Follow the instructions to create the first user'
echo '3) Have a nice chat'

cd migrations
alembic upgrade head
cd ..
gunicorn -c gun.py flask_app:app --chdir chatgpt_wrapper
