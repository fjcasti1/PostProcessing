
#!/usr/bin/env python
#from hellaPy import *
from numpy import *
from pylab import *
from scipy.signal import blackman as blk
import os,sys,natsort,glob,multiprocessing
import matplotlib.pyplot as plt

#Directory where the data lives
datdir  = sys.argv[1]
#datdir='./runs_0/'

#FIG_DIR = f'fig/{runs_dir:s}/'
#OUT_DIR = f'dat/{runs_dir:s}/'

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
#  print(traces)
  Re=np.zeros(len(traces))
  Bo=np.zeros(len(traces))
  beta=np.zeros(len(traces))
  alpha=np.zeros(len(traces))
  St=np.zeros(len(traces))
  std=np.zeros(len(traces))
  i=0
  for data in traces:
    Re[i]=loadtxt(datdir+data).T[0]
    Bo[i]=loadtxt(datdir+data).T[1]
    beta[i]=loadtxt(datdir+data).T[2]
    alpha[i]=loadtxt(datdir+data).T[3]
    St[i]=loadtxt(datdir+data).T[4]
    std[i]=loadtxt(datdir+data).T[5] #or amplitude of wave
    i+=1
  
  BoValues=sort(unique(Bo))        #get all the Bo values present
  M=np.vstack((Re,std,Bo)).T #put all the data in one array
  M=M[M[:,0].argsort()]      #sort with Reynolds

  fig1=figure(1)
  for value in BoValues:
    condition=M[:,2]==value
    m=M[condition]
    plt.semilogy(m[:,0],m[:,1],'-s',label=["Bo=",str(value)])
      
  Bostr = ["" for x in range(len(BoValues))]
  for i in range(0,len(BoValues)):
    Bostr[i]=str(BoValues[i])

  plt.grid()
  xlabel('Re')
  ylabel('$\sigma$',rotation=0,labelpad=20)
  plt.legend([str(BoValues[j])  for j in range(len(BoValues))])
  title_string = ('Results Comparison') 
  title(title_string)
  fig1.savefig('Figure1.png')

  fig2=figure(2)
  for value in BoValues:
    condition=M[:,2]==value
    m=M[condition]
    plot(m[:,0],m[:,1],'-s',label=["Bo=",str(value)])
      
  Bostr = ["" for x in range(len(BoValues))]
  for i in range(0,len(BoValues)):
    Bostr[i]=str(BoValues[i])

  plt.grid()
  xlabel('Re')
  ylabel('$\sigma$',rotation=0,labelpad=20)
  plt.legend([str(BoValues[j])  for j in range(len(BoValues))])
  title_string = ('Results Comparison') 
  title(title_string)
  fig2.savefig('Figure2.png')



 ############ For the bifurcation diagram ###############
  del BoValues
  BoValues=['5e2', '1e2', '4e1', '2e1', '15e0', '1e1', '4e0', '2e0',\
       '15e-1', '1e0', '67e-2', '5e-1']
  Bo=np.zeros(len(BoValues))
  Bo_scale=np.zeros(len(BoValues))
  Rec=np.zeros(len(BoValues))
 
#  pat_names=get_paternNames(BoValues[0])
  i=0
  for Bovalue in BoValues:
    Bo[i]=float(Bovalue)
    Bo_scale[i]=float(Bovalue)**(-2/3)
    if (Bovalue=='5e2'):
      ReValues=['12e2', '1250e0', '1300e0', '1350e0', '14e2',\
          '1450e0', '1500e0', '1550e0', '16e2']

    elif (Bovalue=='1e2'):
      ReValues=['12e2', '1250e0', '1300e0', '1350e0', '14e2',\
          '1450e0', '1500e0', '1550e0', '16e2']

    elif (Bovalue=='4e1'):
      ReValues=['1300e0', '1350e0', '14e2','1450e0', '1500e0', '1550e0', '16e2']

    elif (Bovalue=='2e1'):
      ReValues=['1350e0', '14e2','1450e0', '1500e0', '1550e0', '16e2']

    elif (Bovalue=='15e0'):
      ReValues=['1350e0', '14e2','1450e0', '1500e0', '1550e0', '16e2']

    elif (Bovalue=='1e1'):
      ReValues=['1300e0', '1350e0', '14e2','1450e0', '1500e0', '1550e0', '16e2']

    elif (Bovalue=='4e0'):
      ReValues=['14e2', '1450e0', '1500e0', '1550e0', '16e2',\
          '1750e0', '1700e0', '1750e0', '18e2']

    elif (Bovalue=='2e0'):
      ReValues=['1500e0', '1550e0', '16e2','1750e0', '1700e0', '1750e0', '18e2', '20e2']

    elif (Bovalue=='15e-1'):
      ReValues=['16e2', '1650e0', '1700e0', '1750e0', '18e2',\
          '1850e0', '1900e0', '1950e0']

    elif (Bovalue=='1e0'):
      ReValues=['18e2','1850e0', '1900e0', '1950e0', '20e2']

    elif Bovalue=='67e-2':
      ReValues=['18e2', '1850e0', '1900e0', '1950e0', '20e2',\
          '2050e0', '2100e0', '2150e0', '22e2']

    elif Bovalue=='5e-1':
      ReValues=['20e2', '22e2', '24e2']
    del Re
    del std
    Re=np.zeros(len(ReValues))
    std=np.zeros(len(ReValues))
    j=0
#    print('')
#    print('Doing Bo = '+Bovalue)
#    print('')
    for Revalue in ReValues:
      Re[j]=float(Revalue)
#      print(Re)
#      dataname="ts_Re"+Revalue+"_Bo"+Bovalue+"_beta"+betavalue+"_alpha"+alphavalue+"_St"+Stvalue+"_M201_dt5e-3.txt"
      dataname="ts_Re"+Revalue+"_Bo"+Bovalue+"_beta1e0_alpha0e0_St0e0_M201_dt5e-3.txt"
#      print(dataname)
      std[j]=loadtxt(datdir+dataname).T[5] #or amplitude of wave
#      print(std)
      j+=1
    p=np.poly1d(np.polyfit(Re,std,1))
    Rec[i]=roots(p)
#    print(roots(p))
    i+=1 
  print('')
  print('Critical Reynolds')
  print(Rec)
  print('')

  savetxt('bif_curve.dat',c_[Bo,Bo_scale,Rec],comments='',\
      header='{:>10s} {:>10s} {:>10s}'.format('Bo','Bo_scale','Re_c'),fmt='%10.3e')
  Boscaled=np.power(Bo,-2/3)
  fig3=figure(3)
  plot(Boscaled,Rec,'-s')
  plt.grid()
  xlabel(r'$\log(Bo)$')
  ylabel(r'$Re_c$',rotation=0,labelpad=20)
#  plt.legend([str(BoValues[j])  for j in range(len(BoValues))])
  title_string = ('Critical Reynolds') 
  title(title_string)
  show()
  fig3.savefig('Figure3.png')

  return None

main()

