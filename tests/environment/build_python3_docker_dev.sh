#!/usr/bin/env bash
cd ../../
if [[ $1 ]];then
    image=$1
else
    image="dockerhub.datagrand.com/nlp/u_shape_framework:python3_dev"
fi
docker build -t ${image} -f tests/environment/Dockerfile.python3 .
