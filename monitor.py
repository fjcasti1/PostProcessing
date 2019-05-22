#!/usr/bin/env python
from hellaPy import *
from numpy import *
from pylab import *
from matplotlib import pyplot as plt
from matplotlib import gridspec as gridspec
from mpl_toolkits.mplot3d import axes3d
from scipy.signal import blackman as blk
import os,sys,natsort,glob,multiprocessing,math

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
OUT_DIR = f'dat/{res_dir:s}'

#print("")
#print(FIG_DIR)

################################
#print("")
##print(f'fig/{fig_dir(res_dir):s}/')
#print(fig_dir(res_dir))
#print(f)
################################

def ts_basename(f):
  return f.split('/')[-1]

def shorten_basename(f):
  return f.split('_TU')[0]

def fft_basename(f):
  return f.replace('ts_','fft_')

def orbit_basename(f):
  return f.replace('ts_','orbit_')

def parse_token(bn,token):
  return bn.split(token)[1].split('_')[0]
  
def main(f,dtinput):
  tsbn    = ts_basename(f)
  fftbn   = fft_basename(tsbn)
  orbitbn = orbit_basename(tsbn)
  shortbn = shorten_basename(tsbn)
  tokens  = ['Re','Bo','alpha','f','TU'] 
  try:
    values = [ parse_token(tsbn,token) for token in tokens ]
    Re   = values[0]
    Bo   = values[1]
    alpha= values[2]
    freq = values[3]
    TU   = int(values[4])
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

  title_string = tsbn.replace('_',' ')
  t,Ek,Eg,Ew,ur,uw,uz = loadtxt(f).T
  os.makedirs(FIG_DIR,exist_ok=True)

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

###  if TU>0:
###    if TU==14000:
###      M = 2*1249200 #two periods?
###    elif TU==12000:
###      M = len(Ek)//10
###  elif TU<0:
###    M = len(Ek)
###  AE = Ek[-M:].std()
###  Ax = xmax[-M:].std()
###  # Compute dominant frequency
###  T = M*dt
###  w0= 2*pi/T
###  pE = abs(fft(detrend(Ek[-M:])*blk(M))[:M//2])
###  wME= w0*pE.argmax()
###  clf()
###  semilogy(arange(len(pE))*w0,pE,'k-')
###  xlim(0,1.2)
###  xlabel('resp. freq.')
###  ylabel('resp. power')
###  savefig(f'{FIG_DIR:s}{fftbn:s}.png')
###  os.makedirs(OUT_DIR,exist_ok=True)
###  state = '   00'
###  with open(f'{OUT_DIR:s}{shortbn:s}.txt','w') as fh:
###    print(f'{Bo:s} {Re:s} {alpha:s} {freq:s} {w:16.7e} {AE:16.7e} {wME:16.7e} {state:s}',file=fh)

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

  return None

main(f,dtinput)

