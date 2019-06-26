import sys,os,errno
from hellaPy import *
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
NPROCS=8

CONTOUR_OPTIMIZING = True
CONTOUR_OPTIMIZING = False

RESTART_PATH = sys.argv[1]
OUT_DIR = sys.argv[2]
autoOUT_DIR='movies/'
EPS=0.15  # Percentage of domain that is left for each wall

#OUT_FILE_TYPE = OREC = orec  = 'pdf'
OUT_FILE_TYPE = OREC = orec  = 'png'

#                      # Paint Domain | Paint Range
ALL_CMAP     = mycm19  #    [-a, a]   | dark blue to dark red
NEG_EXT_CMAP = myBlues #    [-b,-a]   | dark blue, blue
INT_CMAP     = mycm15  #    [-a, a]   | blue,white,red
POS_EXT_CMAP = myReds  #    [ c, d]   | red, dark red

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
    tokens = ['alpha','Bo','Re','f']
    values = [parse_token(bn,token) for token in tokens]
    alpha = values[0]
    Bo = values[1]
    Re = values[2]
    f  = values[3]
    outdir=(f'{autoOUT_DIR:s}alpha{alpha:s}/Bo{Bo:s}/Re{Re:s}')
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
    if isPlotted(drec):     # Check if they have been plotted already
      print('FILE ',drec, 'ALREADY PLOTTED')
    else:
      frecs.append(drec)
  drecs = frecs
  drecs.sort()
  return drecs 

def isPlotted(f):
  plotted = False
  if os.path.exists(OUT_DIR+'/'+get_figname(os.path.basename(f))):
    plotted = True
  return plotted

def get_figname(f,field='surf_v',label=''):
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

  v = np.append([0],np.true_divide(g[Nz-1,1:],r[1:]))
  retd = {
    'v' : v,
    't' : t,
  }
  return retd

def myplot(x, q, out_fig, xmin=0, xmax=2, ymin=0, ymax=1.0001):
  plt.plot(x,q,'b')
#  plt.grid() # grid off
  plt.axis([xmin, xmax, ymin, ymax])
  savefig(OUT_DIR+'/'+out_fig)
  return None

def main(f):
  data  = reader(f)
  myplot(r, data['v'], get_figname(os.path.basename(f)))
  return data['v']

if __name__ == '__main__':
  bn = os.path.basename(RESTART_PATH) # basename
  OUT_DIR = create_outdir(bn,OUT_DIR)
  drecs = get_files_to_plot()

  if NPROCS > 1:
    pool = mp.Pool(processes=NPROCS)
    print("PLOTTING")
    D = pool.map(main,drecs)
    mkl_set_num_threads(NPROCS)
    D = array(D)
    E = mean(D,axis=0)
    myplot(r, E, get_figname(os.path.basename(drecs[0][:-5]),'surf_v','_mean'))
    mkl_set_num_threads(1)
  else:
    for drec in drecs:
      main(drec)
#      print('\n')
#      print(f'{"":=<28s}')
#      print('PLOTTING FIELD')
#      print(f'{"":=<28s}')
