#!/bin/bash -i

trap cleanup SIGINT

list_descendants ()
{
	local children=$(ps -o pid= --ppid "$1")
	for pid in $children
	do
		list_descendants "$pid"
	done
	echo "$children"
}

cleanup() {
	echo "Killing all processes."
	kill $(list_descendants $$) &> /dev/null
}

echo "Starting redis server. Log location: ./redis.log"
( bash run-redis.sh &> redis.log ) &
sleep 1
echo "Starting interartic. Log location: ./interartic.log"
( python3 main.py &> interartic.log ) &
sleep 1
echo "Starting celery. Log location: ./celery.log"
( conda activate artic-ncov2019 ; celery worker -A main.celery --concurrency=1 --loglevel=info &> celery.log ) &
sleep 1
echo "Visit http://127.0.0.1:5000 now"
echo "Press ctrl+c to terminate interartic"
wait

