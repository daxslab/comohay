# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev git

# install cryptography dependencies
RUN apk add --no-cache \
        libressl-dev musl-dev libffi-dev

# install libsass dependencies
RUN apk add --no-cache \
        g++

# install pillow dependencies
RUN apk add --no-cache \
        jpeg-dev zlib-dev libjpeg

# install gettext
RUN apk add --no-cache gettext

# install scrapy dependencies
RUN apk add --no-cache gcc libxml2-dev libxslt-dev libxml2 libxslt musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements/dev.txt

# remove unneeded cryptography dependencies
RUN apk del \
        libressl-dev musl-dev libffi-dev

## copy entrypoint.sh
#COPY ./entrypoint.sh .
#
## copy project
#COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
