#!/bin/bash -e

### Requirements ###
### Make sure the DOCKER_REPO env var is pointing to a valid docker repo

POSTGRES_VERSION=${POSTGRES_VERSION:-94}
POSTGRES_DOCKER_IMAGE="${DOCKER_REPO}/postgres${POSTGRES_VERSION}"

echo "Starting Postgresql"

if [[ -z $(docker images | awk "\$1~/postgres${POSTGRES_VERSION}/{print \$3}") ]]
then
    docker pull ${POSTGRES_DOCKER_IMAGE}
fi

export POSTGRES_USER=${POSTGRES_USER:-bobby}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-tables}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export POSTGRES_DATABASE_NAME=${POSTGRES_DATABASE_NAME:-my_db}
export POSTGRES_DOCKER_NAME="index-size-postgres"

export POSTGRES_DOCKER_ID=$(docker ps -q --filter "name=${POSTGRES_DOCKER_NAME}")
if [[ -z ${POSTGRES_DOCKER_ID} ]]
then
    POSTGRES_DOCKER_ID=$(docker run \
        --detach \
        --restart=unless-stopped \
        --name=${POSTGRES_DOCKER_NAME} \
        --env POSTGRES_USER \
        --env POSTGRES_PASSWORD \
        --env POSTGRES_DB=${POSTGRES_DATABASE_NAME} \
        ${POSTGRES_DOCKER_IMAGE})
fi

export POSTGRES_HOST=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' ${POSTGRES_DOCKER_NAME})
export POSTGRESQL_DB_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DATABASE_NAME}"

echo ${POSTGRESQL_DB_URL} > psql_conn.txt
