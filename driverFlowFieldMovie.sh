#!/bin/bash
if [ "$1" = "--help" ] ;  then
  echo "input1 = path to input file with parameters
input2 = MODE (PROBEMODE, PLOTMODE or MOVIDE MODE)
============================================================
                      EXAMPLE OF USE:
============================================================

  --> Only one input file
----------------------------------------
 bash src/PostProcessing/driverFlowFieldMovie.sh job_recs/movieGen/z00 'MOVIEMODE' 

  --> Several input files in parallel
----------------------------------------
 parallel bash src/PostProcessing/driverFlowFieldMovie.sh {} \
'MOVIEMODE' ::: job_recs/movieGen/z*"
  exit 0
fi
inputFiles=${1:?'INPUT FILES NOT PROVIDED'}
MODE=${2:?'MODE NOT PROVIDED'}

srcFile=src/PostProcessing/parallelFlowFieldMovie.sh

parallel bash ${srcFile} {} ${MODE} '0' 'MovieGen' ::: ${inputFiles} 

if [ $MODE == "PROBEMODE" ]; then
  while [[ $(squeue -u fjcasti1 | wc -l) -gt "1" ]]
  do
    sleep 5s  
  done
  echo " "
  echo "Sorting and deleting temporary files"
  for filename in *boundstotal.dat; do
    cat $filename >> temp.dat
    rm $filename
  done
  sort temp.dat >> bounds.dat
  rm temp.dat
  echo " "
  echo "The file bounds.dat has $(wc -l < bounds.dat) lines"
  echo "FINISHED IN $MODE"
else
  echo "JOBS SUBMITTED IN $MODE"
fi
