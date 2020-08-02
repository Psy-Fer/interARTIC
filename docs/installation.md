# Installation


## Dependencies

Dependencies:
Python 3.7 or above
Celery v4.4.6 (cliffs)
Redis Server v6.0.5
Miniconda

## Installation

### Installing the ARTIC pipeline

Enter the following into your command prompt:

```
git clone https://github.com/artic-network/artic-ncov2019.git
cd artic-ncov2019
conda env remove -n artic-ncov2019
conda env create -f environment.yml
```

### Installing Redis Server and Celery

To install the Redis Server (https://redis.io/topics/quickstart), enter the following into your command prompt:
```
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
```