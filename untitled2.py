
# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
plt.style.use('ggplot')
pd.set_option('display.max_rows', 20)
pd.options.display.float_format = '{:.4f}'.format
# %matplotlib inline
# %config InlineBackend.figure_format = 'svg'

test_spd = pd.read_csv('csv/ЛН.csv', index_col = 0)

ax = test_spd.plot()
ax.set(xlabel = r'$\lambda$, нм', ylabel = r'$X_{e\lambda}$, отн.')

def XYZ(test_spd):
  xyz_cmf = pd.read_csv('colorimetry/ciexyz31_1.csv', index_col = 0)
  test_spd = test_spd[(test_spd.index >= 380) & (test_spd.index <= 780)]
  xyz_cmfnew = pd.DataFrame(index = test_spd.index, columns = ['X', 'Y', 'Z'])
  for i in ['X', 'Y', 'Z']:
    f = interpolate.interp1d(xyz_cmf.index, xyz_cmf[i])
    xyz_cmfnew[i] = f(test_spd.index)
  spectral_value = test_spd.columns[0]
  Xnm = test_spd[spectral_value] * xyz_cmfnew['X']
  Ynm = test_spd[spectral_value] * xyz_cmfnew['Y']
  Znm = test_spd[spectral_value] * xyz_cmfnew['Z']
  color_coordinates = {'X': np.trapz(Xnm.values, Xnm.index),
                       'Y': np.trapz(Ynm.values, Ynm.index),
                       'Z': np.trapz(Znm.values, Znm.index)}
  return color_coordinates

def XYZ2xy(color_coordinates):
  X = color_coordinates['X']
  Y = color_coordinates['Y']
  Z = color_coordinates['Z']
  xy_chromacity = {'x': X/(X + Y + Z), 'y': Y/(X + Y + Z)}
  return xy_chromacity

def xy2uv(xy_chromacity):
  x = xy_chromacity['x']
  y = xy_chromacity['y']
  uv_chromacity = {'u': 4*x /(-2*x + 12*y + 3),
                   'v': 6*y /(-2*x + 12*y + 3)}
  return uv_chromacity

def plank(T, nm = np.arange(100, 6000, 1)):
  C1 = 3.741771e-16
  C2 = 1.4388e-2
  M = C1*(nm*1e-9)**(-5)*(np.exp(C2/((nm*1e-9)*T))-1)**(-1)
  ref = pd.DataFrame({'W/m^3':M}, index = nm)
  ref.index.name = 'nm'
  return ref

xyz_test = XYZ(test_spd)
xyz_test

xy_chromacity = XYZ2xy(xyz_test)
xy_chromacity

uv_test = xy2uv(xy_chromacity)
uv_test

xtest = xy_chromacity['x']
ytest = xy_chromacity['y']

n = (xtest - 0.3320)/(ytest - 0.1858)
T = -449*n**3 + 3525*n**2 - 6823.3*n + 5530.33
T

spectr_range = np.arange(80, 5000, 1)
ref_spd = plank(T, nm = spectr_range)

plt.figure(figsize=(10,5))

x = np.append(ref_spd.index[0], ref_spd.index)
y = np.append(0, ref_spd.values)
plt.plot(x,y)

plt.xlabel('нм')
plt.ylabel(r'Вт/м$^3$')
plt.grid(True)

xyz_ref = XYZ(ref_spd)
xyz_ref

xy_ref = XYZ2xy(xyz_ref)
xy_ref

tcs = pd.DataFrame()
tcs = pd.read_csv('colorimetry/TSC(CRI).csv', index_col=0)
tcs.loc[:,'TCS01':'TCS07']

yaxes = ['TCS01', 'TCS02', 'TCS03', 'TCS04',
'TCS05', 'TCS06', 'TCS07', 'TCS08']

title = 'Коэффициенты отражения контрольных образцов'
plt.style.use('ggplot')
ax = tcs.plot(use_index = True, y=yaxes,
              title=title, grid = True)
ax.set(ylabel=r'$\rho$', xlabel=r'$\lambda, нм$')

