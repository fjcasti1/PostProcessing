#!/usr/bin/env python
import sys
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd 
from pylab import savefig

def main():

  BoList    = sys.argv[1].strip('[]').split(',')
  ReList    = sys.argv[2].strip('[]').split(',')
  alphaList = sys.argv[3].strip('[]').split(',')

  DAT_DIR = f'dat/'
  DAT_FILE = f'collectiveData.dat'
  FIG_DIR = f'figL2/'
  labelsize = 15

  df = pd.read_csv(DAT_DIR+DAT_FILE, sep=' ', dtype='object')
  for Bo in BoList:
    Re = ReList[BoList.index(Bo)]
    fig, ax = plt.subplots(nrows=1,ncols=1,figsize=(18,6)) # Create canvas & axes
    ax.set_xlabel(r'$\omega_f$',fontsize=labelsize)
    ax.set_ylabel(r'$\sigma (E_k)$',fontsize=labelsize)
    ax.grid()
    for alpha in alphaList:
      w     = df[(df['alpha']==alpha) & (df['Bo']==Bo) & (df['Re']==Re)].astype('double').sort_values(by=['w_f'])['w_f']
      stdEk = df[(df['alpha']==alpha) & (df['Bo']==Bo) & (df['Re']==Re)].astype('double').sort_values(by=['w_f'])['stdEk']

      ax.plot(w,stdEk,'-s',label=r'$\alpha$ = '+f'{alpha:s}')

    ax.legend()
    ax.set_title(f'Bo = {Bo:s}, Re = {Re:s}')
    savefig(f'{FIG_DIR:s}AmpVsFreq_Bo{Bo:s}.png')
    plt.close()

  return None


if __name__ == '__main__':
  main()

