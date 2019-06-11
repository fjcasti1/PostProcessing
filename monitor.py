#!/usr/bin/env python
import sys
from os import path, makedirs
from numpy import pi, loadtxt
from pylab import detrend,fft,savefig
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from scipy.signal import blackman as blk
import pandas as pd

## TO USE LATEX IN LABELS
#from matplotlib import rc
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
### for Palatino and other serif fonts use:
##rc('font',**{'family':'serif','serif':['Palatino']})
#rc('text', usetex=True)
#----------------------------------------------------------------#

f       = sys.argv[1]
res_dir = sys.argv[2]
dtinput = sys.argv[3]

#FIG_DIR = f'fig/{res_dir:s}'

#def fig_dir(f):
#  a = f.split('/')[0]
#  b = f.split('/')[2]
#  s = "/"
#  return f'fig/{s.join([a,b]):s}/'
def fig_dir(f):
  #a = f.split('/')[0]
  #return f'fig/{a:s}/'
  return f'fig/'

FIG_DIR = fig_dir(res_dir)
DAT_DIR = f'dat/'

def long_basename(f):
  return f.split('/')[-1]

def ts_basename(f):
  return f.split('_TU')[0]

def fft_basename(f):
  return f.replace('ts_','fft_')

def orbit_basename(f):
  return f.replace('ts_','orbit_')

def parse_token(bn,token):
  return bn.split(token)[1].split('_')[0]

def check(df,Bo,Re,alpha,freq):
  cond = ( (df['Re']==Re) & (df['Bo']==Bo) & (df['alpha']==alpha) &
      (df['f']==freq) )
  return df.index[cond].tolist()

def addRow(df,Bo,Re,alpha,freq,w,runs):
  df = df.append({'Re':Re, 'Bo':Bo, 'alpha':alpha, 'f':freq,
    'w*':w, 'runs_#':runs}, ignore_index=True)
  return df

def replaceRow(df,Bo,Re,alpha,freq,w,runs,index):
  df.loc[index,['Bo','Re','alpha','f','w*','runs_#']]=[Bo,Re,alpha,freq,w,runs]
  return None
  
def main(f,dtinput):
  longbn  = long_basename(f)
  tsbn    = ts_basename(longbn)
  fftbn   = fft_basename(tsbn)
  orbitbn = orbit_basename(tsbn)
  tokens  = ['Re','Bo','alpha','f','TU'] 
  try:
    values = [ parse_token(longbn,token) for token in tokens ]
    Re   = values[0]
    Bo   = values[1]
    alpha= values[2]
    freq = values[3]
    TU   = int(values[4])
    runs = f.split('runs_')[-1].split('/')[0]
  except Exception as ex:
    print('Exception in parse token: ', ex)
  if TU<0:
    Nsteps = -TU
    if freq!=0:
      dt     = float(1/(freq*Nsteps))
    elif freq==0:
      dt = float(dtinput)
  else:
    dt = float(dtinput)
    Nsteps = float(TU/dt)
  w = 2*pi*float(freq)

  title_string = longbn.replace('_',' ')
  t,Ek,Eg,Ew,ur,uw,uz = loadtxt(f).T
  makedirs(FIG_DIR,exist_ok=True)

