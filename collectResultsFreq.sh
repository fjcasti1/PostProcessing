#!/usr/bin/env bash

#rm -r -f collectedResults 
mkdir collectedResults 
mkdir tableFiles

N="$(echo runs_* | wc -w)"
let N=$N-1

for i in $(seq 0 $N)
do
  cp -r runs_0$i/* collectedResults/
  echo runs_0$i copied
done

#declare -a BoValues=("5e2" "1e2" "4e1" "2e1" "15e0" "1e1" "4e0" "2e0" \
#                                    "15e-1" "1e0" "67e-2" "5e-1" "1e-1" "1e-2")

declare -a BoValues=("1e2" "1e1")
declare -a ReValues=("10e2" "12e2" "14e2")

for i in "${BoValues[@]}"
do
  for j in "${ReValues[@]}"
  do
  cat << EOF > tableFiles/Freq_alpha1e-2_Bo${i}_Re${j}.dat
  Re Bo beta alpha St                A               wM
EOF
  cat collectedResults/Bo${i}/Re${j}/ts_Re${j}_Bo${i}_beta1e0_alpha1e-2_St?e-3*.txt >> tableFiles/Freq_alpha1e-2_Bo${i}_Re${j}.dat
  done
done

for i in "${BoValues[@]}"
do
  for j in "${ReValues[@]}"
  do
  cat collectedResults/Bo${i}/Re${j}/ts_Re${j}_Bo${i}_beta1e0_alpha1e-2_St1?e-3*.txt >> tableFiles/Freq_alpha1e-2_Bo${i}_Re${j}.dat
  done
done

for i in "${BoValues[@]}"
do
  for j in "${ReValues[@]}"
  do
  cat collectedResults/Bo${i}/Re${j}/ts_Re${j}_Bo${i}_beta1e0_alpha1e-2_St2?e-3*.txt >> tableFiles/Freq_alpha1e-2_Bo${i}_Re${j}.dat
  done
done

for i in "${BoValues[@]}"
do
  for j in "${ReValues[@]}"
  do
  cat collectedResults/Bo${i}/Re${j}/ts_Re${j}_Bo${i}_beta1e0_alpha1e-2_St3?e-3*.txt >> tableFiles/Freq_alpha1e-2_Bo${i}_Re${j}.dat
  done
done
