# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.10.3-slim-bullseye
FROM dataocean42/face_recognition:pi

ENV APP_DIR=/root/Attendance_system
ENV VIRTUAL_ENV=/root/Attendance_system/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
    apt-get install -y nano && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# RUN apt-get -y update
# RUN apt-get install -y --fix-missing \
#     build-essential \
#     cmake \
#     gfortran \
#     git \
#     wget \
#     curl \
#     graphicsmagick \
#     libgraphicsmagick1-dev \
#     libatlas-base-dev \
#     libavcodec-dev \
#     libavformat-dev \
#     libgtk2.0-dev \
#     libjpeg-dev \
#     liblapack-dev \
#     libswscale-dev \
#     pkg-config \
#     python3-dev \
#     python3-numpy \
#     software-properties-common \
#     zip \
#     && apt-get clean && rm -rf /tmp/* /var/tmp/*

# RUN cd ~ && \
#     mkdir -p dlib && \
#     git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
#     cd  dlib/ && \
#     python3 setup.py install --yes USE_AVX_INSTRUCTIONS


# The rest of this file just runs an example script.

# If you wanted to use this Dockerfile to run your own app instead, maybe you would do this:
# COPY . /root/your_app_or_whatever
# RUN cd /root/your_app_or_whatever && \
#     pip3 install -r requirements.txt
# RUN whatever_command_you_run_to_start_your_app

WORKDIR $APP_DIR

# Copy the Flask application files
COPY . $APP_DIR

# Set up Python virtual environment
RUN python3 -m venv $VIRTUAL_ENV

RUN export NEURELO_API_KEY="neurelo_9wKFBp874Z5xFw6ZCfvhXdrIxbYidUfYmprDJks1tK7y+CdPciG0qgAl1exw69RQYdQYxvqcRG1GgVajqZknUzwW3VIC3xEqNyynTa2l6w7oNlrUhKRqRwBMMl8+7AZa47Yep4FXq3GDsvF4EEl8V0KoyaErzYwNp/1UgzVKPIIJ0g4CU0FZ7DttiyrVmTey_QQJSGjZU26OLFcPkkURgzkUzltgQryhI0R5NRDB76x4="


RUN pip install --no-cache-dir gunicorn flask

# Expose the port on which your Flask app will run
EXPOSE 8000

# Start your Flask application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]


# ENTRYPOINT [ "python3" ]

# # # CMD ["websocet_server.py" ]
# CMD ["application.py"]

# ENV FLASK_APP=application.py

# #CMD ["flask", "run", "--host=0.0.0.0"]
# CMD ["sh", "-c", "flask run --host=0.0.0.0 port=5001"]

# Add pip3 install opencv-python==4.1.2.30 if you want to run the live webcam examples

# CMD cd /root/Attendance_system && \
#     python3 application.py
