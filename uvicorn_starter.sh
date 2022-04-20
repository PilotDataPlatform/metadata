#!/bin/sh

set -e

if [ $RUN_MIGRATIONS_ON_BUILD == "true" ]
then
    export SQLALCHEMY_DATABASE_URI="postgresql://$OPSDB_UTILILY_USERNAME:$OPSDB_UTILILY_PASSWORD@$OPSDB_UTILILY_HOST:$OPSDB_UTILILY_PORT/metadata"
    pip install alembic
    alembic upgrade head
fi

uvicorn app.main:app --host 0.0.0.0 --port 5066
