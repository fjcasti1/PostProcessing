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
  majorticksize = 14
  minorticksize = 12

  df = pd.read_csv(DAT_DIR+DAT_FILE, sep=' ', dtype='object')
  for Bo in BoList:
    Re = ReList[BoList.index(Bo)]
    fig, axes = plt.subplots(nrows=1,ncols=2,figsize=(18,6)) # Create canvas & axes
    axes[0].set_xlabel(r'$\omega_f$',fontsize=labelsize)
    axes[0].set_ylabel(r'$\overline{E_k}$',fontsize=labelsize)
    axes[0].grid()
    axes[1].set_xlabel(r'$\omega_f$',fontsize=labelsize)
    axes[1].set_ylabel(r'$\sigma (E_k)$',fontsize=labelsize)
    axes[1].grid()
    for alpha in alphaList:
      w     = df[(df['alpha']==alpha) & (df['Bo']==Bo) & (df['Re']==Re)].astype('double').sort_values(by=['w_f'])['w_f']
      AvgEk = df[(df['alpha']==alpha) & (df['Bo']==Bo) & (df['Re']==Re)].astype('double').sort_values(by=['w_f'])['AvgEk']
      stdEk = df[(df['alpha']==alpha) & (df['Bo']==Bo) & (df['Re']==Re)].astype('double').sort_values(by=['w_f'])['stdEk']

      axes[0].plot(w,AvgEk,'-s',label=r'$\alpha$ = '+f'{alpha:s}')
      axes[1].plot(w,stdEk,'-s',label=r'$\alpha$ = '+f'{alpha:s}')

    axes[0].legend()
    axes[0].set_title(f'Bo = {Bo:s}, Re = {Re:s}')
    axes[0].ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    axes[0].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    axes[0].tick_params(axis='both',which='major', labelsize=majorticksize)
    axes[0].tick_params(axis='both',which='minor', labelsize=minorticksize)
    axes[1].legend()
    axes[1].set_title(f'Bo = {Bo:s}, Re = {Re:s}')
    axes[1].ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    axes[1].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    axes[1].tick_params(axis='both',which='major', labelsize=majorticksize)
    axes[1].tick_params(axis='both',which='minor', labelsize=minorticksize)
    savefig(f'{FIG_DIR:s}AmpVsFreq_Bo{Bo:s}.png')
    plt.close()

  return None


if __name__ == '__main__':
  main()