####################
# Plot time series #
####################
  P = 5 # last P% of the time series
  M = int(len(t)*P/100)
  ticksize = 12
  labelsize = 18
  labelpadx = 3
  labelpady = 10
  
  fig, axes = plt.subplots(nrows=2,ncols=3,figsize=(14,9)) # Create canvas & axes
  ## Global Kinetic Energy Time Series
  axes[0,0].plot(t[-M:],Ek[-M:],'r-')
  axes[0,0].set_xlabel('$t$',fontsize=labelsize,labelpad=labelpadx)
  axes[0,0].set_ylabel('$E_k$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[0,0].tick_params(labelsize=ticksize)
  ## Global Angular Momentum Time Series
  axes[0,1].plot(t[-M:],Ew[-M:],'r-')
  axes[0,1].set_xlabel('$t$',fontsize=labelsize,labelpad=labelpadx)
  axes[0,1].set_ylabel('$E_{\omega}$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[0,1].tick_params(labelsize=ticksize)
  ## Global Enstrophy Time Series
  axes[0,2].plot(t[-M:],Eg[-M:],'r-')
  axes[0,2].set_xlabel('$t$',fontsize=labelsize,labelpad=labelpadx)
  axes[0,2].set_ylabel('$E_{\gamma}$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[0,2].tick_params(labelsize=ticksize)
  ## Local Radial Velocity Time Series
  axes[1,0].plot(t[-M:],ur[-M:],'r-')
  axes[1,0].set_xlabel('$t$',fontsize=labelsize,labelpad=labelpadx)
  axes[1,0].set_ylabel('$u_r$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[1,0].tick_params(labelsize=ticksize)
  ## Local Azimuthal Velocity Time Series
  axes[1,1].plot(t[-M:],uw[-M:],'r-')
  axes[1,1].set_xlabel('$t$',fontsize=labelsize,labelpad=labelpadx)
  axes[1,1].set_ylabel(r'$u_{\theta}$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[1,1].tick_params(labelsize=ticksize)
  ## Local Axial Velocity Time Series
  axes[1,2].plot(t[-M:],uz[-M:],'r-')
  axes[1,2].set_xlabel('$t$',fontsize=labelsize,labelpad=labelpadx)
  axes[1,2].set_ylabel('$u_z$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[1,2].tick_params(labelsize=ticksize)
  
  fig.tight_layout()
  fig.savefig(f'{FIG_DIR:s}{tsbn:s}.png')
  plt.close()


#############
# Plot ffts #
#############
  P = 100
  M = int(len(Ek)*P/100)
  T = M*dt   # Period ??
  w0  = 2*pi/T       # Natural Frequency??
  
  AEk = Ek[-M:].std() # Amplitud of Oscillation
  fftEk  = abs(fft(detrend(Ek[-M:])*blk(M))[:M//2]) # FFT with Blackman filter [array]
  wMEk = w0*fftEk.argmax() # Compute dominant frequency
  
  AEg = Eg[-M:].std() # Amplitud of Oscillation
  fftEg  = abs(fft(detrend(Eg[-M:])*blk(M))[:M//2]) # FFT with Blackman filter [array]
  wMEg = w0*fftEg.argmax() # Compute dominant frequency
  
  AEw = Ew[-M:].std() # Amplitud of Oscillation
  fftEw  = abs(fft(detrend(Ew[-M:])*blk(M))[:M//2]) # FFT with Blackman filter [array]
  wMEw = w0*fftEw.argmax() # Compute dominant frequency
  
  Aur = ur[-M:].std() # Amplitud of Oscillation
  fftur  = abs(fft(detrend(ur[-M:])*blk(M))[:M//2]) # FFT with Blackman filter [array]
  wMur = w0*fftur.argmax() # Compute dominant frequency
  
  Auw = uw[-M:].std() # Amplitud of Oscillation
  fftuw  = abs(fft(detrend(uw[-M:])*blk(M))[:M//2]) # FFT with Blackman filter [array]
  wMuw = w0*fftuw.argmax() # Compute dominant frequency
  
  Auz = uz[-M:].std() # Amplitud of Oscillation
  fftuz  = abs(fft(detrend(uz[-M:])*blk(M))[:M//2]) # FFT with Blackman filter [array]
  wMuz = w0*fftuz.argmax() # Compute dominant frequency

  wFourier = min([wMEk,wMEg,wMEw,wMur,wMuw,wMuz])
  
  wLim = 2
  AnotationSize = 15
  labelpady = 16
  xPosText = 0.25
  yPosText = 0.92
  fig, axes = plt.subplots(nrows=2,ncols=3,figsize=(14,9)) # Create canvas & axes
  ## Global Kinetic Energy FFT
  axes[0,0].semilogy(w0*arange(len(fftEk)),fftEk,'k-')
  axes[0,0].annotate('$\omega^*$ = {:f}'.format(wMEk), xy=(wMEk, fftEk.max()),
          xycoords='data', xytext=(xPosText,yPosText), textcoords='axes fraction', 
          size=AnotationSize, arrowprops=dict(arrowstyle="->"))
  axes[0,0].set_xlabel('$\omega$',fontsize=labelsize,labelpad=labelpadx)
  axes[0,0].set_ylabel('$|\hat{E}_k|$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[0,0].set_xlim(0,wLim)
  axes[0,0].tick_params(labelsize=ticksize)
  ## Global Angular Momentum FFT
  axes[0,1].semilogy(w0*arange(len(fftEw)),fftEw,'k-')
  axes[0,1].annotate('$\omega^*$ = {:f}'.format(wMEw), xy=(wMEw, fftEw.max()),
          xycoords='data', xytext=(xPosText,yPosText), textcoords='axes fraction', 
          size=AnotationSize, arrowprops=dict(arrowstyle="->"))
  axes[0,1].set_xlabel('$\omega$',fontsize=labelsize,labelpad=labelpadx)
  axes[0,1].set_ylabel('$|\hat{E}_w|$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[0,1].set_xlim(0,wLim)
  axes[0,1].tick_params(labelsize=ticksize)
  ## Global Enstrophy FFT
  axes[0,2].semilogy(w0*arange(len(fftEg)),fftEg,'k-')
  axes[0,2].annotate('$\omega^*$ = {:f}'.format(wMEg), xy=(wMEg, fftEk.max()),
          xycoords='data', xytext=(xPosText,yPosText), textcoords='axes fraction', 
          size=AnotationSize, arrowprops=dict(arrowstyle="->"))
  axes[0,2].set_xlabel('$\omega$',fontsize=labelsize,labelpad=labelpadx)
  axes[0,2].set_ylabel('$|\hat{E}_{\gamma}|$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[0,2].set_xlim(0,wLim)
  axes[0,2].tick_params(labelsize=ticksize)
  ## Local Radial Velocity FFT
  axes[1,0].semilogy(w0*arange(len(fftur)),fftur,'k-')
  axes[1,0].annotate('$\omega^*$ = {:f}'.format(wMur), xy=(wMur, fftur.max()),
          xycoords='data', xytext=(xPosText,yPosText), textcoords='axes fraction', 
          size=AnotationSize, arrowprops=dict(arrowstyle="->"))
  axes[1,0].set_xlabel('$\omega$',fontsize=labelsize,labelpad=labelpadx)
  axes[1,0].set_ylabel('$|\hat{u}_r|$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[1,0].set_xlim(0,wLim)
  axes[1,0].tick_params(labelsize=ticksize)
  ## Local Azimuthal Velocity FFT
  axes[1,1].semilogy(w0*arange(len(fftuw)),fftuw,'k-')
  axes[1,1].annotate('$\omega^*$ = {:f}'.format(wMuw), xy=(wMuw, fftuw.max()),
          xycoords='data', xytext=(xPosText,yPosText), textcoords='axes fraction', 
          size=AnotationSize, arrowprops=dict(arrowstyle="->"))
  axes[1,1].set_xlabel('$\omega$',fontsize=labelsize,labelpad=labelpadx)
  axes[1,1].set_ylabel(r'$|\hat{u}_{\theta}|$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[1,1].set_xlim(0,wLim)
  axes[1,1].tick_params(labelsize=ticksize)
  ## Local Axial Velocity FFT
  axes[1,2].semilogy(w0*arange(len(fftuz)),fftuz,'k-')
  axes[1,2].annotate('$\omega^*$ = {:f}'.format(wMuz), xy=(wMuz, fftuz.max()),
          xycoords='data', xytext=(xPosText,yPosText), textcoords='axes fraction', 
          size=AnotationSize, arrowprops=dict(arrowstyle="->"))
  axes[1,2].set_xlabel('$\omega$',fontsize=labelsize,labelpad=labelpadx)
  axes[1,2].set_ylabel('$|\hat{u}_z|$',rotation=0,fontsize=labelsize,labelpad=labelpady)
  axes[1,2].set_xlim(0,wLim)
  axes[1,2].tick_params(labelsize=ticksize)
  
  fig.tight_layout()
  savefig(f'{FIG_DIR:s}{fftbn:s}.png')
  plt.close()


#####################
# Plot phase orbits #
#####################
  elevation = 30
  theta0 = 10
  dtheta = 35
  ticksize = 0.1
  labelsize = 16
  labelpadx = 0
  labelpady = 0
  labelpadz = 0
  
  fig = plt.figure(figsize=(14,10)) # Create canvas
  ## Plot Global Orbit
  for j in range(1,4):
      ax = fig.add_subplot(2,3,j,projection='3d')
      ax.xaxis.set_rotate_label(False)  # disable automatic rotation
      ax.yaxis.set_rotate_label(False)  # disable automatic rotation
      ax.zaxis.set_rotate_label(False)  # disable automatic rotation
      ax.plot(Eg,Ew,Ek,'g-')
      ax.set_xlabel('$E_{\gamma}$',fontsize=labelsize,labelpad=labelpadx)
      ax.set_ylabel('$E_{\omega}$',rotation=0,fontsize=labelsize,labelpad=labelpady)
      ax.set_zlabel('$E_k$',rotation=0,fontsize=labelsize,labelpad=labelpadz)
      ax.tick_params(labelsize=ticksize)
      ax.view_init(elevation,theta0+(j-1)*dtheta)
  ## Plot Local Orbit
  for j in range(1,4):
      ax = fig.add_subplot(2,3,j+3,projection='3d')
      ax.xaxis.set_rotate_label(False)  # disable automatic rotation
      ax.yaxis.set_rotate_label(False)  # disable automatic rotation
      ax.zaxis.set_rotate_label(False)  # disable automatic rotation
      ax.plot(ur,uw,uz,'b-')
      ax.set_xlabel('$u_r$',fontsize=labelsize,labelpad=labelpadx)
      ax.set_ylabel(r'$u_{\theta}$',rotation=0,fontsize=labelsize,labelpad=labelpady)
      ax.set_zlabel('$u_z$',rotation=0,fontsize=labelsize,labelpad=labelpadz)
      ax.tick_params(labelsize=ticksize)
      ax.view_init(elevation,theta0+(j-1)*dtheta)
      
  fig.tight_layout()
  savefig(f'{FIG_DIR:s}{orbitbn:s}.png')
  plt.close()



  dataFile = 'collectiveData.dat'
  df = pd.DataFrame(columns=['runs_#','Bo','Re','alpha','f','w*'])
  if path.exists(dataFile):
    df = pd.read_csv(dataFile, sep=" ", header=None, dtype=object) 
    df.columns=['runs_#','Bo','Re','alpha','f','w*']

  filterIndex = check(df,Bo,Re,alpha,freq)

  if filterIndex and runs > df.loc[filterIndex,'runs_#'].values:
    replaceRow(df,Bo,Re,alpha,freq,wFourier,runs,filterIndex)
  elif not filterIndex:
    df = addRow(df,Bo,Re,alpha,freq,wFourier,runs)
  
  with open(path.join(DAT_DIR, dataFile),'w') as outfile:
    df.to_csv(outfile,header=False,index=False,sep=' ')
    outfile.close()

  return None

main(f,dtinput)

