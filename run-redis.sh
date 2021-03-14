#!/bin/bash

die() {
	echo "$1" >&2
	echo
	exit 1
}

if [ ! -e redis-stable/src/redis-server ]; then
    rm -rf redis-stable redis-stable.tar.gz
    wget http://download.redis.io/redis-stable.tar.gz || die "Downloading failed"
    tar xf redis-stable.tar.gz || die "Extracting failed"
    rm redis-stable.tar.gz
    cd redis-stable && make || die "Building redis failed"
fi

redis-stable/src/redis-server || die "Running redis failed"
