#!/usr/bin/env python3
# =============================================================================
#
# NAME: cam_stats_grid2obs_read_mping_point.py
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Read point data from raw mPING data files and convert them to 
#          MET-readable format
#
# =============================================================================

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

MET_PATH = os.environ['MET_PATH']
met_ver = os.environ['met_ver']
sys.path.insert(0, os.path.abspath( os.path.join(
    MET_PATH,f'share','met','python'
)))
from met_point_obs import convert_point_data

########################################################################

print("Python Script:\t" + repr(sys.argv[0]))

##
##  input file specified on the command line
##  load the data into the numpy array
##

if len(sys.argv) != 3:
    print(
        "ERROR: test_read_mping_point.py -> Must specify exactly two input "
        + "file."
    )
    sys.exit(1)

# Read the input file as the first argument
input_file1 = os.path.expandvars(sys.argv[1])
input_file2 = os.path.expandvars(sys.argv[2])
try:

    print("Input File 1:\t" + repr(input_file1))
    print("Input File 2:\t" + repr(input_file2))
    # Read and format the input 11-column observations:
    #   (1)  string:  Message_Type
    #   (2)  string:  Station_ID
    #   (3)  string:  Valid_Time(YYYYMMDD_HHMMSS)
    #   (4)  numeric: Lat(Deg North)
    #   (5)  numeric: Lon(Deg East)
    #   (6)  numeric: Elevation(msl)
    #   (7)  string:  Var_Name(or GRIB_Code)
    #   (8)  numeric: Level
    #   (9)  numeric: Height(msl or agl)
    #   (10) string:  QC_String
    #   (11) numeric: Observation_Value
    point_csv1 = pd.read_csv(
        input_file1, header=0, 
        names=['sid', 'vld', 'obs', 'lat', 'lon'], 
        dtype={'sid':'str', 'vld':'str'}
    )
    point_csv2 = pd.read_csv(
        input_file2, header=0, 
        names=['sid', 'vld', 'obs', 'lat', 'lon'], 
        dtype={'sid':'str', 'vld':'str'}
    )
    print("    point_data1: Data Length:\t" + repr(len(point_csv1.values.tolist())))
    print("    point_data1: Data Type:\t" + repr(type(point_csv1.values.tolist())))
    print("    point_data2: Data Length:\t" + repr(len(point_csv2.values.tolist())))
    print("    point_data2: Data Type:\t" + repr(type(point_csv2.values.tolist())))

    point_csv = pd.concat((point_csv1, point_csv2))

    point_data_t = point_csv.values.T

    sid_new = point_data_t[0]
    lat_new = point_data_t[3]
    lon_new = point_data_t[4]
    obs_new = point_data_t[2]
    vld = point_data_t[1]
    vld_new = [
        datetime.strptime(vld_i, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y%m%d_%H%M%S') 
        for vld_i in vld
    ]
    typ_new = ['MPING' for _ in point_data_t[0]]
    var_new = ['PTYPE' for _ in point_data_t[0]]
    hgt_new = [0. for _ in point_data_t[0]]
    elv_new = lvl_new = [-9999. for _ in point_data_t[0]]
    qc_new = ['NA' for _ in point_data_t[0]]

    point_data = np.array(
        [
            typ_new, sid_new, vld_new, lat_new, lon_new, elv_new, var_new, lvl_new, 
            hgt_new, qc_new, obs_new
        ], 
        dtype=object
    ).T.tolist()
    met_point_data = convert_point_data(point_data)
    print(" met_point_data: Data Type:\t" + repr(type(met_point_data)))
except NameError:
    print("Can't find the input file")
    sys.exit(1)

########################################################################
