FROM accetto/ubuntu-vnc-xfce-python-g3:vscode-firefox

ENV PYTHONPATH=/src:$PYTHONPATH

RUN if [ ! -z "$DATABASE_PATH" ]; then touch "$DATABASE_PATH"; fi

USER root

# Pkgs for default database
RUN apt-get update && apt-get install -y sqlite3

# Fonts
RUN apt-get -y -qq install fonts-droid-fallback ttf-wqy-zenhei ttf-wqy-microhei fonts-arphic-ukai fonts-arphic-uming fonts-emojione

COPY .dockerignore .

COPY requirements.txt /tmp/requirements.txt

# RUN pip install langchain
RUN pip install -r /tmp/requirements.txt

COPY . /src
WORKDIR /src

# dev purpose, please switch to the other command and comment out pip install requirements
RUN pip install -e .
# RUN python setup.py install

