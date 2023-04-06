###############################################################################
# Name of Script: prep_spc_otlk_files.py
# Contact(s):     Logan Dawson
# Purpose of Script: Copy and unzip MRMS radar files that are closest to top of hour
#
# History Log:
#   2020:       Initial script assembled and run in dev
#   12/22/2022: Initial script modified to follow NCO standards
###############################################################################

import sys, os, shutil, subprocess
import datetime
import re, csv, glob
import bisect
import numpy as np
import cam_util as cutil


OTLK_DATE = os.environ['OTLK_DATE'] 
cyc = os.environ['cyc']

YYYY = int(OTLK_DATE[0:4])
MM   = int(OTLK_DATE[4:6])
DD   = int(OTLK_DATE[6:8])
HH   = 12

day1_datetime = datetime.datetime(YYYY,MM,DD,HH,0,0)
day2_datetime = day1_datetime + datetime.timedelta(days=1)
day3_datetime = day1_datetime + datetime.timedelta(days=2)
day4_datetime = day1_datetime + datetime.timedelta(days=3)



SPC_PROD_DIR = os.environ['COMINspc']+'/'+OTLK_DATE+'/validation_data/weather/spc'


VERIF_GRIDS = ['G104','G211','G221','G227','3km']
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

                    print(f'Processing Record Number #{REC}: {NAME}')

                    MASK_FNAME = f'spc_otlk.day{DAY}_{OTLK}_{NAME}.v{V1DATE}-{V2DATE}.{VERIF_GRID}'
                    if DAY == 3:
                        MASK_NAME = f"DAY{DAY}_{NAME}"
                    else:
                        MASK_NAME = f"DAY{DAY}_{OTLK}_{NAME}"

                    os.environ['VERIF_GRID'] = VERIF_GRID
                    os.environ['REC'] = str(REC)
                    os.environ['MASK_FNAME'] = MASK_FNAME
                    os.environ['MASK_NAME'] = MASK_NAME

                    cutil.run_shell_command([
                    os.path.join(os.environ['METPLUS_PATH'],'ush','run_metplus.py'), '-c',
                    os.path.join(os.environ['PARMevs'],'metplus_config','machine.conf'),
                    os.path.join(os.environ['PARMevs'],'metplus_config',
                                 'cam/severe/prep','GenVxMask_SPC_OTLK.conf')])

        else:
            print(f'No Day {DAY} outlook areas were issued at {OTLK}Z on {OTLK_DATE}')
            continue

exit()


'''
NAME=`gis_dump_dbf ${SHP_FILE}.dbf | egrep -A 5 "^Record ${REC}" | tail -1 | cut -d'"' -f2`

# Make sure output directory exists
 mkdir -p ${MASK_DIR}/${TOGRID}/SPC_outlooks

                      GRID_NAME=${GRID_DIR}/grid_files/${TOGRID}.nc
                          MASK_NAME=${SHP_FILE}_Rec${REC}_${NAME}_mask

                              if [[ ${DAY} == 3 ]]; then
                                     gen_vx_mask ${GRID_NAME} ${SHP_FILE}.shp ${MASK_NAME}.nc -type shape -shapeno ${REC} -name DAY${DAY}_${NAME} -v 3
                                         else
                                                gen_vx_mask ${GRID_NAME} ${SHP_FILE}.shp ${MASK_NAME}.nc -type shape -shapeno ${REC} -name DAY${DAY}_${OTLK}_${NAME} -v 3
                                                    fi

cp ${MASK_NAME}.nc ${MASK_DIR}/${TOGRID}/SPC_outlooks/${MASK_NAME}.nc
'''





domains = ['conus','alaska']

for domain in domains:

    TMP_DIR = os.environ['DATA']+'/MRMS_'+domain+'_tmp'



    # Copy and unzip the following MRMS products
    if domain == 'conus':
        MRMS_PRODUCTS = ['MergedReflectivityQCComposite','SeamlessHSR','EchoTop']
    elif domain == 'alaska':
      # MRMS_PRODUCTS = ['MergedReflectivityQCComposite']
        MRMS_PRODUCTS = ['MergedReflectivityQComposite']


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
