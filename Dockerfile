FROM python:3.8.9-slim-buster
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  gcc \
  gettext \
  libc-dev \
  libffi-dev \
  libxslt-dev \
  libxml2-dev \
  musl-dev \
  openjpeg-dev \
  openssl-dev \
  postgresql-client \
  python3-dev \
  python3-lxml \

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY ./run.sh /usr/src/app/run.sh
COPY . /usr/src/app/

EXPOSE 8000 80 443

CMD sh /usr/src/app/run.sh