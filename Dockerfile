FROM python:3.10.3-slim-bullseye
FROM ubuntu:18.04

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*


RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install gunicorn3 -y
RUN pip3 install --upgrade pip

RUN pip3 install --upgrade pip setuptools wheel
 
RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS

COPY . /root/Attendance_system
RUN cd /root/Attendance_system && \
    pip3 install -r requirements.txt

WORKDIR /root/Attendance_system

RUN export NEURELO_API_KEY="neurelo_9wKFBp874Z5xFw6ZCfvhXdrIxbYidUfYmprDJks1tK7y+CdPciG0qgAl1exw69RQYdQYxvqcRG1GgVajqZknUzwW3VIC3xEqNyynTa2l6w7oNlrUhKRqRwBMMl8+7AZa47Yep4FXq3GDsvF4EEl8V0KoyaErzYwNp/1UgzVKPIIJ0g4CU0FZ7DttiyrVmTey_QQJSGjZU26OLFcPkkURgzkUzltgQryhI0R5NRDB76x4="


CMD [ "gunicorn3","-b","0.0.0.0:8000","application:app","--workers=5" ]