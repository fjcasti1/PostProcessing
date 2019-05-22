import numpy as np
import matplotlib.pyplot as plt
import os

FIG_DIR = os.environ["SCRATCH"]+'/generalKnifeEdge/figL2/'

# Create some mock data
BoBif = np.array([1e-1,5e-1,67e-2,1e0,15e-1,2e0,4e0,\
    1e1,15e0,2e1,4e1,1e2,5e2])
ReBif = np.array([3350,2080,1930,1760,1630,1550,1420,\
    1320,1300,1280,1270,1250,1250])
wBif  = np.array([3.7699,6.1485,6.6422,7.3154,7.9437,8.3028,9.0657,\
    9.6492,9.7838,9.8736,9.9633,10.0531,10.0980])*1e-2/(2*np.pi)


fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('$\omega$')
ax1.set_ylabel('$Bo^{-2/3}$', color=color)
ax1.plot(wBif, BoBif**(-2/3), color=color, marker='o')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('$Re$', color=color)  # we already handled the x-label with ax1
ax2.plot(wBif, ReBif, color=color,marker='o')
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.savefig(f'{FIG_DIR:s}FreqBifScaled_alpha0e0_f0e0.png')
plt.close()

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('$\omega$')
ax1.set_ylabel('$Bo$', color=color)
ax1.plot(wBif, BoBif, color=color, marker='o')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('$Re$', color=color)  # we already handled the x-label with ax1
ax2.plot(wBif, ReBif, color=color,marker='o')
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.savefig(f'{FIG_DIR:s}FreqBif_alpha0e0_f0e0.png')
plt.close()