def XYZ_tcs(spd, tcs, k):
  xyz_cmf = pd.read_csv('colorimetry/ciexyz31_1.csv',index_col = 0)
  spd = spd[(spd.index >= 380) & (spd.index <= 780)]
  xyz_cmfnew = pd.DataFrame(index = spd.index, columns = ['X','Y', 'Z'])
  
  for i in ['X', 'Y', 'Z']:
    f = interpolate.interp1d(xyz_cmf.index, xyz_cmf[i])
    xyz_cmfnew[i] = f(spd.index)
  spectral_value = spd.columns[0]
  
  f = interpolate.interp1d(tcs.index, tcs.values)
  tcs = f(spd.index)
  Xnm = k * spd[spectral_value] * xyz_cmfnew['X'] * tcs
  Ynm = k * spd[spectral_value] * xyz_cmfnew['Y'] * tcs
  Znm = k * spd[spectral_value] * xyz_cmfnew['Z'] * tcs
 
  color_coordinates = {'X': np.trapz(Xnm.values, Xnm.index),
                       'Y': np.trapz(Ynm.values, Ynm.index),
                       'Z': np.trapz(Znm.values, Znm.index)}
  return color_coordinates

k_test = 100/xyz_test['Y']

calctbl_test = {}
for i in tcs.columns:
  calctbl_test[i] = XYZ_tcs(test_spd, tcs[i], k_test)
calctbl_test = pd.DataFrame(calctbl_test)
calctbl_test.loc[:,'TCS01':'TCS08'].T

k_ref = 100/xyz_ref['Y']

calctbl_ref = {}
for i in tcs.columns:
  calctbl_ref[i] = XYZ_tcs(ref_spd, tcs[i], k_ref)
calctbl_ref = pd.DataFrame(calctbl_ref)
calctbl_ref.loc[:,'TCS01':'TCS08'].T

calctbl_test = calctbl_test.T
calctbl_test['x'] = calctbl_test['X']/(calctbl_test['X']+calctbl_test['Y']+calctbl_test['Z'])
calctbl_test['y'] = calctbl_test['Y']/(calctbl_test['X']+calctbl_test['Y']+calctbl_test['Z'])

calctbl_ref = calctbl_ref.T
calctbl_ref['x'] = calctbl_ref['X']/(calctbl_ref['X']+calctbl_ref['Y']+calctbl_ref['Z'])
calctbl_ref['y'] = calctbl_ref['Y']/(calctbl_ref['X']+calctbl_ref['Y']+calctbl_ref['Z'])
calctbl_ref.round(4)

calctbl_test['u'] = 4*calctbl_test['x']/(-2 * calctbl_test['x'] + 12 * calctbl_test['y'] + 3)
calctbl_test['v'] = 6*calctbl_test['y']/(-2 * calctbl_test['x'] + 12 * calctbl_test['y'] + 3)

calctbl_ref['u'] = 4*calctbl_ref['x']/(-2*calctbl_ref['x']+ 12*calctbl_ref['y']+3)
calctbl_ref['v'] = 6*calctbl_ref['y']/(-2*calctbl_ref['x']+ 12*calctbl_ref['y']+3)

ut = uv_test['u']
vt = uv_test['v']

calctbl_test['W'] = 25*calctbl_test['Y']**(1/3)-17
calctbl_test['U'] = 13*calctbl_test['W']*(calctbl_test['u'] - ut)
calctbl_test['V'] = 13*calctbl_test['W']*(calctbl_test['v'] - vt)
calctbl_test;

uv_ref = xy2uv(xy_ref)
ur = uv_ref['u']
vr = uv_ref['v']

calctbl_ref['W'] = 25*calctbl_ref['Y']**(1/3)-17
calctbl_ref['U'] = 13*calctbl_ref['W']*(calctbl_ref['u'] - ur)
calctbl_ref['V'] = 13*calctbl_ref['W']*(calctbl_ref['v'] - vr)
calctbl_ref;

deltaE = np.sqrt((calctbl_test['W'] - calctbl_ref['W'])**2 + (calctbl_test['U'] - calctbl_ref['U'])**2 + (calctbl_test['V'] - calctbl_ref['V'])**2)
deltaE

Ri = 100 - 4.6 * deltaE
Ri

Ra = np.sum(Ri['TCS01':'TCS08'])/8
Ra
