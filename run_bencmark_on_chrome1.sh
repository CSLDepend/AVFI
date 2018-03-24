#/bin/bash

nvidia-docker run -v `pwd`:/av_il_fi -ti zubin.maas/av_il_fi:ppc64le python /av_il_fi/run_CIL.py --host 172.16.0.2 -p $1 -c $2
