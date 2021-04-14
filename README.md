# InterARTIC

InterARTIC is a web application designed to ease the use of the convoluted [ARTIC pipeline](https://github.com/artic-network/artic-ncov2019). InterARTIC supports both Nanopolish and Medaka pipelines.


# Quick start

## Step 1: Installing interARTIC

We provide a binary release for common Linux distributions. The binary releases is tested to work well on Ubuntu 14, 16, 18 and 20 distributions (on Windows Subsystem for Linux as well). The binary release should work on other distributions as long as GLIBC 2.17 (and basic shared libraries such as *pthreads*) or higher and `/usr/bin/env` are present.

First, download the latest release and run the provided `run.sh` script:

```bash
wget https://cloudstor.aarnet.edu.au/plus/s/jtIWKun0E6SmpMj/download -O interartic_bin.tar.gz
tar xf interartic_bin.tar.gz
cd interartic_bin
./run.sh
```

To launch the interARTIC web interface, visit [http://127.0.0.1:5000](http://127.0.0.1:5000) on your browser. Make sure you keep the terminal open to keep interARTIC running.

## Step 2: Downloading test dataset

Now take a new terminal to download and extract the example test dataset. Enter the commands below that downloads and extracts the dataset to `/data`, assuming you have write permission to `/data`.

```bash
cd /data
wget https://cloudstor.aarnet.edu.au/plus/s/srVo6NEicclqQNE/download -O FLFL031920_sample_data.tar.gz
tar xf FLFL031920_sample_data.tar.gz
rm FLFL031920_sample_data.tar.gz
```

Once extracted, you should see two directories: 
1. *FLFL031920* containing a subset of a GridION sequencing run (with live base-calling enabled) of 10 multiplexed COVID-19 samples. The *fast5* files, *fastq* files and the sequencing summary file are amongst the extracted data.
2. *sample-barcodes* containing a .csv file that maps sample names to barcodes.

## Step 3: Configuring interARTIC

Configuration is only required if you downloaded the dataset to a custom location instead of `/data`.
On the interARTIC web interface, click *Edit Input and sample .csv directories*. Fill first two fields (1. location of your input data, and 2. where your sample barcode .csv files are located). Click `confirm` to save the settings.

## Step 4: Running InterARTIC on test dataset

CLick `Add Job` on the interARTIC web interface. Then fill the fields as given in the following table.

| field  | value  | description  |
|---|---|---|
| **Job name**                  | *test*    | whatever name that you like for the run  |
| **Select a pipeline to run**  | *Both*   | we will test both pipelines, which will run one after the other  |
| **Select an input folder**    | *FLFL031920*  | this is the directory containing the nanopore data (must contain fast5_pass and fastq_pass directories inside)  |
| **Select a CSV file**         | *sample-barcode.csv*  | .csv file that maps sample names to barcodes  |
| **Select a primer type**      | *Eden V1 (2500bp)*    | our example test dataset used Eden V1 primers |
| **Select a barcode type**     | *Native*              | our example test dataset  used native barcodes |
| **This input contains**       | *Multiple samples*    | our example test dataset contains 10 multiplexed samples |

Now click *Submit job(s)* and you should see the pipeline running :)


# interARTIC usage

For detailed information on using interARTIC visit [here](https://psy-fer.github.io/interARTIC/usage/).

# Troubleshooting

See [here](https://psy-fer.github.io/interARTIC/troubleshooting/) for troubleshooting common issues.


# Building from source

Building from source is not the easiest to do due to the dependency hell of Python versions. Step by step instructions for building from source are given [here](https://psy-fer.github.io/interARTIC/installation/).


# Acknowledgement

interARTIC is a layer built on top of the [ARTIC pipeline](https://github.com/artic-network/artic-ncov2019). Binary releases of interARTIC contains:
1. [Python 3.7 binaries](https://github.com/indygreg/python-build-standalone) (build: [cpython-3.7.7-linux64-20200409T0045](https://github.com/indygreg/python-build-standalone/releases/download/20200408/cpython-3.7.7-linux64-20200409T0045.tar.zst)) and several Python 3.7 modules available through *pypi* (e.g., [celery](https://pypi.org/project/celery/), [redis](https://pypi.org/project/redis/), [flask](https://pypi.org/project/Flask/), [redis-server](https://pypi.org/project/redis-server/))
3. [ARTIC pipeline binaries](https://bioconda.github.io/recipes/artic/README.html) available through bioconda that includes many dependencies (e.g., Python 3.6, medaka, nanopolish)



