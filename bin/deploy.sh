#!/bin/bash

set -x

#check environment
if [ -z $ENV ]; then
  echo "Environment (\$ENV) must be set" >&2
  exit 1
fi
if [ -z $DATABASE_URL ]; then
  echo "Database connection string (\$DATABASE_URL) must be set" >&2
  exit 1
fi 

#parameters
host=$1
key=aws_my_handicapped_pet

#set up agent if we aren't already set
if [ -z $SSH_AUTH_SOCK ]; then
    export SSH_AUTH_SOCK=/tmp/ssh-agent.sock
    ssh-agent -a $SSH_AUTH_SOCK > /dev/null
fi

#make the target machine trusted
mkdir -p ~/.ssh
ssh-keygen -F $host
if [ $? != 0 ]; then
  ssh-keyscan $host >> ~/.ssh/known_hosts
fi

#copy and add ssh key
cp $key ~/.ssh/
cp $key.pub ~/.ssh/
chmod 600 ~/.ssh/$key
ssh-add ~/.ssh/$key

#make a tunnel
ssh -fN -L 23750:127.0.0.1:23750 ec2-user@$host
export DOCKER_HOST=tcp://127.0.0.1:23750

export COMPOSE_PROJECT_NAME=$ENV
docker compose -f docker-compose.yml -f docker-compose."$ENV".yml pull
docker run -i -e DATABASE_URL myhandicappedpet/webapp-flask python -m scripts.apply_migrations
docker compose -f docker-compose.yml -f docker-compose."$ENV".yml up -d --force-recreate
