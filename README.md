# InterARTIC

InterARTIC is a web application designed to ease the use of the convoluted [ARTIC pipeline](https://github.com/artic-network/artic-ncov2019). InterARTIC supports both Nanopolish and Medaka pipelines.


# Quick start

We provide binary release for common Linux distributions. Tested to work well on Ubuntu 14, 16, 18 and 20. Should work on other distributions as long as GLIBC 2.17 or higher and `/usr/bin/env` are present.

First download the latest release and run the provided script as below.

```bash
wget https://cloudstor.aarnet.edu.au/plus/s/VvslkxgQrIcTm78/download -O interartic_bin.tar.gz	
tar xf interartic_bin.tar.gz
cd interartic_bin
./run.sh
```

To launch the interARTIC web interface visit [http://127.0.0.1:5000](http://127.0.0.1:5000) on your browser. Make sure you keep the terminal open to keep interARTIC running.

Now take a new terminal to download and extract the sample data by entering the commands below. This example downloads and extracts the data to `/data` assuming you have write permission to `/data`.

```bash
cd /data
wget https://cloudstor.aarnet.edu.au/plus/s/srVo6NEicclqQNE/download -O FLFL031920_sample_data.tar.gz
tar xf FLFL031920_sample_data.tar.gz
rm FLFL031920_sample_data.tar.gz
```

TODO: Step by step tutorial (with screen shots) on how to configure paths and then do the test run.


# Building from source

Building from source is not the easiest to do due to the dependency hell of Python versions. Step by step instructions for building from source are given [here](https://tthnguyen11.github.io/interARTIC/installation/).


# interARTIC usage

See [https://tthnguyen11.github.io/interARTIC/usage/](https://tthnguyen11.github.io/interARTIC/usage/)

# Troubleshooting

See [https://tthnguyen11.github.io/interARTIC/troubleshooting/](https://tthnguyen11.github.io/interARTIC/troubleshooting/)
