FROM python:3.10

COPY ./ /api
WORKDIR /api

RUN pip install pipenv
RUN pipenv install --system --deploy

ENTRYPOINT ["python", "api.py"]
