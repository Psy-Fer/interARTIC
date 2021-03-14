# InterARTIC

InterARTIC is a web application designed to ease the use of the convoluted [ARTIC pipeline](https://github.com/artic-network/artic-ncov2019). InterARTIC supports both Nanopolish and Medaka pipelines.

# Full documentation

The complete documentation can be accessed at [here](https://tthnguyen11.github.io/interARTIC/)


# Quick start

We provide binary release for common Linux distributions. Tested to work well on Ubuntu 14, 16, 18 and 20. Should work on other distributions as long as GLIBC 2.17 or higher and `/usr/bin/env` are present.

First download the latest release and run the provided script as below.

```bash
wget https://cloudstor.aarnet.edu.au/plus/s/VvslkxgQrIcTm78/download -O interartic_bin.tar.gz	
tar xf interartic_bin.tar.gz
cd interartic_bin
./run.sh
```

Now download the sample data and extract to a suitable location as below. We will put onto `/data` as the location in this example.

```bash
cd /data
wget https://cloudstor.aarnet.edu.au/plus/s/srVo6NEicclqQNE/download -O FLFL031920_sample_data.tar.gz
tar xf FLFL031920_sample_data.tar.gz
rm FLFL031920_sample_data.tar.gz
```

Now visit [http://127.0.0.1:5000](http://127.0.0.1:5000) on your browser.

TODO: Step by step tutorial (with screen shots) on how to configure paths and then do the test run.


# Building from source

Building from source is not for the faint hearted. Step by step instructions for building from source are given [here](https://tthnguyen11.github.io/interARTIC/installation/).


# interARTIC usage

See [https://tthnguyen11.github.io/interARTIC/usage/](https://tthnguyen11.github.io/interARTIC/usage/)
# Troubleshooting

See [https://tthnguyen11.github.io/interARTIC/troubleshooting/](https://tthnguyen11.github.io/interARTIC/troubleshooting/)
