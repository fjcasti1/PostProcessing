#!/usr/bin/env bash
job_rec="${1:?'JOB RECORD NOT SUPPLIED'}"
MODE="${2:?'MODE OPT NOT SUPPLIED'}"
delay="${3:?'DELAY TIME NOT SUPPLIED'}"
job_com="${4:-main}"


TIMELIMIT="0-00:23"
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

pMovieMaker() {
  MODE="${1:?'MODE OPT MISSING'}"
  Re="${2:?'REYNOLDS VAL MISSING'}"
  Bo="${3:?'BOUSSINESQ VAL MISSING'}"
  alpha="${4:?'ALPHA VAL MISSING'}"
  wf="${5:?'FORCING FREQ VAL MISSING'}"
  restartPath="${6:?'RESTART PATH MISSING'}"
  NtsT="${7:?'TIME STEPS PER PERIOD MISSING'}"
  NT="${8:?'NUMBER OF PERIODS MISSING'}"
  field="${9:?'FIELD VAL MISSING'}"
  IMA="${10:?'IMA VAL MISSING'}"
  GMA="${11:?'GMA VAL MISSING'}"
  pertIMA="${12:?'PERT IMA VAL MISSING'}"
  pertGMA="${13:?'PERT GMA VAL MISSING'}"
  outPath="${14:-"movies"}"

  srcPath="src/PostProcessing/flowFieldPlot.py"
  framerate=50

  ffcmd0="-hide_banner -loglevel panic -framerate ${framerate} -i"
  moviefields=($field "${field}_pert")

  restartName="Re${Re}_Bo${Bo}_alpha${alpha}_wf${wf}_NtsT${NtsT}_NT${NT}_0*"
  pycmdBody=("${restartPath}${restartName}" auto)
  flags="${field} ${IMA} ${GMA} ${pertIMA} ${pertGMA}"
  if [ ${MODE} == "PROBEMODE" ]; then
    echo "PROBING:"
    echo "python ${srcPath} ${pycmdBody[@]} ${flags} ${MODE}"
    python ${srcPath} "${pycmdBody[@]}" ${flags} ${MODE}
  elif [ ${MODE} == "PLOTMODE" ] || [ ${MODE} == "MOVIEMODE" ]; then
    echo "CREATING FRAMES:"
    echo "python ${srcPath} ${pycmdBody[@]} ${flags}"
    python ${srcPath} "${pycmdBody[@]}" ${flags}
    if [ ${MODE} == "MOVIEMODE" ]; then
      echo "CREATING MOVIES:"
      for field in ${moviefields[@]}; do
        imgsPath="movies/alpha${alpha}/Bo${Bo}/"
        imgsName="${field}_Re${Re}_Bo${Bo}_alpha${alpha}_wf${wf}_NtsT${NtsT}_NT${NT}_%04d.png"
        movName="${outPath}/${field}_Re${Re}_Bo${Bo}_alpha${alpha}_wf${wf}.mp4"
        ffcmdbody=(${imgsPath}${imgsName} ${movName})
        ffmpeg $ffcmd0 ${ffcmdbody[@]}
        echo "ffmpeg $ffcmd0 ${ffcmdbody[@]}"
      done
    fi
  else 
    echo "MODE NOT CORRECT"
  fi
}

my_job() {
  MODE="${1:?'MODE OPT MISSING 1'}"
  Re="${2:?'REYNOLDS VAL MISSING'}"
  Bo="${3:?'BOUSSINESQ VAL MISSING'}"
  alpha="${4:?'ALPHA VAL MISSING'}"
  wf="${5:?'FORCING FREQ VAL MISSING'}"
  restartPath="${6:?'RESTART PATH MISSING'}"
  NtsT="${7:?'TIME STEPS PER PERIOD MISSING'}"
  NT="${8:?'NUMBER OF PERIODS MISSING'}"
  field="${9:?'FIELD VAL MISSING'}"
  IMA="${10:?'IMA VAL MISSING'}"
  GMA="${11:?'GMA VAL MISSING'}"
  pertIMA="${12:?'PERT IMA VAL MISSING'}"
  pertGMA="${13:?'PERT GMA VAL MISSING'}"
  res_dir="${14:-"../../movies/"}"

  prefix="Re${Re}_Bo${Bo}_alpha${alpha}_wf${wf}_NtsT${NtsT}_NT${NT}"
  out_rec="${res_dir}sweep_${prefix}.out"
  ! [[ -d "$res_dir" ]] && mkdir -p "$res_dir" || :
   
  printf "Plotting ${field} field of the solution: ${prefix}\n"
  pMovieMaker $MODE $Re $Bo $alpha $wf $restartPath $NtsT $NT $field $IMA $GMA $pertIMA $pertGMA 
  if [ "${MODE}" == "PROBEMODE" ]; then
    inawkfile="${field}_Re${Re}_Bo${Bo}_alpha${alpha}_wf${wf}_NtsT${NtsT}_NT${NT}_bounds.dat"
    outawkfile="${field}_Re${Re}_Bo${Bo}_alpha${alpha}_wf${wf}_NtsT${NtsT}_NT${NT}_boundstotal.dat"
    if [ -f ${inawkfile} ]; then
      src/PostProcessing/igMAX.awk -v restartPath="$restartPath" ${inawkfile} >> $outawkfile
      rm ${inawkfile}
    fi
    inawkfile_pert="${field}_pert_Re${Re}_Bo${Bo}_alpha${alpha}_wf${wf}_NtsT${NtsT}_NT${NT}_bounds.dat"
    outawkfile_pert="${field}_pert_Re${Re}_Bo${Bo}_alpha${alpha}_wf${wf}_NtsT${NtsT}_NT${NT}_boundstotal.dat"
    if [ -f ${inawkfile_pert} ]; then
      src/PostProcessing/igMAX.awk -v restartPath="$restartPath" ${inawkfile_pert} >> $outawkfile_pert
      rm ${inawkfile_pert}
    fi
  fi
}

export -f my_job pMovieMaker

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
