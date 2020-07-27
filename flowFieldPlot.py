import sys,os,errno
from myPlots import *
from cheb import *
from numpy import *
from pylab import *
from glob import glob
from matplotlib import rcParams
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import multiprocessing as mp
from functools import partial

rcParams['text.usetex'] = True

mkl_set_num_threads(1)
NPROCS=4

CONTOUR_OPTIMIZING = True
CONTOUR_OPTIMIZING = False

RESTART_PATH = sys.argv[1]
OUT_DIR = sys.argv[2]
REQ_FIELD = sys.argv[3]
IMA = float(sys.argv[4])
GMA = float(sys.argv[5])
pertIMA = float(sys.argv[6])
pertGMA = float(sys.argv[7])
if len(sys.argv)==9 and sys.argv[8]=="PROBEMODE":
  PROBE_MODE = True
else:
  PROBE_MODE = False
autoOUT_DIR='fig/'
EPS=0.15  # Percentage of domain that is left for each wall

#OUT_FILE_TYPE = OREC = orec  = 'pdf'
OUT_FILE_TYPE = 'png'

##                      # Paint Domain | Paint Range
#ALL_CMAP     = mycm19  #    [-a, a]   | dark blue to dark red
#NEG_EXT_CMAP = myBlues #    [-b,-a]   | dark blue, blue
#INT_CMAP     = mycm15  #    [-a, a]   | blue,white,red
#POS_EXT_CMAP = myReds  #    [ c, d]   | red, dark red

# TOLERANCE = 1e-8

# Geometric parameters
Hasp = Rasp = 2
Nz = Nr = 201
z = linspace(0, Hasp, Nz)
r = linspace(0, Rasp, Nr)
Z,R = meshgrid(z,r,indexing='ij')

# ======================================================================
# --------------------------- SUBROUTINES ------------------------------
# ======================================================================

# def pause():
#   wait = input("Press <ENTER> to continue")
#   return None

def create_outdir(bn,outdir):
  if outdir=='auto':
    tokens  = ['Bo','Re','Ro','wf','Gamma','eta','NtsT','NT']
    try:
      values = [ parse_token(longbn,token) for token in tokens ]
      Bo   = values[0]
      Re   = values[1]
      Ro   = values[2]
      wf   = values[3]  # Forcing Angular Freq
      Gamma= values[4]
      eta  = values[5]
      NtsT = int(values[6])
      NT   = int(values[7])
      runs = f.split('runs_')[-1].split('/')[0]
    except Exception as ex:
      print('Exception in parse token: ', ex)
    outdir=(f'{autoOUT_DIR:s}')
    print('\n')
    print(f'{"":=<42s}')
    print('OUTPUT DIRECTORY GENERATED AUTOMATICALLY')
    print(f'{"":=<42s}')
    print('OUTDIR = ', outdir)
  if not os.path.exists(outdir):
    try:
      os.makedirs(outdir, 0o700)
    except OSError as e:
      if e.errno != errno.EEXIST:
        raise
      pass
  return outdir

def parse_token(bn,token):
  return bn.split(token)[1].split('_')[0]

def get_files_to_plot():
  drecs = []
  if '*' in RESTART_PATH:
    drecs = glob(RESTART_PATH) # list of input restarts, path included
    if not drecs:
      print('\nNO FILES FOUND MATCHING THE PATTERN:  ', RESTART_PATH)
      print('--> QUITTING')
      sys.exit(1)
  else:
    drecs.append(RESTART_PATH)
    if not os.path.exists(RESTART_PATH):
      print('\nFILE ',RESTART_PATH,' NOT FOUND')
      print('--> QUITTING')
      sys.exit(1)
  frecs=[]
  for drec in drecs:
    #if isPlotted(drec):     # Check if they have been plotted already
    #  print('FILE ',drec, 'ALREADY PLOTTED')
    #else:
    frecs.append(drec)
  drecs = frecs
  drecs.sort()
  return drecs

def isPlotted(f):
  plotted = False
  if os.path.exists(OUT_DIR+'/'+get_figname(os.path.basename(f),REQ_FIELD)):
    plotted = True
  return plotted

def get_figname(f,field,label=''):
  return (f'{field:s}{label:s}_{f:s}.{OUT_FILE_TYPE:s}')

def read_field(fheader,udt,pdt,pcount=1):
  pad     = fromfile(fheader,dtype=pdt,count=1)
  field_s = fromfile(fheader,dtype=udt,count=1)
  field_x = fromfile(fheader,dtype=udt,count=1)
  field_g = fromfile(fheader,dtype=udt,count=1)
  pad     = fromfile(fheader,dtype=pdt,count=1)
  s = field_s[0].astype(double).T
  x = field_x[0].astype(double).T
  g = field_g[0].astype(double).T
  return (s,x,g)

