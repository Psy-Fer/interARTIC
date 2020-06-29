FROM continuumio/anaconda3

RUN apt-get update -y && apt-get install -y apt-utils git 
RUN conda update -n base -c defaults conda
RUN git clone https://github.com/artic-network/artic-ncov2019.git
RUN cd artic-ncov2019 && conda env remove -n artic-ncov2019 && conda env create -f environment.yml

WORKDIR /app