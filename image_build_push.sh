#!/bin/zsh

if [ -z "$1" ]
  then
    cho "expect a tag to be provided, in the form of 'v0.0.1'"
fi

docker build -t richardwzp/sandman:"$1" .
docker tag richardwzp/sandman richardwzp/sandman:"$1"
docker push richardwzp/sandman:"$1"

