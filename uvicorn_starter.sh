#!/bin/sh

set -e

if [ $RUN_MIGRATIONS == "true" ]
then
    export SQLALCHEMY_DATABASE_URI="postgresql://$OPSDB_UTILITY_USERNAME:$OPSDB_UTILITY_PASSWORD@$OPSDB_UTILITY_HOST:$OPSDB_UTILITY_PORT/metadata"
    pip install alembic
    alembic upgrade head
fi

uvicorn app.main:app --host 0.0.0.0 --port 5066 --log-level debug
