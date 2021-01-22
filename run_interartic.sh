#!/bin/bash -i

cd interARTIC
( bash run-redis.sh ) &
sleep 1
( python3 main.py ) &
sleep 1
( conda activate artic-ncov2019; celery worker -A main.celery --concurrency=1 --loglevel=info ) &
sleep 1
wait
