#!/bin/bash -i

trap cleanup SIGINT

list_descendants ()
{
    argproc=$1
    local children=$(ps -x -o pid,ppid  | awk -v argproc=$argproc '{ if($2==argproc) {print $1} }')
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

die() {
	echo "$1" >&2
	echo
	cleanup
	exit 1
}

REDIS_PORT=7777

echo "Starting redis server. Log location: ./redis.log"
( bash run-redis.sh $REDIS_PORT &> redis.log || die "Launching redis failed. see ./redis.log" ) &
sleep 1
echo "Starting interartic. Log location: ./interartic.log"
( python3 main.py $REDIS_PORT &> interartic.log || die "Launching inteartic failed. see ./interartic.log" ) &
sleep 1
echo "Starting celery. Log location: ./celery.log"
( conda activate artic-ncov2019 ; celery worker -A main.celery -b redis://localhost:$REDIS_PORT/0 --result-backend redis://localhost:$REDIS_PORT/0 --concurrency=1 --loglevel=info &> celery.log || die "Launching celery failed. See ./celery.log" ) &
sleep 1
echo ""
echo "Visit http://127.0.0.1:5000 now"
echo "Press ctrl+c to terminate interartic"
wait
