#!/bin/bash

trap cleanup SIGINT

list_descendants ()
{
	local children=$(ps -o pid= --ppid "$1")
	for pid in ${children}
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
WEB_ADDR=127.0.0.1
WEB_PORT=5000
LOG_LOCATION=$(pwd)


usage() {
	echo "Usage: $0 [-r REDIS_PORT] [-a WEB_ADDRESS] [-p WEB_PORT] [-l LOG_PATH]" 1>&2;
	echo "optional arguments:                                                                            " 1>&2;
	echo "  -h              show this help message and exit                                              " 1>&2;
	echo "  -r REDIS_PORT                                                                                " 1>&2;
	echo "                  port to use for redis server (default: $REDIS_PORT)                          " 1>&2;
	echo "  -a WEB_ADDRESS                                                                               " 1>&2;
	echo "                  address to bind the web interface (default: $WEB_ADDR), but to run from other" 1>&2;
	echo "                  computers over the network (under VPN) can be 0.0.0.0 *WARNING*              " 1>&2;
	echo "  -p WEB_PORT                                                                                  " 1>&2;
	echo "                  port used with web address (default: $WEB_PORT)                              " 1>&2;
	echo "  -l LOG_PATH		                                                                             " 1>&2;
	echo "                  the directory path to write the logs (default: $LOG_LOCATION)	             " 1>&2;
	echo "                                                                                               " 1>&2;

	exit 1;
}

while getopts ":r:p:a:l:" o; do
    case "${o}" in
        r)
            REDIS_PORT=${OPTARG}
            ;;
        p)
            WEB_PORT=${OPTARG}
            ;;
        a)
            WEB_ADDR=${OPTARG}
            ;;
		l)	LOG_LOCATION=${OPTARG}
			;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${REDIS_PORT}" ] || [ -z "${WEB_PORT}" ] || [ -z "${WEB_ADDR}" ]; then
    usage
fi

REDIS_LOG="${LOG_LOCATION}/redis.log"
INTERARTIC_LOG="${LOG_LOCATION}/interartic.log"
CELERY_LOG="${LOG_LOCATION}/celery.log"
REALPATH=$(dirname "$(readlink -f "$0")")

ARCH=$(uname -m)
OS=$(uname -s)

if [ "${OS}" != "Linux"  ];
then
    echo "This binary package is for Linux. You O/S  is ${OS}. Trying to launch anyway - anticipating a crash!"
fi

if [[ ${ARCH} != "x86_64"  && ${ARCH} != "aarch64" ]];
then
    echo "Unsupported architecture ${ARCH}. Trying to launch anyway - anticipating a crash!"
fi

if [[ ${ARCH} = "aarch64" ]]
then
    export OPENBLAS_CORETYPE=ARMV8
fi


export PYTHONNOUSERSITE=1
unset PYTHONHOME
unset PYTHONPATH

cd "${REALPATH}"
echo "Starting redis server on port $REDIS_PORT. Log location: $REDIS_LOG"
( bin/redis-server --port ${REDIS_PORT} &> "${REDIS_LOG}" || die "Launching redis server on port $REDIS_PORT failed. See $REDIS_LOG" ) &
sleep 1
echo "Starting interartic on $WEB_ADDR:$WEB_PORT. Log location: $INTERARTIC_LOG"
( bin/python3.7 main.py ${REDIS_PORT} -a ${WEB_ADDR} -p ${WEB_PORT} &>  "${INTERARTIC_LOG}" || die "Launching interartic on $WEB_ADDR:$WEB_PORT failed. See $INTERARTIC_LOG") &
sleep 1
echo "Starting celery. Log location: $CELERY_LOG"
( export PATH="$(pwd)/artic_bin/bin:$(pwd)/scripts:${PATH}"; export LD_LIBRARY_PATH="$(pwd)/artic_bin/lib/:${LD_LIBRARY_PATH}"; bin/python3.7m bin/celery worker -A main.celery -b redis://localhost:${REDIS_PORT}/0 --result-backend redis://localhost:${REDIS_PORT}/0 --concurrency=1 --loglevel=info &> "${CELERY_LOG}" || die "Launching celery failed. See ${CELERY_LOG}" ) &
sleep 1
echo ""
echo "InterARTIC is now running on your machine :)"
echo "To launch InterARTIC web interface visit http://127.0.0.1:${WEB_PORT} on your browser"
echo "To keep your InterARTIC active this terminal must remain open."
echo "To terminate InterARTIC type CTRL-C or close the terminal."
wait
