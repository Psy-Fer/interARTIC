# Installation

[TOC]

## Dependencies

* Python 3.7 or above
* Celery v4.4.6 (cliffs)
* Redis Server v6.0.5
* Miniconda

## Opening terminal

Your operating system's command line will be used to install the dependencies and start interARTIC. 

* For Mac OS: Type “terminal” into your spotlight search, then hit Return.
* For Windows: Type “cmd” into your search bar in the Start menu, then hit Enter.
* For Linux: Enter the keyboard shortcut: Ctrl+Alt+T.

If these instructions don't work on your operating system, google how to open command line on your operating system and software version.

## Installing Python and pip

In order to use interARTIC, you’ll need Python and its package manager pip installed on your system.

Check if they're already installed by entering the following into your command prompt:

```
python --version
pip --version
```

If Python is not installed, go to: ```https://www.python.org/downloads/``` and follow the instructions there.

If you are a Linux user, you may instead follow the commands below to install Python:
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.7 python3.7-dev
python3.7-venv
```

If you have just installed Python, it will likely have also installed pip. Check that it is installed, and upgrade if necessary using the 2nd command below.

```
pip --version
pip install --upgrade pip
```

If pip is not installed, go to: ```https://pip.pypa.io/en/stable/installing/``` and follow the prompts there.

## Installing miniconda

The miniconda installation guide can be found here: ```https://conda.io/projects/conda/en/latest/user-guide/install/index.htm```

We suggest you undergo the 'Regular Installation' process.

## Installing the ARTIC pipeline environment

Enter the following into your command prompt:

```
git clone https://github.com/artic-network/artic-ncov2019.git
cd artic-ncov2019
conda env remove -n artic-ncov2019
conda env create -f environment.yml
```

## Installing the Redis Server and Celery

Follow this link to install the Redis Server ```https://redis.io/topics/quickstart```, then enter the following into your command prompt:

```
bash run-redis.sh
```

## Installing Python packages for Redis, Celery and Flask

To install the Python packages for Redis, Celery and Flask, enter the following into your command prompt:

```
pip3 install celery==4.4.6 redis==3.5.3 flask 
```

## Installing Porechop

To install the ARTIC version of Porechop, enter the following into your command prompt:

```
conda install -c bioconda artic-porechop 
```

## Installing interARTIC

Clone the repository from github by entering the following commands into your terminal.

```
git clone https://github.com/tthnguyen11/interARTIC.git
```

## Setting Up interARTIC

#### Job Concurrency

By default, job concurrency is turned off and the automatic and manual setups will allow one job to be run at a time. 

If you wish to **turn concurrency on** and run multiple jobs at a time, then please run the commands under the Concurrency Manual setup heading, which will allow all the CPUs available on your machine to be used to run jobs. Note that running jobs concurrently will likely slow down the speed of your machine.

### Automatic setup

To start interARTIC, navigate to the directory where the repository was cloned and enter the following command into your command prompt:

```
cd interARTIC
bash run.sh <terminal type>
# Terminal types: macos, xterm, konsole
```

### Manual setup

If your terminal is not listed, enter the following commands into your command prompt:

```
cd interARTIC
bash run-redis.sh &
conda activate artic-ncov2019; celery worker -A main.celery --concurrency=1 --loglevel=info &
python3 main.py
```

### Concurrency Manual setup

If you wish to turn job concurrency on, enter the following commands into your command prompt:

```
cd interARTIC
bash run-redis.sh &
conda activate artic-ncov2019; celery worker -A main.celery --loglevel=info &
python3 main.py
```

### Configure interARTIC

On any text editor, open ```config.init```. Update each of the configurations as necessary. All inputs should be file paths. More information about this can be found in the next section.

The default config folder is as below:

```
{
	"data-folder": "/data",
	"sample-barcode-csvs": "/Users/stephanietong/sample-barcodes",
	"kirby-primer-scheme-folder": "/Users/stephanietong/primer-schemes",
	"kirby-scheme-name": "IturiEBOV/V1",
	"artic-primer-scheme-folder": "/Users/stephanietong/primer-schemes",
	"artic-scheme-name": "IturiEBOV/V2"
}
```

* **data-folder**: This is the folder where all your data is located. By default, it is set to "/data"
* **sample-barcode-csvs**: This is the folder where your csv containing barcode names is placed.
* **kirby-primer-scheme-folder**: This is the folder containing, for example, the folder nCoV-2019 which contains the V1, V2, etc folders.
* **kirby-scheme-name**: This is the name of the kirby primer scheme being used for your nanopore sequencing run.
* **artic-primer-scheme-folder**: This is the folder containing, for example, the folder nCoV-2019 which contains the V1, V2, etc folders.
* **artic-scheme-name**: This is the name of the artic primer scheme being used for your nanopore sequencing run.

####  File path input

* Folders and files should be inputted by their file paths.
* File paths can be retrieved by running 'pwd' in the appropriate folder on any terminal.
* Folders may also be referred to as directories.
* File paths should start with “/” (Mac or Linux) or “C:\” (Windows). If you have not worked with navigating folders and files in the terminal before, take a look at this resource: https://www.earthdatascience.org/courses/intro-to-earth-data-science/python-code-fundamentals/work-with-files-directories-paths-in-python/.

For example:

```
$ pwd                                    # get file path of current directory
/Users/YOURNAME
$ ls                                     # list contents of current directory
folder1     folder2     file1       documents
$ cd documents                           # change current directory to documents
$ pwd
/Users/YOURNAME/documents
$ cd outputFolder                         # change current directory to your output folder

$ pwd                                    # obtain file path you will input into interARTIC
/Users/YOURNAME/documents/outputFolder
```
Note: your input folder may not be located in documents folder. Simply navigate, using these commands, to inside your input folder and obtain the file path. 

## Running interARTIC

Navigate to your browser and go to ```http://127.0.0.1:5000``` to access interARTIC.
