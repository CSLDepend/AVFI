FROM nvidia/cuda-ppc64le:9.0-cudnn7-runtime-ubuntu16.04

# Install python3
RUN apt update && apt install -y build-essential bzip2 curl && \
    rm -rf /var/lib/apt/lists/*

# Install tensorflow
RUN curl -LO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-ppc64le.sh && \
    bash Miniconda3-latest-Linux-ppc64le.sh -p /miniconda -b && \
    rm Miniconda3-latest-Linux-ppc64le.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda && \
    conda install -y tensorflow-gpu

# Install CARLA agent
COPY . /av-il-fi
#RUN conda install --yes --file /av-il-fi/requirements.txt
