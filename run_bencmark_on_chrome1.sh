#/bin/bash

mkdir -p `pwd`/output
nvidia-docker run -v `pwd`/output:/av-il-fi/_benchmark_results -ti zubin.maas/av_il_fi:ppc64le python /av-il-fi/run_CIL.py --host chrome1.csl.illinois.edu
