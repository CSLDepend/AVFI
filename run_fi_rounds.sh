#!/bin/bash

for ((COUNT=1;COUNT<=$1;COUNT++))

    do
	sh ./run_bencmark_on_chrome1_through_csl.sh $2 $3
	if [ ! -d "./run_results" ]; then
		mkdir ./run_results
	fi
	if [ ! -d "./run_results/run$COUNT" ]; then
		mkdir ./run_results/run$COUNT
	fi
	cp -r ./_benchmarks_results/test_uiuc_fi_2018_$3* ./run_results/run$COUNT/
    done
