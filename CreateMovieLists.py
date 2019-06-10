#!/usr/bin/env python
import sys, os
import pandas as pd
from itertools import islice



def parse_token(bn,token):
  return bn.split(token)[1].split('_')[0]

def returnIndex(df,Re,Bo,alpha,f,field):
  index = df.loc[(df['Re']==Re) & (df['Bo']==Bo) & (df['alpha']==alpha) &
         (df['f']==f) & (df['field']==field)].index.values[0]
  return index

def MovieListProbe(inputFile,path):
  df = pd.DataFrame(columns=['Re','Bo','alpha','f','restartPath','TU',
    'field','IMA','GMA','pertIMA','pertGMA'])
  with open(inputFile,"r") as file:
    for line in file:    # loops through lines starting at the 4th one
      linelist    = line.split()
      Re          = linelist[0]
      Bo          = linelist[1]
      alpha       = linelist[3]
      f           = linelist[4]
      restartPath = linelist[7]
      TU          = linelist[8]
      fields = ['g','s','x']
      for field in fields:
        df = df.append({'Re':Re, 'Bo':Bo, 'alpha':alpha, 'f':f,
          'restartPath':restartPath, 'TU':TU, 'field':field,
          'IMA':'0', 'GMA':'1', 'pertIMA':'2', 'pertGMA':'3'},
           ignore_index=True)
  file.close()

  filename = 'movielistprobe.dat'
  with open(os.path.join(path+'/', filename),'w') as outfile:
    df.to_csv(outfile,header=False,index=False,sep=' ')
    outfile.close()
  return None

def MovieListBounds(path):
  df = pd.DataFrame(columns=['Re','Bo','alpha','f','restartPath','TU','field','IMA','GMA','pertIMA','pertGMA'])
  
  with open(os.path.join(path+'/', "bounds.dat"),"r") as file:
    for line in islice(file,3, None): # loops through lines starting at 4th one
      linelist = line.split()
      Bo    = parse_token(linelist[0],'Bo')
      Re    = parse_token(linelist[0],'Re')
      alpha = parse_token(linelist[0],'alpha')
      f     = parse_token(linelist[0],'f')
      TU    = parse_token(linelist[0],'TU')
      field = linelist[0].split('_')[0]
      
      if 'pert' in linelist[0]:
        df = df.append({'Re':Re, 'Bo':Bo, 'alpha':alpha, 'f':f,
          'restartPath':linelist[1], 'TU':TU, 'field':field,
          'pertIMA':linelist[2], 'pertGMA':linelist[4]},
          ignore_index=True)

      if 'pert' not in linelist[0]:
        index = returnIndex(df,Re,Bo,alpha,f,field)
        df.iloc[index]['IMA'] = linelist[2]
        df.iloc[index]['GMA'] = linelist[4]

    file.close()
  
  df = df.sort_values(by=['Bo','Re'])
  print(df) 
  filename = 'movielist.dat'
  with open(os.path.join(path+'/', filename),'w') as outfile:
    df.to_csv(outfile,header=False,index=False,sep=' ')
    outfile.close()
  return None


if __name__ == '__main__':
  INPUTFILE = sys.argv[1]
  MODE      = sys.argv[2]
  DIRNAME   = os.path.dirname(INPUTFILE)
  print(INPUTFILE)
  print(DIRNAME)
  if MODE == 'PROBEMODE':
    print(MODE)
    MovieListProbe(INPUTFILE,DIRNAME)
  elif MODE == 'BOUNDSMODE':
    print(MODE)
    MovieListBounds(DIRNAME)
  else:
    print(MODE)
    exit(1) 



