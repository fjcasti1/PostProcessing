#!/bin/bash

inputFiles=${1:?'INPUT FILES NOT PROVIDED'}
MODE=${2:?'MODE NOT PROVIDED'}
srcFile=src/PostProcessing/parallelSurfVelocMovie.sh

parallel bash ${srcFile} {} ${MODE} '0' 'SurfMovieGen' ::: ${inputFiles}
