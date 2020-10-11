# pull official base image
FROM python:3.8-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
# git
RUN apt-get install -y git
# dependencies for building Python packages
RUN apt-get install -y build-essential
# psycopg2 dependencies
RUN apt-get install -y libpq-dev
# Translations dependencies
RUN apt-get install -y gettext
# Netcat for db startup check
RUN apt-get install -y netcat
# cleaning up unused files
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --no-cache-dir --upgrade pip
COPY ./requirements ./requirements
RUN pip install --no-cache-dir -r requirements/dev.txt

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
