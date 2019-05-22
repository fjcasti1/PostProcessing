
#!/usr/bin/env python
#from hellaPy import *
from numpy import *
from pylab import *
from scipy.signal import blackman as blk
import os,sys,natsort,glob,multiprocessing
import matplotlib.pyplot as plt

#Directory where the data lives
datdir  = sys.argv[1]

def get_paternNames(f):
  glob_str = pat_str = f
  G = glob.glob(pat_str)
  F = natsort.realsorted(G)
  return F

def get_allnames(f):
  return os.listdir(f) #where f is the path to the directory

def get_basename(f):
  return f.split('/')[-1]

def parse_token(bn,token):
  return bn.split(token)[1].split('_')[0]
  
def main():
  traces=get_allnames(datdir)
  Re=np.zeros(len(traces))
  Bo=np.zeros(len(traces))
  alpha=np.zeros(len(traces))
  f=np.zeros(len(traces))
  w=np.zeros(len(traces))
  stdx=np.zeros(len(traces))
  stdE=np.zeros(len(traces))
  i=0
# Bo Re alpha freq w AE wME State
  for data in traces:
    Bo[i]=loadtxt(datdir+data).T[0]
    Re[i]=loadtxt(datdir+data).T[1]
    alpha[i]=loadtxt(datdir+data).T[2]
    f[i]=loadtxt(datdir+data).T[3]
    w[i]=loadtxt(datdir+data).T[4]
    stdE[i]=loadtxt(datdir+data).T[5] #or amplitude of wave
    i+=1
  
  BoValues=sort(unique(Bo))        #get all the Bo values present
  M=np.vstack((Re,Bo,stdE)).T #put all the data in one array
  M=M[M[:,0].argsort()]            #sort with Reynolds

  fig1=figure(1)
  for value in BoValues:
    condition=M[:,1]==value
    m=M[condition]
    plt.semilogy(m[:,0],m[:,2],'-s',label=["Bo=",str(value)])
  plt.grid()
  xlabel('Re')
  ylabel('$\sigma$',rotation=0,labelpad=10)
  title_string = ('L2-norm Kinetic Energy') 
  title(title_string)
  fig1.savefig('Figure1.png')

  fig2=figure(2)
  for value in BoValues:
    condition=M[:,1]==value
    m=M[condition]
    plot(m[:,0],m[:,2],'-s',label=["Bo=",str(value)])
  plt.grid()
  xlabel('Re')
  ylabel('$\sigma$',rotation=0,labelpad=10)
  title_string = ('L2-norm Kinetic Energy') 
  title(title_string)
  fig2.savefig('Figure2.png')

 ############ For the bifurcation diagram ###############
  del BoValues
  BoValues=['5e2', '1e2', '4e1', '2e1', '15e0', '1e1', '4e0', '2e0',\
       '15e-1', '1e0', '67e-2', '5e-1']
  Bo=np.zeros(len(BoValues))
  Bo_scale=np.zeros(len(BoValues))
  RecE=np.zeros(len(BoValues))
 
  i=0
  for Bovalue in BoValues:
    Bo[i]=float(Bovalue)
    Bo_scale[i]=float(Bovalue)**(-2/3)
    if (Bovalue=='5e2'):
      ReValuesE=['1240e0', '1250e0', '1260e0']

    elif (Bovalue=='1e2'):
      ReValuesE=['1250e0', '1260e0', '1270e0']

    elif (Bovalue=='4e1'):
      ReValuesE=['1260e0', '1270e0', '1280e0']

    elif (Bovalue=='2e1'):
      ReValuesE=['1280e0', '1290e0', '1300e0']

    elif (Bovalue=='15e0'):
      ReValuesE=['1290e0', '1300e0', '1350e0']

    elif (Bovalue=='1e1'):
      ReValuesE=['1310e0', '1320e0', '1330e0']

    elif (Bovalue=='4e0'):
      ReValuesE=['1410e0', '1420e0', '1430e0']

    elif (Bovalue=='2e0'):
      ReValuesE=['1550e0', '1560e0', '1570e0']

    elif (Bovalue=='15e-1'):
      ReValuesE=['1630e0', '1640e0', '1650e0']

    elif (Bovalue=='1e0'):
      ReValuesE=['1760e0', '1770e0', '1780e0']

    elif Bovalue=='67e-2':
      ReValuesE=['1930e0', '1940e0', '1950e0']
    elif Bovalue=='5e-1':
      ReValuesE=['2080e0', '2090e0', '2100e0']
    del stdE
    ReE=np.zeros(len(ReValuesE))
    stdE=np.zeros(len(ReValuesE))

    j=0
    for Revalue in ReValuesE:
      ReE[j]=float(Revalue)
      dataname="ts_Re"+Revalue+"_Bo"+Bovalue+"_alpha0e0_f0e0.txt"
      stdE[j]=loadtxt(datdir+dataname).T[5] #or amplitude of wave, kinetic Energy
      j+=1

    pE=np.poly1d(np.polyfit(ReE,stdE,1))
    RecE[i]=roots(pE)
    i+=1 

  print('')
  print('Critical Reynolds')
  print(RecE)
  print('')

  savetxt('bif_curve.dat',c_[Bo,Bo_scale,RecE],comments='',\
      header='{:>10s} {:>10s} {:>10s}'.format('Bo','Bo_scale','Rec_E'),fmt='%10.3e')
  Boscaled=np.power(Bo,-2/3)

  fig3=figure(3)
  plot(Boscaled,RecE,'-s')
  plt.grid()
  xlabel(r'$Bo^{-2/3}$')
  ylabel(r'$Re_c$',rotation=0,labelpad=20)
  title_string = ('Critical Reynolds with L2 Kinetic Energy') 
  title(title_string)
  fig3.savefig('Figure3.png')
  return None

main()

