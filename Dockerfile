# FROM accetto/ubuntu-vnc-xfce-python-g3:vscode-firefox
FROM ubuntu:20.04
# export $(cat .docker.env | xargs)
ENV PYTHONPATH=/src:$PYTHONPATH

ARG TZ=Asia/Shanghai
ENV TZ=${TZ}

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

USER root

# Pkgs for default database
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    tzdata

# COPY .dockerignore .

COPY requirements.txt /tmp/requirements.txt

# RUN pip install langchain
RUN pip install -r /tmp/requirements.txt

COPY . /src
WORKDIR /src

# dev purpose, please switch to the other command and comment out pip install requirements
RUN pip install -e .
# RUN python setup.py install

