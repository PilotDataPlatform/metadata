FROM python:3.9

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir poetry==1.1.12
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-interaction

RUN chmod +x uvicorn_starter.sh
CMD ["./uvicorn_starter.sh"]
