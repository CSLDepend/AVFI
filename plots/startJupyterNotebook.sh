#!/bin/bash
sudo docker run -d -v /home/jcyriac/Documents/av-research/av_il_fi/plots:/home/jovyan/work -p 8888:8888 jupyter/datascience-notebook start-notebook.sh --NotebookApp.token=''

