#!/usr/bin/env python3

###############################################################################
# Name of Script: evs_prep_spc_otlk.py
# Contact(s):     Marcel Caron (marcel.caron@noaa.gov)
#                 Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: Copy and unzip SPC outlook shapefiles on a daily basis
#                    and run METplus to generate VX_MASK regions
#
# History Log:
#   1/2023: Initial script assembled
#   4/2023: Script modified to generate masks on a daily basis
###############################################################################

import sys, os, shutil, subprocess
import datetime
import re, csv, glob
import bisect
import numpy as np
import cam_util as cutil


OTLK_DATE = os.environ['OTLK_DATE'] 
vhr = os.environ['vhr']

YYYY = int(OTLK_DATE[0:4])
MM   = int(OTLK_DATE[4:6])
DD   = int(OTLK_DATE[6:8])
HH   = 12

day1_datetime = datetime.datetime(YYYY,MM,DD,HH,0,0)
day2_datetime = day1_datetime + datetime.timedelta(days=1)
day3_datetime = day1_datetime + datetime.timedelta(days=2)
day4_datetime = day1_datetime + datetime.timedelta(days=3)



SPC_PROD_DIR = os.environ['DCOMINspc']+'/'+OTLK_DATE+'/validation_data/weather/spc'


VERIF_GRIDS = ['G211','G221','G227','3km']
CATS = ['TSTM','MRGL','SLGT','ENH','MDT','HIGH']

for DAY in range(1,4):

    # Set up temporary working directory
    OTLK_DIR = os.environ['DATA']+'/day'+f'{DAY}'+'otlk'
    os.environ['OTLK_DIR'] = OTLK_DIR
    if not os.path.exists(OTLK_DIR):
        os.makedirs(OTLK_DIR)
    os.chdir(OTLK_DIR)

    search_path = SPC_PROD_DIR+'/day'+f'{DAY}'+'otlk_'+OTLK_DATE+'*-shp.zip'
    file_list = [f for f in glob.glob(search_path)]
    print(file_list)

    if len(file_list) > 0:

        if DAY == 1:
            OTLK = '1200'
            V1DATE = day1_datetime.strftime('%Y%m%d%H') 
            V2DATE = day2_datetime.strftime('%Y%m%d%H') 

        elif DAY == 2:
            OTLK = '1730'
            V1DATE = day2_datetime.strftime('%Y%m%d%H') 
            V2DATE = day3_datetime.strftime('%Y%m%d%H') 

        elif DAY == 3:
            V1DATE = day3_datetime.strftime('%Y%m%d%H') 
            V2DATE = day4_datetime.strftime('%Y%m%d%H') 

            if '_0730-' in file_list[0]:
                OTLK = '0730'
            elif '_0830-' in file_list[0]:
                OTLK = '0830'
            os.environ['DAY3_OTLK'] = OTLK

        print(f'Copying and unzipping SPC Day {DAY} Outlook issued at {OTLK}Z {OTLK_DATE}')

        for fil in file_list:

            # Copy and unzip file
            filename=fil[-30:]
            os.system('cp '+SPC_PROD_DIR+'/'+filename+' '+OTLK_DIR+'/'+filename)
            os.system('unzip '+OTLK_DIR+'/'+filename)
    
            SHP_FILE = f'day{DAY}otlk_{OTLK_DATE}_{OTLK}_cat' 
            os.environ['SHP_FILE'] = SHP_FILE

            # Check the number of records in the shapefile
            if os.path.isfile(os.path.join(OTLK_DIR,f'{SHP_FILE}.dbf')):
                N_REC = cutil.run_shell_command([
                        'gis_dump_dbf', 
                        os.path.join(OTLK_DIR,f'{SHP_FILE}.dbf'), 
                        '|', 'grep', 'n_records', 
                        '|', 'cut', '-d\'=\'', '-f2', 
                        '|', 'tr', '-d', '\' \''], 
                        capture_output=True)
            else:
                N_REC = 0

            # Process each record in the shapefile 
            if int(N_REC) > 0:
                print(f'Processing {N_REC} records.')
                for REC in np.arange(int(N_REC)):
                    for VERIF_GRID in VERIF_GRIDS:
 
                        NAME = cutil.run_shell_command([
                               'gis_dump_dbf', 
                               os.path.join(OTLK_DIR,f'{SHP_FILE}.dbf'),
                               '|', 'egrep', '-A', '5', f'"^Record {REC}"',
                               '|', 'tail','-1',
                               '|', 'cut', '-d\'"\'', '-f2'],
                               capture_output=True)
                        NAME = NAME.replace('\n','')
                        regexp="^[^:. ()]*$"
                        if not re.match(regexp, NAME):
                            print(f'NOTE: Record name ({NAME}) '
                                  + f'indicates no outlooks for Day {DAY} '
                                  + f'were issued at {OTLK}Z on {OTLK_DATE}.'
                                  + f' Check the spc dbf file for more info:'
                                  + f'{OTLK_DIR}/{SHP_FILE}.dbf')
                            continue
                        
                        print(f'Processing Record Number #{REC}: {NAME}')
                        
                        if DAY == 3:
                            MASK_FNAME = f'spc_otlk.day{DAY}_{NAME}.v{V1DATE}-{V2DATE}.{VERIF_GRID}'
                            MASK_NAME = f"DAY{DAY}_{NAME}"
                        else:
                            MASK_FNAME = f'spc_otlk.day{DAY}_{OTLK}_{NAME}.v{V1DATE}-{V2DATE}.{VERIF_GRID}'
                            MASK_NAME = f"DAY{DAY}_{OTLK}_{NAME}"

                        os.environ['VERIF_GRID'] = VERIF_GRID
                        os.environ['REC'] = str(REC)
                        os.environ['MASK_FNAME'] = MASK_FNAME
                        os.environ['MASK_NAME'] = MASK_NAME

                        cutil.run_shell_command([
                        os.path.join(os.environ['METPLUS_PATH'],'ush','run_metplus.py'), '-c',
                        os.path.join(os.environ['PARMevs'],'metplus_config','machine.conf'),
                        os.path.join(os.environ['PARMevs'],'metplus_config',
                                     'prep/cam/severe','GenVxMask_SPC_OTLK.conf')])

            else:
                print(f'No Day {DAY} outlook areas were issued at {OTLK}Z on {OTLK_DATE}')
                continue


exit()

