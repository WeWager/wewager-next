FROM python:3.8.0-alpine
RUN apk update && apk upgrade
RUN apk add --no-cache jpeg-dev zlib-dev gcc libxslt-dev libc-dev
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev postgresql-dev

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY ./run.sh /usr/src/app/run.sh
COPY . /usr/src/app/

EXPOSE 8000 80 443

CMD sh /usr/src/app/run.sh