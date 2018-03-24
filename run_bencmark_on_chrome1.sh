#/bin/bash

nvidia-docker run -v `pwd`:/av_il_fi -t zubin.maas/av_il_fi:ppc64le python /av_il_fi/run_CIL.py --host chrome1.csl.illinois.edu -p $1
