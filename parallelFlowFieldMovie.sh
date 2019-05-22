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

pMovieMaker() {
  Bo="${1:?'BOUSSINESQ VAL MISSING'}"
  Re="${2:?'REYNOLDS VAL MISSING'}"
  alpha="${3:?'ALPHA VAL MISSING'}"
  freq="${4:?'FORCING FREQ VAL MISSING'}"
  TU="${5:?'TIME UNITS MISSING'}"
  runs="${6:?'RUNS UNIT MISSING'}"
  field="${7:?'FIELD VAL MISSING'}"
  IMA="${8:?'IMA VAL MISSING'}"
  GMA="${9:?'GMA VAL MISSING'}"
  pertIMA="${10:?'PERT IMA VAL MISSING'}"
  pertGMA="${11:?'TIME UNITS MISSING'}"
  MODE="${12:?'MODE OPT MISSING'}"
  outPath="${13:-"movies"}"

  srcPath="src/PostProcessing/flowFieldPlot.py"
  destMachine="somss11"
  framerate=50

  ffcmd0="-hide_banner -loglevel panic -framerate ${framerate} -i"
  moviefields=($field "${field}_pert")

  if [ ${MODE} == "PROBEMODE" ]; then
    echo "PROBING:"
    restartPath="alpha${alpha}/runs_${runs}/Bo${Bo}/"
    restartName="Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_0*"
    pycmdBody=("${restartPath}${restartName}" auto)
    flags="${field} ${IMA} ${GMA} ${pertIMA} ${pertGMA}"
    echo "python ${srcPath} ${pycmdBody[@]} ${flags} ${MODE}"
    python ${srcPath} "${pycmdBody[@]}" ${flags} ${MODE}
  elif [ ${MODE} == "PLOTMODE" ] || [ ${MODE} == "MOVIEMODE" ]; then
    echo "CREATING FRAMES:"
    restartPath="alpha${alpha}/runs_${runs}/Bo${Bo}/"
    restartName="Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_0*"
    pycmdBody=("${restartPath}${restartName}" auto)
    flags="${field} ${IMA} ${GMA} ${pertIMA} ${pertGMA}"
    echo "python ${srcPath} ${pycmdBody[@]} ${flags}"
    python ${srcPath} "${pycmdBody[@]}" ${flags}
    if [ ${MODE} == "MOVIEMODE" ]; then
      echo "CREATING MOVIES:"
      for field in ${moviefields[@]}; do
        imgsPath="movies/alpha${alpha}/Bo${Bo}/Re${Re}/"
        imgsName="${field}_Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_%04d.png"
        movName="${outPath}/${field}_Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}.mp4"
        ffcmdbody=(${imgsPath}${imgsName} ${movName})
        ffmpeg $ffcmd0 ${ffcmdbody[@]}
        scpbody="${movName} ${destMachine}:/home/castillo/Documents/RESEARCH/MOVIES/"
        scp ${scpbody}
      done
    fi
  else 
    echo "MODE NOT CORRECT"
  fi
}

my_job() {
  MODE="${1:?'MODE OPT MISSING 1'}"
  Bo="${2:?'BOUSSINESQ VAL MISSING'}"
  Re="${3:?'REYNOLDS VAL MISSING'}"
  alpha="${4:?'ALPHA VAL MISSING'}"
  freq="${5:?'FORCING FREQ VAL MISSING'}"
  TU="${6:?'TIME UNITS MISSING'}"
  runs="${7:?'RUNS UNIT MISSING'}"
  field="${8:?'FIELD VAL MISSING'}"
  IMA="${9:?'IMA VAL MISSING'}"
  GMA="${10:?'GMA VAL MISSING'}"
  pertIMA="${11:?'PERT IMA VAL MISSING'}"
  pertGMA="${12:?'TIME UNITS MISSING'}"
  res_dir="${13:-"../../movies/"}"

  prefix="Re${Re}_Bo${Bo}_alpha${alpha}_f${MODE}_TU${TU}"
  out_rec="${res_dir}sweep_${prefix}.out"
  ! [[ -d "$res_dir" ]] && mkdir -p "$res_dir" || :
   
  printf "Plotting ${field} field of the solution: ${prefix}\n"
#  src/PostProcessing/pMovieMaker.sh $Bo $Re $alpha $freq $TU $runs $field $IMA $GMA $pertIMA $pertGMA $MODE
  pMovieMaker $Bo $Re $alpha $freq $TU $runs $field $IMA $GMA $pertIMA $pertGMA $MODE
  if [ "${MODE}" == "PROBEMODE" ]; then
    inawkfile="${field}_Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_bounds.dat"
    outawkfile="${field}_Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_boundstotal.dat"
    if [ -f ${inawkfile} ]; then
#      src/PostProcessing/igMAX.awk ${inawkfile} >> temp.dat
      src/PostProcessing/igMAX.awk ${inawkfile} >> $outawkfile
      rm ${inawkfile}
    fi
#    igMAX.awk ${inawkfile} >> temp.dat
    inawkfile_pert="${field}_pert_Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_bounds.dat"
    outawkfile_pert="${field}_pert_Re${Re}_Bo${Bo}_alpha${alpha}_f${freq}_TU${TU}_boundstotal.dat"
    if [ -f ${inawkfile_pert} ]; then
#     src/PostProcessing/igMAX.awk ${inawkfile_pert} >> temp.dat
      src/PostProcessing/igMAX.awk ${inawkfile_pert} >> $outawkfile_pert
      rm ${inawkfile_pert}
    fi
    echo "Creating header of bounds.dat"
    pycmd=$HOME/.local/opt/anaconda/bin/python
    $pycmd <<__EOF > bounds.dat
FILENAME = "FILENAME"
IMA      = "IMA"
IMAavg   = "IMAavg"
GMA      = "GMA"
GMAavg   = "GMAavg"
N        = "N"
print(f'# {"":=<132s} #')
print(f'#{FILENAME:^50s}{IMA:>21s}{IMAavg:>16s}{GMA:>15s}{GMAavg:>18s}{N:>8s}      #')
print(f'# {"":=<132s} #')
__EOF
    
#    if [ -f temp.dat ]; then
#    echo "Sorting:"
#    sort temp.dat | uniq >> bounds.dat
#    fi
#    igMAX.awk ${inawkfile_pert} >> temp.dat
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
