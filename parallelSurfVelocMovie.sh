#!/usr/bin/env bash
job_rec="${1:?'JOB RECORD NOT SUPPLIED'}"
MODE="${2:?'MODE OPT NOT SUPPLIED'}"
delay="${3:?'DELAY TIME NOT SUPPLIED'}"
job_com="${4:-main}"

TIMELIMIT="0-00:03"
echo "Delay = ${delay} hours"
echo "Time Limit = ${TIMELIMIT}"

#OVERHEAD_THREADS=14
OVERHEAD_THREADS=28
OVERHEAD_JOBS=14
MKL_CPUS=1

job_prefix=$(python -c "print('$job_rec'.split('/')[-1])")

sbatch_dir="log/"
sbatch_rec="${sbatch_dir}Movies_JR${job_prefix}_${job_com// /_}"

! [[ -d "$sbatch_dir" ]] && mkdir -p "$sbatch_dir" || :

trapped() {
  echo 'TRAPPED -- QUITTING'
  exit 70
}

pSurfVelocMovie() {
  MODE="${1:?'MODE OPT MISSING'}"
  Bo="${2:?'BOUSSINESQ VAL MISSING'}"
  Re="${3:?'REYNOLDS VAL MISSING'}"
  alpha="${4:?'ALPHA VAL MISSING'}"
  freq="${5:?'FORCING FREQ VAL MISSING'}"
  TU="${6:?'TIME UNITS MISSING'}"
  restartDir="${7:?'RUNS UNIT MISSING'}"
  field="${8:?'FIELD MISSING'}"
  outPath="${9:-"movies"}"

  srcPath="src/PostProcessing/surfVelocPlot.py"
  framerate=50
  pycmd="python ${srcPath} "

  ffcmd0="-hide_banner -loglevel panic -framerate ${framerate} -i"

  echo "CREATING FRAMES:"
  restartName="Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_0*"
  pycmdBody=("${restartDir}${restartName}" auto)
  echo "python ${srcPath} ${pycmdBody[@]}"
  python ${srcPath} "${pycmdBody[@]}"
  if [ ${MODE} == "MOVIEMODE" ]; then
    echo "CREATING MOVIES:"
    imgsPath="movies/alpha${alpha}/Bo${Bo}/"
    imgsName="${field}_Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_%04d.png"
    movName="${outPath}/${field}_Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}.mp4"
    ffcmdbody=(${imgsPath}${imgsName} ${movName})
    echo "ffmpeg $ffcmd0 ${ffcmdbody[@]}"
    ffmpeg $ffcmd0 ${ffcmdbody[@]}
  fi
}

my_job() {
  MODE="${1:?'MODE OPT MISSING'}"
  Re="${2:?'REYNOLDS VAL MISSING'}"
  Bo="${3:?'BOUSSINESQ VAL MISSING'}"
  dummy="${4:?'DUMMY VAL MISSING'}"
  alpha="${5:?'ALPHA VAL MISSING'}"
  freq="${6:?'FORCING FREQ VAL MISSING'}"
  dummy="${7:?'DUMMY VAL MISSING'}"
  dummy="${8:?'DUMMY VAL MISSING'}"
  restartDir="${9:?'RESTART DIR MISSING'}"
  TU="${10:?'TIME UNITS MISSING'}"
  res_dir="../../movies/"
  field="surf_v"
  
  prefix="Re${Re}_Bo${Bo}_alpha${alpha}_f${f}_TU${TU}"
  out_rec="${res_dir}sweep_${prefix}.out"
  ! [[ -d "$res_dir" ]] && mkdir -p "$res_dir" || :
   
  printf "Plotting surface ${field} of the solution: ${prefix}\n"
  pSurfVelocMovie $MODE $Bo $Re $alpha $freq $TU $restartDir $field
  echo "pSurfVelocMovie $MODE $Bo $Re $alpha $freq $TU $restartDir
  $field" > out.log
}

export -f my_job pSurfVelocMovie

trap "trapped" 1 2 3 4 5 6 7 8 

sbatch --comment="Sweep ${job_prefix} ${job_com}" << EOF
#!/bin/bash
#SBATCH -p parallel
#SBATCH -t ${TIMELIMIT}
#SBATCH --begin=now+${delay}hour
#SBATCH --nodes=1-1
#SBATCH --ntasks=1
#SBATCH --mincpus=$OVERHEAD_THREADS
#SBATCH --mail-type ALL
#SBATCH --mail-user fjcasti1@asu.edu
#SBATCH -o "${sbatch_rec}.out"
#SBATCH -e "${sbatch_rec}.err"

! [[ -d "$sbatch_dir" ]] && mkdir -p "$sbatch_dir" || :

[[ -d "../lib/" ]] && {
  export LD_LIBRARY_PATH=":$(readlink -f ../lib/):$LD_LIBRARY_PATH"
  export    LIBRARY_PATH="$LD_LIBRARY_PATH"
} || :

module load intel/2018x

export MKL_NUM_THREADS=$MKL_CPUS
ulimit -s unlimited

echo "Jobs:"
pcmd=$HOME/.local/bin/parallel
\$pcmd -v -j $OVERHEAD_JOBS --col-sep='\s+' my_job $MODE :::: $job_rec 


EOF
