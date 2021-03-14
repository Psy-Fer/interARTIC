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

die() {
	echo "$1" >&2
	echo
	cleanup
	exit 1
}

echo "Starting redis server. Log location: ./redis.log"
( bin/redis-server &> redis.log || die "Launching redis server failed. See redis.log" ) &
sleep 1
echo "Starting interartic. Log location: ./interartic.log"
( bin/python3.7 main.py &>  interartic.log || die "Launching interartic failed. See interartic.log") &
sleep 1
echo "Starting celery. Log location: ./celery.log"
( export PATH=`pwd`/artic_bin/bin:$PATH; export LD_LIBRARY_PATH=`pwd`/artic_bin/lib/:$LD_LIBRARY_PATH; bin/python3.7m bin/celery worker -A main.celery --concurrency=1 --loglevel=info &> celery.log || die "Launching celery failed. See celery.log" ) &
sleep 1
echo "Visit http://127.0.0.1:5000 now"
echo "Press ctrl+c to terminate interartic"
wait
