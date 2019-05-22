#!/usr/bin/awk -f

NF > 0{
  if (n==0){
    ima = $2
    gma = $3
    imaAVG = $2
    gmaAVG = $3
    n=1
  }
  else {
  if ($2>ima) ima = $2
  if ($3>gma) gma = $3
  imaAVG = imaAVG+$2
  gmaAVG = gmaAVG+$3
  n++
  }
}
END{
  imaAVG=imaAVG/NR
  gmaAVG=gmaAVG/NR
  printf "%-60s\t %.8e\t %.8e\t %.8e\t %.8e\t %d\n", FILENAME, ima, imaAVG, gma, gmaAVG, NR
}

