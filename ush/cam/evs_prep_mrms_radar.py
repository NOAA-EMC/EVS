#!/usr/bin/env python3
###############################################################################
# Name of Script: evs_prep_mrms_radar.py
# Contact(s):     Marcel G. Caron (marcel.caron@noaa.gov)
# Purpose of Script: Copy and unzip MRMS radar files that are closest to top of hour
# History Log:
#   2020:       Initial script assembled and run in dev
#   12/22/2022: Initial script modified to follow NCO standards
###############################################################################

import sys, os, shutil, subprocess
import datetime
import re, csv, glob
import bisect
import numpy as np


valid_date = os.environ['VDATE'] 
vhr = os.environ['vhr']

YYYY = int(valid_date[0:4])
MM   = int(valid_date[4:6])
DD   = int(valid_date[6:8])
HH   = int(vhr)

valid = datetime.datetime(YYYY,MM,DD,HH,0,0)


domains = ['conus','alaska']

for domain in domains:

    MRMS_PROD_DIR = os.environ['DCOMINmrms']+'/'+domain
    TMP_DIR = os.environ['DATA']+'/MRMS_'+domain+'_tmp'

    # Set up working directory
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)


    # Copy and unzip the following MRMS products
    if domain == 'conus':
        MRMS_PRODUCTS = ['MergedReflectivityQCComposite','SeamlessHSR','EchoTop']
    elif domain == 'alaska':
        MRMS_PRODUCTS = ['MergedReflectivityQCComposite']


    for MRMS_PRODUCT in MRMS_PRODUCTS:

        print('Copying and unzipping '+valid.strftime('%Y%m%d%H')+' MRMS '+MRMS_PRODUCT+' data')

        if MRMS_PRODUCT == 'MergedReflectivityQCComposite':
            level = '_00.50_'
        elif MRMS_PRODUCT == 'MergedReflectivityQComposite':
            level = '_00.50_'
        elif MRMS_PRODUCT == 'SeamlessHSR':
            level = '_00.00_'
        elif MRMS_PRODUCT == 'EchoTop':
            level = '_00.50_'
            input_file_head  = 'EchoTop_18'
            output_file_head = 'EchoTop18'

        if MRMS_PRODUCT != 'EchoTop':
            input_file_head  = MRMS_PRODUCT
            output_file_head = MRMS_PRODUCT


        # Sort list of files for each MRMS product
        search_path = MRMS_PROD_DIR+'/'+MRMS_PRODUCT+'/'+input_file_head+'*.gz'
        file_list = [f for f in glob.glob(search_path)]
        time_list = [file_list[x][-24:-9] for x in range(len(file_list))]
        int_list = [int(time_list[x][0:8]+time_list[x][9:15]) for x in range(len(time_list))]
        int_list.sort()
        datetime_list = [datetime.datetime.strptime(str(x),"%Y%m%d%H%M%S") for x in int_list]
 
        # Find the MRMS file closest to the valid time
        i = bisect.bisect_left(datetime_list,valid)
        closest_timestamp = min(datetime_list[max(0, i-1): i+2], key=lambda date: abs(valid - date))

        # Check to make sure closest file is within +/- 15 mins of top of the hour
        # Copy and rename the file for future ease
        difference = abs(closest_timestamp - valid)
        if difference.total_seconds() <= 900:

            filename1 = input_file_head+level+closest_timestamp.strftime('%Y%m%d-%H%M%S')+'.grib2.gz'
            filename2 = output_file_head+level+valid.strftime('%Y%m%d-%H')+'0000.grib2.gz'

            os.system('cp '+MRMS_PROD_DIR+'/'+MRMS_PRODUCT+'/'+filename1+' '+TMP_DIR+'/'+filename2)
            os.system('gunzip '+TMP_DIR+'/'+filename2)
        else:
            print('No '+MRMS_PRODUCT+' file found within 15 minutes of '+valid.strftime('%HZ %m/%d/%Y')+'. Skipping this time.')



exit()
