#!/usr/bin/env bash

OUT_DIR="collectedResults"
PARMAP_DIR="./"
#PARMAP_DIR="ParMapFiles"

rm -r -f $OUT_DIR
#rm -r -f $PARMAP_DIR 

mkdir $OUT_DIR
#mkdir $PARMAP_DIR

N="$(echo runs_* | wc -w)"
let N=$N-1

echo "Transfering data files into a single $OUT_DIR directory"
if [ $N -le 9 ]; then
  for i in $(seq 0 $N)
  do
    cp runs_0$i/*/ts_Re* $OUT_DIR/
    echo runs_0$i copied
  done
elif [ $N -ge 10 ]; then
  for i in $(seq 0 9)
  do
    cp runs_0$i/*/ts_Re* $OUT_DIR/
    echo runs_0$i copied
  done
  for i in $(seq 10 19)
  do
    cp runs_$i/*/ts_Re* $OUT_DIR/
    echo runs_$i copied
  done
fi

echo "Creating table file for tikz plotting of the parameter map"
declare -a BoValues=("5e2" "1e2" "4e1" "2e1" "15e0" "1e1" "4e0" "2e0" \
                                    "15e-1" "1e0" "67e-2" "5e-1" "1e-1" "1e-2")


for i in "${BoValues[@]}"
do
  cat $OUT_DIR/ts_Re*Bo${i}* >> $PARMAP_DIR/UnsortedParMap_alpha0.dat
done

cat << EOF > $PARMAP_DIR/ParMap_alpha0.dat
 Bo   Re alpha f           w               AE               wME       State
EOF

rsort < $(echo $PARMAP_DIR/UnsortedParMap_alpha0.dat) >> $PARMAP_DIR/ParMap_alpha0.dat

rm $PARMAP_DIR/UnsortedParMap_alpha0.dat

echo "Python: generating bifurcation data and preliminary figures"
python ../../src/ParMapAlpha0.py $OUT_DIR/
