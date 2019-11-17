#!/bin/bash -e

ENVIRONMENT=$1
DEBUG=$2

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

if [ "$ENVIRONMENT" == "prd" ]
then
    source $SCRIPTPATH/../environment-prd.sh
else
    source $SCRIPTPATH/../environment-dev.sh
fi

if [ "$DEBUG" == "debug" ]
then
    DEBUG_ENV="--env REMOTE_DEBUGGING=true"
fi

sls invoke local \
    --function feed \
    --docker \
    --docker-arg='--publish 5678:5678' \
    --path lambda_feed_event.json \
    --env IS_LOCAL=true $DEBUG_ENV \
    --env AWS_LAMBDA_FUNCTION_TIMEOUT=1000 \
    --env AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    --env AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    --env AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
