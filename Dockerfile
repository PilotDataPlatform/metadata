FROM python:3.7-buster

ARG PIP_USERNAME
ARG PIP_PASSWORD

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir poetry==1.1.12
RUN poetry config virtualenvs.create false && poetry config http-basic.pilot ${PIP_USERNAME} ${PIP_PASSWORD}
RUN poetry install --no-dev --no-root --no-interaction

RUN chmod +x uvicorn_starter.sh
CMD ["./uvicorn_starter.sh"]
