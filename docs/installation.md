# Installation

## Dependencies

* Python 3.7 or above
* Celery v4.4.6 (cliffs)
* Redis Server v6.0.5
* Miniconda

## Opening terminal

Your operating systems command line will be used to install the dependencies. 

* For Mac OS: Typing “terminal” into your spotlight search, then hit Return.
* For Windows: Typing “cmd” into your search bar in the Start menu, then hit Enter.
* For Linux: Entering Ctrl+Alt+T

## Installing Python and pip

In order to use InterARTIC, you’ll need Python and its package manager pip installed on your system.

Check if they're already installed by entering the following into your command prompt:

```
python --version
pip --version
```

If Python is not installed, go to: https://www.python.org/downloads/ and follow the prompts there.

If you have just installed Python, it will likely have also installed pip. Check that it is installed, and upgrade if necessary.

```
pip --version
pip install --upgrade pip
```

If pip is not installed, go to: https://pip.pypa.io/en/stable/installing/ and follow the prompts there.

## Installing miniconda

The miniconda installation guide can be found here: https://conda.io/projects/conda/en/latest/user-guide/install/index.htm

We suggest you undergo the 'Regular Installation' process.

## Installing the ARTIC pipeline

Enter the following into your command prompt:

```
git clone https://github.com/artic-network/artic-ncov2019.git
cd artic-ncov2019
conda env remove -n artic-ncov2019
conda env create -f environment.yml
```

## Installing the Redis Server and Celery

To install the Redis Server (https://redis.io/topics/quickstart), enter the following into your command prompt:
```
bash run-redis.sh
```

## Installing Python packages for Redis, Celery and Flask

```
pip install celery==4.4.6 redis==3.5.3 flask 
```

## Installing InterARTIC

Clone the repository from github.

```
git clone https://github.com/tthnguyen11/SARS-CoV-2-NanoporeAnalysisWebApp.git
```

## Running InterARTIC

To start InterARTIC, navigate to the directory where the repository was cloned and enter the following command.

```
cd SARS-CoV-2-NanoporeAnalysisWebApp
bash run.sh <terminal type>
# Terminal types: macos, xterm, konsole
```

If your terminal is not listed, enter the following commands:

```
bash redis-server
conda activate artic-ncov2019; celery worker -A main.celery --loglevel=info
python3 main.py
```

Navigate to your browser and go to http://127.0.0.1:5000 to access InterARTIC.

