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

sls deploy
