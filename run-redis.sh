#!/bin/bash

die() {
	echo "$1" >&2
	echo
	exit 1
}

if [ ! -e redis-stable/src/redis-server ]; then
    rm -rf redis-stable redis-6.0.12.tar.gz
    wget https://download.redis.io/releases/redis-6.0.12.tar.gz || die "Downloading failed"
    tar xf redis-stable.tar.gz || die "Extracting failed"
    rm redis-6.0.12.tar.gz
    cd redis-stable && make || die "Building redis failed"
fi

redis-stable/src/redis-server --port $1 || die "Running redis failed"
