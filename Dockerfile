FROM ubuntu:16.04
WORKDIR /
RUN apt-get update && apt-get install -y wget
RUN wget https://github.com/Psy-Fer/interARTIC/releases/download/v0.4.3/interartic-v0.4.3-linux-x86-64-binaries.tar.gz -O interartic_bin.tar.gz
RUN tar xf interartic_bin.tar.gz
WORKDIR /interartic_bin
CMD ./run.sh -a 0.0.0.0
