FROM python:3.9

ARG PIP_USERNAME
ARG PIP_PASSWORD
ARG RUN_MIGRATIONS_ON_BUILD
ARG SQLALCHEMY_DATABASE_URI

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir poetry==1.1.12
RUN poetry config virtualenvs.create false && poetry config http-basic.pilot ${PIP_USERNAME} ${PIP_PASSWORD}
RUN poetry install --no-dev --no-root --no-interaction

RUN if [ ${RUN_MIGRATIONS_ON_BUILD} == "true" ] && [ ${SQLALCHEMY_DATABASE_URI} ] ; then pip install alembic ; alembic upgrade head ; fi

RUN chmod +x gunicorn_starter.sh
CMD ["./gunicorn_starter.sh"]
