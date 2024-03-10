#!/bin/bash
set -o errexit

function usage() {
  echo "usage: $0 action args..."
  exit 1
}

function gen_config() {
  source .env
  cd docker && bash gen-conf.sh $COMPOSE_PROJECT_NAME $APP_AMOUNT && cd ..
}

if [ $# -lt 1 ]; then
  usage $0
fi

action=$1
rest_args=${@:2:$#}
case $action in
  create|up)
    gen_config
    docker-compose $action $rest_args
  ;;
  flogs)
    docker-compose logs -f --tail="15" $rest_args
  ;;
  *) 
    docker-compose $action $rest_args
  ;;
esac

