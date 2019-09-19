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

outFile="bounds.dat"
path="$(dirname $inputFiles)"
srcFile=src/PostProcessing/parallelFlowFieldMovie.sh

probeMode() {
  if [[ $inputFiles == *00 ]]; then
    echo "Creating header of $outFile"
    pycmd=$HOME/.local/opt/anaconda/bin/python
    $pycmd <<__EOF > $outFile
FILENAME    = "FILENAME"
RESTARTPATH = "RESTARTPATH"
IMA         = "IMA"
IMAavg      = "IMAavg"
GMA         = "GMA"
GMAavg      = "GMAavg"
N           = "N"
print(f'# {"":=<161s} #')
print(f'#{FILENAME:^50s}{RESTARTPATH:>33s}{IMA:>20s}{IMAavg:>16s}{GMA:>15s}{GMAavg:>18s}{N:>8s}   #')
print(f'# {"":=<161s} #')
__EOF
  fi

  parallel bash ${srcFile} {} ${MODE} '0' 'MovieGen' ::: ${inputFiles} 
  
  if [[ $inputFiles != *00 ]]; then
    exit 0
  fi
  
  while [[ $(squeue -u fjcasti1 | wc -l) -gt "2" ]]
  do
    sleep 5s  
  done
  echo " "
  echo "Sorting and deleting temporary files"
  for filename in *boundstotal.dat; do
    cat $filename >> temp.dat
    rm $filename
  done
  sort temp.dat >> $outFile
  rm temp.dat

  L=$(wc -l < $outFile)
  N=$(( ($L-3)/6  ))
  echo " "
  echo "The file $outFile has $L lines"
  echo "That should represent $N different cases"
  echo "Moving $outFile to $path/"
  mv $outFile "$path/"
  echo "FINISHED IN $MODE"
}

export -f probeMode

if [ $MODE == "PROBEMODE" ]; then
  probeMode
else
  parallel bash ${srcFile} {} ${MODE} '0' 'MovieGen' ::: ${inputFiles} 
  echo "JOBS SUBMITTED IN $MODE"
fi
