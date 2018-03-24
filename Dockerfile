FROM nvidia/cuda-ppc64le:9.0-cudnn7-runtime-ubuntu16.04

# Install python3 + dependencies
RUN apt update && \
    apt install -y build-essential bzip2 curl git python3-dev python3-opengl libfreetype6-dev python3-setuptools \
    mercurial python3-dev python3-setuptools python3-numpy python3-opengl libav-tools libsdl-image1.2-dev \
    libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libsdl1.2-dev libportmidi-dev libswscale-dev libavformat-dev \
    libavcodec-dev libtiff5-dev libx11-6 libx11-dev fluid-soundfont-gm timgm6mb-soundfont xfonts-base xfonts-100dpi \
    xfonts-75dpi xfonts-cyrillic fontconfig fonts-freefont-ttf && \
    rm -rf /var/lib/apt/lists/*

# Install tensorflow
RUN curl -LO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-ppc64le.sh && \
    bash Miniconda3-latest-Linux-ppc64le.sh -p /miniconda -b && \
    rm Miniconda3-latest-Linux-ppc64le.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda && \
    conda install -y tensorflow-gpu scipy

# Install CARLA agent
RUN git clone https://github.com/carla-simulator/carla.git
RUN sed -i.bak s/pygame//g carla/PythonClient/requirements.txt
RUN sed -i.bak s/rb/r/g carla/PythonClient/carla/benchmarks/metrics.py
RUN sed -i.bak 's/header_details\[\-1\]\[\:\-2\]/header_details\[\-1\]\[\:\-1\]/g' carla/PythonClient/carla/benchmarks/metrics.py
RUN python -m easy_install pip && \
    python -m pip install pygame && \
    conda install --yes --file carla/PythonClient/requirements.txt && \
    cd carla/PythonClient && git checkout tags/0.7.1 && \
    python setup.py build && python setup.py install
