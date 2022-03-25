#!/bin/sh

set -e

if [ $RUN_MIGRATIONS_ON_BUILD == "true" ]
then
    export SQLALCHEMY_DATABASE_URI="postgresql://$OPSDB_UTILILT_USERNAME:$OPSDB_UTILILT_PASSWORD@$OPSDB_UTILILT_HOST:$OPSDB_UTILILT_PORT/metadata"
    pip install alembic
    alembic upgrade head
fi

uvicorn app.main:app --host 0.0.0.0 --port 5066
