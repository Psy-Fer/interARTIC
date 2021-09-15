# Installation from Source

[TOC]

This page has the instructions to build interARTIC from the source, which is tedious. If your system is a common Linux distribution (including Windows Subsystem for Linux) or even macOS, follow the steps [here](https://github.com/Psy-Fer/interARTIC#quick-start) to easily install interARTIC using pre-compiled binaries.

## Dependencies

* Python 3.7 or above
* Celery v4.4.6 (cliffs)
* Redis Server v6.0.5
* Artic 1.2.1 (Miniconda required for Artic installation)

## Opening terminal

Your operating system's command line will be used to install the dependencies and start interARTIC.

* For Mac OS: Type “terminal” into your spotlight search, then hit Return.
* For Windows: Type “Ubuntu” into your search bar in the Start menu, then hit Enter (you need to have an Ubuntu distribution installed via Windows Subsystem for Linux. See [here](https://linuxhint.com/install_ubuntu_windows_10_wsl/) for steps.
* For Linux: Enter the keyboard shortcut: `Ctrl`+`Alt`+`T`.

If these instructions don't work on your operating system, google how to open command line on your operating system and software version.

## Installing Python and pip

In order to use interARTIC, you’ll need Python and its package manager pip installed on your system. Python and associated libraries have limited compatibility across different versions and thus we recommend using a Python 3.7 virtual environment.

### Linux users (distributions supporting apt)

If you are a Linux user using a distribution that supports `apt`, you may follow the commands below to install Python 3.7:
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.7 python3.7-dev python3.7-venv
```
Now create a Python virtual environment called interARTIC-venv, activate it and upgrade pip:

```
python3.7 -m venv interARTIC-venv
source interARTIC-venv/bin/activate
pip install --upgrade pip
```


### Other operating system users

Check if Python and Pip are already installed by entering the following into your command prompt:

```
python --version	# or this can be python3 --version
pip --version		# or this can be pip3 --version
```

If Python is not installed, follow [this link](https://www.python.org/downloads/) and follow the instructions there.

* This application uses `Python3` as the default, not `Python2`.

If you have just installed Python, it will likely have also installed pip. Check that it is installed.

```
pip --version
```

If pip is not installed, follow [this link](https://pip.pypa.io/en/stable/installing/) and follow the prompts there.

Now create a Python virtual environment called interARTIC-venv, activate it and upgrade pip:

```
python -m venv interARTIC-venv
source interARTIC-venv/bin/activate
pip install --upgrade pip
```

## Installing Python packages for Redis, Celery and Flask

To install the Python packages for Redis, Celery, Flask and Pandas enter the following into your command prompt (make sure you have activated the interARTIC-venv virtual environment created above):

```
pip install celery==4.4.6 redis==3.5.3 flask==1.1.2 pandas==1.2.4
```

## Installing the ARTIC pipeline environment

The ARTIC pipeline has to be installed via conda.

If you do not have conda installed, we suggest installing miniconda.
The miniconda installation guide can be found [here](https://docs.conda.io/en/latest/miniconda.html)
We suggest you follow the 'Regular Installation' process.

After installing conda, enter the following into your command prompt to install ARTIC:

```
git clone https://github.com/artic-network/artic-ncov2019.git
cd artic-ncov2019 && git checkout 7e359dae37d894b40ae7e35c3582f14244ef4d36
conda env remove -n artic-ncov2019
conda env create -f environment.yml
```

Conda will download half of the Internet (pun intended!) so wait patiently.
After installation completes, run the following command and verify artic is installed.

```
conda activate artic-ncov2019
artic --version
conda deactivate
```


### Trouble installing Artic?

Follow [this link](https://artic.readthedocs.io/en/latest/installation/) to access the documentation for installing Artic.


## Installing interARTIC

Clone the repository from github by entering the following commands into your terminal.

```
git clone git@github.com:Psy-Fer/interARTIC.git
cd interARTIC
```

## Installing the Redis Server

To locally build the redis server and do a test launch, enter the following into your command prompt in your interARTIC base folder:

```
./run-redis.sh 7777
```

Exit the redis server by pressing ctrl+c now. Now close the terminal.

Alternatively, you can follow [this link](https://redis.io/topics/quickstart) to install the Redis Server manually.


## Launching interARTIC

Now launch a new terminal and activate the interARTIC-venv virtual environment we created above by calling `source interARTIC-venv/bin/activate`.  interARTIC can be launched by running the provided `run-dev.sh` script (see Automatic launch below). If something goes wrong, follow the steps under Manual launch below.

### Automatic launch

To start interARTIC, navigate to the directory where the interARTIC repository was cloned and enter the following command into your command prompt:

```
./run-dev.sh
```

### Manual launch

1. Take a new terminal, and run redis on port 7777.

```
cd interARTIC
./run-redis.sh 7777
```
2. Take another new terminal, activate the interARTIC-venv virtual environment we created above and run interARTIC main script.

```
source interARTIC-venv/bin/activate
cd interARTIC
python3 main.py 7777
```

3. Take another new terminal, activate the interARTIC-venv virtual environment followed by the ARTIC conda environment and run celery.

```
source interARTIC-venv/bin/activate
cd interARTIC
conda activate artic-ncov2019; celery worker -A main.celery -b redis://localhost:7777/0 --result-backend redis://localhost:7777/0 --concurrency=1 --loglevel=info
```


### Job Concurrency

By default, job concurrency is turned off and the automatic and manual launches will allow one job to be run at a time.

If you wish to **turn concurrency on** and run multiple jobs at a time, then please follow the steps under Manual launch above except that now you should not pass `--concurrency=1` to celery. Alternatively you can increase concurrency to the desired upper limit of concurrent jobs you would like. eg, `--concurrency=4` for 4 jobs

## Launching interARTIC web interface

Navigate to your browser and follow [this link](http://127.0.0.1:5000) to access interARTIC.


# Installation using Docker

```
git clone https://github.com/Psy-Fer/interARTIC
cd interARTIC
docker build - < Dockerfile
docker run -p 5000:5000  -v /path/to/local/data/data/:/data/ <image_id>
```


<!--
On any text editor, open ```config.init```. Update each of the configurations as necessary. All inputs should be file paths. More information about this can be found in the next section.

<!--
The default config folder is as below:

```
{
	"data-folder": "/data",
	"sample-barcode-csvs": "/data/sample-barcodes",
	"eden-primer-scheme-folder": "/data/primer_schemes_eden",
	"eden-scheme-name": "nCoV-2019/V1",
	"artic-primer-scheme-folder": "/data/primer_schemes",
	"artic-scheme-name": "nCoV-2019/V1"
}
```

* **data-folder**: This is the folder where all your data is located. By default, it is set to "/data"
* **sample-barcode-csvs**: This is the folder where your csv containing barcode names is placed.
* **eden-primer-scheme-folder**: This is the folder containing, for example, the folder nCoV-2019 which contains the V1, V2, etc folders.
* **eden-scheme-name**: This is the name of the eden primer scheme being used for your nanopore sequencing run.
* **artic-primer-scheme-folder**: This is the folder containing, for example, the folder nCoV-2019 which contains the V1, V2, etc folders.
* **artic-scheme-name**: This is the name of the artic primer scheme being used for your nanopore sequencing run.

After you update your config file, close main.py and rerun it as below:

```
CTRL + C
python3 main.py
```


####  File path input

* Folders and files should be inputted by their file paths.
* File paths can be retrieved by running 'pwd' in the appropriate folder on any terminal.
* Folders may also be referred to as directories.
* File paths should start with “/” (Mac or Linux) or “C:\” (Windows). If you have not worked with navigating folders and files in the terminal before, take a look at this [resource](https://www.earthdatascience.org/courses/intro-to-earth-data-science/python-code-fundamentals/work-with-files-directories-paths-in-python/).

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
-->
