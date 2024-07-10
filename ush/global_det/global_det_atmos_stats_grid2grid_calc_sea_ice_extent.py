#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_grid2grid_calc_sea_ice_extent.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This script calculates the forecast and observation
          sea-ice extent.
Run By: python embedding for parm/metplus_config/global_det/atmos_grid2grid/stats/StatAnalysis_fcstGLOBAL_DET_obsOSI-SAF_DailyAvg_Extent_MPRtoSL1L2.conf
'''

import os
import sys
import numpy as np
from pyproj import Geod
from pyproj import CRS
import netCDF4 as netcdf
import datetime
import global_det_atmos_util as gda_util

print("Python Script:\t" + repr(sys.argv[0]))

def iceArea(lon1,lat1,ice1):
    """
    Compute the cell side dimensions (Vincenty) and the cell surface areas.
    This assumes the ice has already been masked and subsampled as needed
    returns ice_extent, ice_area, surface_area = iceArea(lon,lat,ice)
    surface_area is the computed grid areas in km**2)
    """
    lon=lon1.copy()
    lat=lat1.copy()
    ice=ice1.copy()
    g=Geod(ellps='WGS84')
    _,_,xdist=g.inv(lon,lat,np.roll(lon,-1,axis=1),np.roll(lat,-1,axis=1))
    _,_,ydist=g.inv(lon,lat,np.roll(lon,-1,axis=0),np.roll(lat,-1,axis=0))
    xdist=np.ma.array(xdist,mask=ice.mask)/1000.
    ydist=np.ma.array(ydist,mask=ice.mask)/1000.
    xdist=xdist[:-1,:-1]
    ydist=ydist[:-1,:-1]
    ice=ice[:-1,:-1]     # just to match the roll
    extent=xdist*ydist   # extent is surface area only
    area=xdist*ydist*ice # ice area is actual ice cover (area * concentration)
    return extent.flatten().sum(), area.flatten().sum(), extent

# Check for needed environment variables
env_var_list = ['MODEL', 'DATE', 'valid_hr_start', 'valid_hr_end',
                'fhr_list', 'hemisphere', 'grid', 'DATA', 'VERIF_CASE', 'STEP',
                'RUN']
for env_var in env_var_list:
    if not env_var in os.environ:
        print("FATAL ERROR: "+repr(sys.argv[0])
              +" -> No environment variable "+env_var)
        sys.exit(1)
MODEL = os.environ['MODEL'].replace('"', '')
DATE = os.environ['DATE']
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
fhr_list = os.environ['fhr_list'].split(', ')
hemisphere = os.environ['hemisphere']
grid = os.environ['grid']
DATA = os.environ['DATA']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
RUN = os.environ['RUN']

# Set date info
DATE_start_dt = datetime.datetime.strptime(DATE+valid_hr_start, '%Y%m%d%H')
DATE_end_dt = datetime.datetime.strptime(DATE+valid_hr_end, '%Y%m%d%H')
DATEm1_end_dt = DATE_end_dt - datetime.timedelta(days=1)

# Set hemisphere info
if hemisphere == 'nh':
    #bounding_lat = 30.98
    bounding_lat = 50.0
    VX_MASK = 'ARCTIC'
    OBS_LAT = '85.0'
    OBS_LON = '90.0'
elif hemisphere == 'sh':
    #bounding_lat = -39.23
    bounding_lat = -50.0
    VX_MASK = 'ANTARCTIC'
    OBS_LAT = '-85.0'
    OBS_LON = '90.0'

# Build MPR data
mpr_data = []

# Static variables
MODEL = MODEL
DESC = grid
FCST_VALID_BEG = DATE_start_dt.strftime('%Y%m%d_%H%M%S')
FCST_VALID_END = DATE_end_dt.strftime('%Y%m%d_%H%M%S')
OBS_LEAD = '000000'
OBS_VALID_BEG = FCST_VALID_BEG
OBS_VALID_END = FCST_VALID_END
FCST_VAR = 'ICEEX_DAILYAVG'
FCST_UNITS = '10^6_km^2'
FCST_LEV = 'Z0'
OBS_VAR = 'ICEEX_DAILYAVG'
OBS_UNITS = '10^6_km^2'
OBS_LEV = 'Z0'
OBTYPE = 'osi_saf'
INTERP_MTHD = 'NEAREST'
INTERP_PNTS = '1'
FCST_THRESH = 'NA'
OBS_THRESH = 'NA'
COV_THRESH = 'NA'
ALPHA = 'NA'
LINE_TYPE = 'MPR'
TOTAL = '1'
INDEX = '1'
OBS_SID = VX_MASK
OBS_LVL = 'NA'
OBS_ELV = '0'
OBS_QC = 'NA'
CLIMO_MEAN = 'NA'
CLIMO_STDEV = 'NA'
CLIMO_CDF = 'NA'

# Calculate observation sea-ice extent
obs_file = os.path.join(DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
                        RUN+'.'+DATE_end_dt.strftime('%Y%m%d'), 'osi_saf',
                        VERIF_CASE, 'regrid_data_plane_sea_ice_'
                        +'DailyAvg_Concentration'+hemisphere.upper()+'_valid'
                        +DATEm1_end_dt.strftime('%Y%m%d%H')
                        +'to'+DATE_end_dt.strftime('%Y%m%d%H')+'.nc')
if gda_util.check_file_exists_size(obs_file):
    obs = netcdf.Dataset(obs_file, 'r')
    obs_lat_in = obs.variables['lat'][:]
    obs_lon_in = obs.variables['lon'][:]
    obs_ICEC = obs.variables['ice_conc'][:]
    if obs_lat_in.ndim == 1 and obs_lon_in.ndim == 1:
        obs_lon, obs_lat = np.meshgrid(obs_lon_in, obs_lat_in)
    else:
        obs_lon = obs_lon_in
        obs_lat = obs_lat_in
    if hemisphere == 'nh':
        obs_lat_masked = np.ma.masked_invalid(
            np.where(obs_lat>=bounding_lat, obs_lat, np.nan)
        )
    elif hemisphere == 'sh':
        obs_lat_masked = np.ma.masked_invalid(
            np.where(obs_lat<=bounding_lat, obs_lat, np.nan)
        )
    drop_idx_list = []
    for r in range(len(obs_lat_masked[:,0])):
        if obs_lat_masked[r,:].mask.all():
            drop_idx_list.append(r)
    obs_lat = np.delete(obs_lat, drop_idx_list, axis=0)
    obs_lon = np.delete(obs_lon, drop_idx_list, axis=0)
    obs_ice = np.delete(obs_ICEC, drop_idx_list, axis=0)
    obs_ice = np.ma.masked_greater(
        np.ma.masked_less(np.ma.masked_invalid(obs_ice),15)
    ,100)
    obs_extent, obs_area, obs_surface_area = (
        iceArea(obs_lon, obs_lat, obs_ice)
    )
    OBS = str(obs_extent/1e6)
else:
    print("NOTE: Using NA for obs")
    OBS = 'NA'

# Calculate observation sea-ice extent
for fcst_lead in fhr_list:
    FCST_LEAD = fcst_lead.zfill(2)+'0000'
    initDATE_dt = DATE_end_dt - datetime.timedelta(hours=int(fcst_lead))
    fcst_file = os.path.join(DATA, VERIF_CASE+'_'+STEP, 'METplus_output',
                             RUN+'.'+DATE_end_dt.strftime('%Y%m%d'),
                             MODEL, VERIF_CASE, 'daily_avg_sea_ice_DailyAvg_'
                             +'Concentration'+hemisphere.upper()+'_init'
                             +initDATE_dt.strftime('%Y%m%d%H')+'_'
                             +'valid'+DATEm1_end_dt.strftime('%Y%m%d%H')
                             +'to'+DATE_end_dt.strftime('%Y%m%d%H')+'.nc')
    if gda_util.check_file_exists_size(fcst_file):
        fcst = netcdf.Dataset(fcst_file, 'r')
        fcst_lat_in = fcst.variables['lat'][:]
        fcst_lon_in = fcst.variables['lon'][:]
        fcst_ICEC = fcst.variables['FCST_ICEC_Z0_DAILYAVG'][:] * 100
        if fcst_lat_in.ndim == 1 and fcst_lon_in.ndim == 1:
            fcst_lon, fcst_lat = np.meshgrid(fcst_lon_in, fcst_lat_in)
        else:
            fcst_lon = fcst_lon_in
            fcst_lat = fcst_lat_in
        if hemisphere == 'nh':
            fcst_lat_masked = np.ma.masked_invalid(
                np.where(fcst_lat>=bounding_lat, fcst_lat, np.nan)
            )
        elif hemisphere == 'sh':
            fcst_lat_masked = np.ma.masked_invalid(
                np.where(fcst_lat<=bounding_lat, fcst_lat, np.nan)
            )
        drop_idx_list = []
        for r in range(len(fcst_lat_masked[:,0])):
            if fcst_lat_masked[r,:].mask.all():
                drop_idx_list.append(r)
        fcst_lat = np.delete(fcst_lat, drop_idx_list, axis=0)
        fcst_lon = np.delete(fcst_lon, drop_idx_list, axis=0)
        fcst_ice = np.delete(fcst_ICEC, drop_idx_list, axis=0)
        fcst_ice = np.ma.masked_greater(
            np.ma.masked_less(np.ma.masked_invalid(fcst_ice),15)
        ,100)
        fcst_extent, fcst_area, fcst_surface_area = (
            iceArea(fcst_lon, fcst_lat, fcst_ice)
        )
        FCST = str(fcst_extent/1e6)
    else:
        print("NOTE: Using NA for forecast")
        FCST = 'NA'
    mpr_data.append(
        [MODEL, DESC, FCST_LEAD, FCST_VALID_BEG, FCST_VALID_END,
         OBS_LEAD, OBS_VALID_BEG, OBS_VALID_END, FCST_VAR,
         FCST_UNITS, FCST_LEV, OBS_VAR, OBS_UNITS, OBS_LEV, OBTYPE,
         VX_MASK, INTERP_MTHD, INTERP_PNTS, FCST_THRESH, OBS_THRESH,
         COV_THRESH, ALPHA, LINE_TYPE, TOTAL, INDEX, OBS_SID, OBS_LAT,
         OBS_LON, OBS_LVL, OBS_ELV, FCST, OBS, OBS_QC, CLIMO_MEAN,
         CLIMO_STDEV, CLIMO_CDF]
    )

print("Data Length:\t" + repr(len(mpr_data)))
print("Data Type:\t" + repr(type(mpr_data)))
