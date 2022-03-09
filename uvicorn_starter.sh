#!/bin/sh

set -e

if [ $RUN_MIGRATIONS_ON_BUILD == "true" ] && [ $SQLALCHEMY_DATABASE_URI ]
then
    pip install alembic
    alembic upgrade head
fi

uvicorn app.main:app --host 0.0.0.0 --port 5066
