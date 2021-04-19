# InterARTIC

InterARTIC is an interactive web application designed to simplify the use of the [ARTIC biofinformatics pipelines](https://github.com/artic-network/artic-ncov2019) for nanopore sequencing analysis on viral genomes. InterARTIC was initally designed and tested for analysis of SARS-CoV-2, but is suitable for analysis of any virus and/or amplicon scheme, including a user's own custom amplicons. InterARTIC spports both the Nanopolish and Medaka pipeline alternatives from ARTIC, with full parameter customisation enabled through a simple graphical interface.


# Quick start

## Step 1: Installing interARTIC

We provide a pre-compiled binary release for common Linux distributions on x86_64 architecture. The binary release is tested to work well on Ubuntu 14, 16, 18 and 20 distributions (on Windows Subsystem for Linux as well). The binary release should work on other distributions as long as GLIBC 2.17 (and basic shared libraries such as *pthreads*) or higher and `/usr/bin/env` are present.

First, open a bash terminal and run the following commands to download the [latest release](https://github.com/Psy-Fer/interARTIC/releases/latest), extract the tar ball and run the provided `run.sh` script:

```bash
wget https://cloudstor.aarnet.edu.au/plus/s/OysmkiekO1tCuSU/download -O interartic_bin.tar.gz
tar xf interartic_bin.tar.gz
cd interartic_bin
./run.sh
```

**IMPORTANT: Make sure the interARTIC binaries reside at a location with no white characters and non-ASCII charcaters in directory names**

The `run.sh` script has now launched a new interactive interARTIC session. To see your session, visit [http://127.0.0.1:5000](http://127.0.0.1:5000) on your web browser. Here, you can configure and run your next job via the graphical interface. Make sure you keep the terminal open to keep your interARTIC session running.

## Step 2: Downloading test dataset

Open a new terminal to download and extract the [example test dataset](https://cloudstor.aarnet.edu.au/plus/s/srVo6NEicclqQNE/). The commands below will extract the dataset to `/data`, assuming you have write permission to `/data`.

```bash
cd /data
wget https://cloudstor.aarnet.edu.au/plus/s/srVo6NEicclqQNE/download -O FLFL031920_sample_data.tar.gz
tar xf FLFL031920_sample_data.tar.gz
rm FLFL031920_sample_data.tar.gz
```

Once extracted, you should see two directories: 
1. *FLFL031920* containing a subset of a GridION sequencing run (with live base-calling enabled) of 10 multiplexed COVID-19 samples. The *fast5* files, *fastq* files and the sequencing summary file are amongst the extracted data.
2. *sample-barcodes* containing a .csv manifest file that matches sample names to sample barcodes.

## Step 3: Configuring interARTIC

Configuration is only required if you downloaded the dataset to a custom location instead of `/data`.
In your interARTIC web interface, click *Set locations of input data*. Fill first two fields (1. location of your input data, and 2. location of your sample-barcode .csv files are located). Click `confirm` to save the settings.

## Step 4: Running InterARTIC on the test dataset

Click `Add Job` on the interARTIC web interface. Then fill the fields as given in the following table.

| field  | value  | description  |
|---|---|---|
| **Job name**                  | *test*    | whatever name that you like for the run  |
| **Select a pipeline to run**  | *Both*   | we will test both pipelines, which will run one after the other  |
| **Select an input folder**    | *FLFL031920*  | this is the directory containing the nanopore data (must contain fast5_pass and fastq_pass directories inside)  |
| **Select a CSV file**         | *sample-barcode.csv*  | .csv manifest file that matches sample names to sample barcodes  |
| **Select a primer type**      | *Eden V1 (2500bp)*    | our example test dataset used Eden V1 primers |
| **Select a barcode type**     | *Native*              | our example test dataset used native barcodes |
| **This input contains**       | *Multiple samples*    | our example test dataset contains 10 multiplexed samples |

Now click *Submit job(s)* and you should see the pipeline running :)


# interARTIC usage

For detailed information on using interARTIC visit [here](https://psy-fer.github.io/interARTIC/usage/).

# Troubleshooting

See [here](https://psy-fer.github.io/interARTIC/troubleshooting/) for troubleshooting common issues.


# Building from source

Building from source is not the easiest to do due to the dependency hell of Python versions (this was one of the motivations for developing interARTIC). Step by step instructions for building from source are given [here](https://psy-fer.github.io/interARTIC/installation/).


# Acknowledgement

interARTIC is a layer built on top of the [ARTIC pipeline](https://github.com/artic-network/artic-ncov2019). Binary releases of interARTIC contains:
1. [Python 3.7 binaries](https://github.com/indygreg/python-build-standalone) (build: [cpython-3.7.7-linux64-20200409T0045](https://github.com/indygreg/python-build-standalone/releases/download/20200408/cpython-3.7.7-linux64-20200409T0045.tar.zst)) and several Python 3.7 modules available through *pypi* (e.g., [celery](https://pypi.org/project/celery/), [redis](https://pypi.org/project/redis/), [flask](https://pypi.org/project/Flask/), [redis-server](https://pypi.org/project/redis-server/))
3. [ARTIC pipeline binaries](https://bioconda.github.io/recipes/artic/README.html) available through bioconda that includes many dependencies (e.g., Python 3.6, medaka, nanopolish)



