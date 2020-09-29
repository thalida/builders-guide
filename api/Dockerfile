FROM python:3.7

MAINTAINER Thalida Noel "hello@thalida.com"

COPY ./ /api
WORKDIR /api

RUN pip install pipenv
RUN pipenv install --system --deploy

ENTRYPOINT ["python", "api.py"]
