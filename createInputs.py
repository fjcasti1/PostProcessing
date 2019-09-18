#!/usr/bin/env python
import sys, os, fileinput
import numpy as np
import pandas as pd
from itertools import islice
from monitor import findIndex


def parse_token(bn,token):
  return bn.split(token)[1].split('_')[0]

def returnIndex(df,Re,Bo,alpha,wf,field):
  index = df.loc[(df['Re']==Re) & (df['Bo']==Bo) & (df['alpha']==alpha) &
         (df['w_f']==wf) & (df['field']==field)].index.values[0]
  return index

def MovieListProbe(inputFile,dataFile,path):
  datadf = pd.read_csv(dataFile,sep=' ',dtype=object) 
  df = pd.DataFrame(columns=['Re','Bo','alpha','w_f','restartPath','TU',
    'field','IMA','GMA','pertIMA','pertGMA'])
  fields = ['g','s','x']
  for line in fileinput.FileInput(inputFile,inplace=1):
      linelist    = line.split()
      Re          = linelist[0]
      Bo          = linelist[1]
      alpha       = linelist[3]
      wf          = linelist[4]
      restartPath = linelist[7] # Output, where to place the restarts, not read
      wFFT        = float(datadf.iloc[findIndex(datadf,Bo,Re,alpha,wf)]['w*'])
      TU = str(int(round(4*np.pi/wFFT,6)*1e6))+'e-6'
      line = line.replace(' TU ',' '+TU+' ').strip('\n')
      print(line)
      for field in fields:
        df = df.append({'Re':Re, 'Bo':Bo, 'alpha':alpha, 'w_f':wf,
          'restartPath':restartPath, 'TU':TU, 'field':field,
          'IMA':'0', 'GMA':'1', 'pertIMA':'2', 'pertGMA':'3'},
           ignore_index=True)

  filename = 'MOVIEPROBE_MASTER'
  with open(path+filename,'w') as outfile:
    df.to_csv(outfile,header=False,index=False,sep=' ')
    outfile.close()
  return None

def MovieListBounds(inputFile,path):
  df = pd.DataFrame(columns=['Re','Bo','alpha','w_f','restartPath','TU','field','IMA','GMA','pertIMA','pertGMA'])
  
  with open(inputFile,"r") as file:
    for line in islice(file,3, None): # loops through lines starting at 4th one
      linelist = line.split()
      Bo    = parse_token(linelist[0],'Bo')
      Re    = parse_token(linelist[0],'Re')
      alpha = parse_token(linelist[0],'alpha')
      wf    = parse_token(linelist[0],'w')
      TU    = parse_token(linelist[0],'TU')
      field = linelist[0].split('_')[0]
      
      if 'pert' in linelist[0]:
        df = df.append({'Re':Re, 'Bo':Bo, 'alpha':alpha, 'w_f':wf,
          'restartPath':linelist[1], 'TU':TU, 'field':field,
          'pertIMA':linelist[2], 'pertGMA':linelist[4]},
          ignore_index=True)

      if 'pert' not in linelist[0]:
        index = returnIndex(df,Re,Bo,alpha,wf,field)
        df.iloc[index]['IMA'] = linelist[2]
        df.iloc[index]['GMA'] = linelist[4]

    file.close()
  
  df = df.sort_values(by=['Bo','Re'])
  print(df) 
  filename = 'MOVIELIST_MASTER'
  with open(os.path.join(path+'/', filename),'w') as outfile:
    df.to_csv(outfile,header=False,index=False,sep=' ')
    outfile.close()
  return None

def replaceRS(inputFile,dataFile):
  datadf = pd.read_csv(dataFile,sep=' ',dtype=object) 
  for line in fileinput.FileInput(inputFile,inplace=1):
      linelist    = line.split()
      Re          = linelist[0]
      Bo          = linelist[1]
      alpha       = linelist[2]
      wf          = linelist[3]
      (runs, TU)  = tuple(datadf[['runs_#','TU']].iloc[findIndex(datadf,
          Bo,Re,alpha,wf)].values[0])
      RSpath   = f'alpha{alpha:s}/runs_{runs:s}/Bo{Bo:s}/' 
      RSfile   = f'Re{Re:s}_Bo{Bo:s}_alpha{alpha:s}_w{wf:s}_TU{TU:s}_0010' 
      line     = line.replace('RS',RSpath+RSfile).strip('\n')
      print(line)
  return None

#def replaceRS(inputFile,dataFile):
#  datadf = pd.read_csv(dataFile,sep=' ',dtype=object) 
#  for line in fileinput.FileInput(inputFile,inplace=1):
#      linelist    = line.split()
#      Re          = linelist[0]
#      Bo          = linelist[1]
#      alpha       = linelist[2]
#      wf          = linelist[3]
#      (runs, TU)  = tuple(datadf[['runs_#','TU']].iloc[findIndex(datadf,
#          Bo,Re,alpha,wf)].values[0])
#      RSpath   = f'alpha{alpha:s}/runs_{runs:s}/Bo{Bo:s}/' 
#      RSfile   = f'Re{Re:s}_Bo{Bo:s}_alpha{alpha:s}_w{wf:s}_TU{TU:s}_0010' 
#      line     = line.replace('RS',RSpath+RSfile).strip('\n')
#      print(line)
#  return None


if __name__ == '__main__':
  MODE      = sys.argv[1]
  if MODE == 'PROBEMODE':
    INPUTFILE = sys.argv[2]
    DATAFILE  = sys.argv[3]
    DIRNAME   = sys.argv[4]
    print(f'Input File: {INPUTFILE:s}')
    print(f'Data File: {DATAFILE:s}')
    print(f'Output Directory: {DIRNAME:s}')
    print(f'MODE: {MODE:s}')
    MovieListProbe(INPUTFILE,DATAFILE,DIRNAME)
  elif MODE == 'MOVIEMODE':
    INPUTFILE = sys.argv[2]
    DIRNAME   = os.path.dirname(INPUTFILE)
    print(f'Input File: {INPUTFILE:s}')
    print(f'Output Directory: {DIRNAME:s}')
    print(f'MODE: {MODE:s}')
    MovieListBounds(INPUTFILE,DIRNAME)
  elif MODE == 'ADDRS':
    INPUTFILE = sys.argv[2]
    DATAFILE  = sys.argv[3]
    print(f'Input File: {INPUTFILE:s}')
    print(f'Data File: {DATAFILE:s}')
    print(f'MODE: {MODE:s}')
    replaceRS(INPUTFILE,DATAFILE)
  else:
    print(f'Incorrect MODE: {MODE:s}')
    exit(1)



