# InterARTIC

InterARTIC is a web application designed to ease the use of the convoluted [ARTIC pipeline](https://github.com/artic-network/artic-ncov2019). InterARTIC supports both Nanopolish and Medaka pipelines.


# Quick start

## Step 1: Installing interARTIC

We provide binary release for common Linux distributions. Tested to work well on Ubuntu 14, 16, 18 and 20. Should work on other distributions as long as GLIBC 2.17 (and basic shared libraries such as *pthreads*) or higher and `/usr/bin/env` are present.

First download the latest release and run the provided script as below.

```bash
wget https://cloudstor.aarnet.edu.au/plus/s/VvslkxgQrIcTm78/download -O interartic_bin.tar.gz
tar xf interartic_bin.tar.gz
cd interartic_bin
./run.sh
```

To launch the interARTIC web interface visit [http://127.0.0.1:5000](http://127.0.0.1:5000) on your browser. Make sure you keep the terminal open to keep interARTIC running.

## Step 2: Downloading test dataset

Now take a new terminal to download and extract the sample data by entering the commands below. This example downloads and extracts the data to `/data` assuming you have write permission to `/data`.

```bash
cd /data
wget https://cloudstor.aarnet.edu.au/plus/s/srVo6NEicclqQNE/download -O FLFL031920_sample_data.tar.gz
tar xf FLFL031920_sample_data.tar.gz
rm FLFL031920_sample_data.tar.gz
```

Once extracted, you should see two directories: *FLFL031920* containing a subset of data generated from a sequencing run of 10 multiplexed COVID-19 samples and *sample-barcodes* containing a csv file that maps sample names to barcodes.

## Step 3: Configuring interARTIC

Configuration is only required if you downloaded the dataset to a custom location instead of `/data`.
On the interARTIC web interface, click *Edit Default Input Folder* and the first two fields (1. location of your input data and 2.where your sample barcode csvs are located). Click `confirm` to save the settings.

## Step 4: Running InterARTIC on test dataset

CLick `Add Job` on the interARTIC web interface. Then fill the following fields.

| field  | value  | description  |
|---|---|---|
| **Job name**                  | *test*    | whatever name that you like  |
| **Select a pipeline to run**  | *Both*   |   |
| **Select an input folder**    | *FLFL031920*  | this is the directory containing the nanopore data (should contain fast5_pass and fastq_pass directories inside)  |
| **Select a CSV file**         | *sample-barcode.csv*  | sample names to barcode mapping  |
| **Select a primer type**      | *Eden V1 (2500bp)*    | the test dataset is based on Eden V1 primers |
| **Select a barcode type**     | *Native*              | the test dataset used native barcodes |
| **This input contains**       | *Multiple samples*    | the test dataset contains multiple samples |

Now click *Submit job(s)* and you should see the pipeline running.

TODO: some screen shots

# interARTIC usage

For detailed information on using interARTIC visit [here](https://tthnguyen11.github.io/interARTIC/usage/)

# Troubleshooting

See [here](https://tthnguyen11.github.io/interARTIC/troubleshooting/) for troubleshooting common issues.


# Building from source

Building from source is not the easiest to do due to the dependency hell of Python versions. Step by step instructions for building from source are given [here](https://tthnguyen11.github.io/interARTIC/installation/).


# Acknowledgement

Binaries contain:
1. [Python 3.7 binaries](https://github.com/indygreg/python-build-standalone) (build: [cpython-3.7.7-linux64-20200409T0045](https://github.com/indygreg/python-build-standalone/releases/download/20200408/cpython-3.7.7-linux64-20200409T0045.tar.zst))
2. Python 3.7 modules: [celery](https://pypi.org/project/celery/), [redis](https://pypi.org/project/redis/), [flask](https://pypi.org/project/Flask/), [redis-server](https://pypi.org/project/redis-server/)
3. [ARTIC pipeline](https://github.com/artic-network/artic-ncov2019) that includes its dependencies: python 3.6, associated modules and dependencies