def reader(f,fmean=0,label=''):
  hdt = dtype('(4)i4, (4)f8, (2)i4, (8)f8, i4') # header data type
  pdt = dtype('i4') # padding data type
  with open(f,'rb') as fh:
    header= fromfile(fh,dtype=hdt,count=1)
    Nz = header[0][0][1]  # M=Nz, N=Nr
    Nr = header[0][0][2]  # M=Nz, N=Nr
    Hasp  = header[0][3][6]
    Rasp  = header[0][3][7]
    t   = header[0][1][3]
    udt = dtype('({:d},{:d}) f8'.format(Nz,Nr))
    s, x, g = read_field(fh,udt,pdt)
  retd = {
    's' : s,
    'x' : x,
    'g' : g,
    't' : t,
  }
  if PROBE_MODE:
    Q = retd[REQ_FIELD]-fmean
    gma = abs(Q).max()
    Lz=max(z)-min(z)
    Lr=max(r)-min(r)
    indz = abs(z-EPS*Lz).argmin()
    indr = abs(r-EPS*Lr).argmin()  #
    indr = indz = 30
    ima = abs(Q[indz:-indz,indr:-indr]).max()
            # ->  Only works for equispaced grids, if not use indmin and indmax
    fbase = get_figname(os.path.basename(f),REQ_FIELD,label)
#    probe_res = ('{:s}' + 3*' {:+21.7e}'+'\n').format(fbase,ima,gma,gma/ima)
    probe_res = ('{:s}' + 2*' {:+21.7e}'+'\n').format(fbase,ima,gma)
    fgbase = fbase[0:-9]

#    datafile = (f'{REQ_FIELD:s}{label:s}_bounds.dat')
    datafile = (f'{fgbase:s}_bounds.dat')
    file = open(datafile,'a')
    file.write(probe_res)
  return retd

###def header_print(num_files):
###  print(72*'=')
###  print(f'NUM FILES: {num_files:d}')
###  print(72*'-')
###  if NPROCS > 1:
###    print('PARALLEL MODE')
###    print(r'NPROCS: {NPROCS:d}')
###  else:
###    print('SERIAL MODE')
###  print(f'PLOTTING FIELD: {REQ_FIELD:s}')
###  print(72*'-')
###  print('{:^28s} {:^10s} {:^10s} {:^10s} {:^10s}'.format(
###      f'file (under {OUT_DIR:s}/)','ima','gma','gma/ima'
###    )
###  )
###  return None

def mycf(X,Y,field,ima=None,gma=None,fn=1,fb=4,fgamma=1,Nell=33,Nred=3):
  if not gma: #TODO: Needs to find interior and global maximum, ima wrong atm
      gma = abs(field).max()
  if not ima:
      ima = abs(field).max()
  f,a = no_ax_fig(fn,fb,fgamma)
  if ima == gma:
    gma = gma*1.0001
  ell = pylab.linspace(-ima,ima,Nell)
  red = pylab.linspace(ima,gma,Nred)
  blu = -red[::-1]
  f,a = no_ax_fig(fn,fb,fgamma)
  mycontourf(X,Y,field,lc='#777777',lw=0.01,levels=blu,cmap=myBlues)
  mycontourf(X,Y,field,lc='#777777',lw=0.01,levels=ell,cmap=mycm15)
  mycontourf(X,Y,field,lc='#777777',lw=0.01,levels=red,cmap=myReds)
  if field.min() < 0 and field.max() > 0:
      contour(X,Y,field,levels=[0],linestyles='-',colors='#777777')
  return None

def main(f,fmean=0,label='',mode='normal'):
  data  = reader(f,fmean,label)
  Gamma = float(parse_token(f,"Gamma"))
  if not PROBE_MODE:
    if (mode=='normal'):
      mycf(Z,R,transpose(data[REQ_FIELD]),ima=IMA,gma=GMA,fgamma=Gamma)
    elif mode=='perturbation':
      mycf(Z,R,transpose(data[REQ_FIELD]-fmean),ima=pertIMA,gma=pertGMA)

  out_fig = get_figname(os.path.basename(f),REQ_FIELD,label)
  savefig(OUT_DIR+'/'+out_fig)
  plt.close()
  return data[REQ_FIELD]#,data['Z'],data['R']

if __name__ == '__main__':
  bn = os.path.basename(RESTART_PATH) # basename
  OUT_DIR = create_outdir(bn,OUT_DIR)
  drecs = get_files_to_plot()

  if not CONTOUR_OPTIMIZING:
    if NPROCS > 1:
      pool = mp.Pool(processes=NPROCS)
      D = pool.map(main,drecs)
      mkl_set_num_threads(NPROCS)
      D = array(D)
      E = mean(D,axis=0)
      if not PROBE_MODE:
        mycf(Z,R,transpose(E),ima=IMA,gma=GMA)
        out_fig = get_figname(os.path.basename(drecs[0].replace('_0001','')),REQ_FIELD,'_mean')
        savefig(OUT_DIR+'/'+out_fig)
        plt.close()
      if not (pertIMA==0 and pertGMA==0):
        main2 = partial(main,fmean=E,label='_pert',mode='perturbation')
        D = pool.map(main2,drecs)
      mkl_set_num_threads(1)
    else:
      for drec in drecs:
        main(drec)
  else:
    main(drecs[len(drecs)//2])
#      print('\n')
#      print(f'{"":=<28s}')
#      print('PLOTTING FIELD')
#      print(f'{"":=<28s}')
