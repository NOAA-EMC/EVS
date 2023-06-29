#!/usr/bin/env python3

###############################################################################
# Name of Script: evs_stats_check_otlk.py
# Contact(s):     Logan C. Dawson (logan.dawson@noaa.gov)
# Purpose of Script: Check for existence of SPC outlook masks based
#                    on valid date/time. Output is text file written to $DATA
#
# History Log:
#   4/2023: Initial script assembled  
###############################################################################

import datetime
import os, glob


FIX_DIR = os.environ['FIXevs'] 
OTLK_DIR = os.environ['COMINspcotlk']
WORK_DIR = os.environ['DATA']

verif_case = os.environ['VERIF_CASE']
vx_grid = os.environ['VERIF_GRID']
add_conus_regions = os.environ['ADD_CONUS_REGIONS']
add_conus_subregions = os.environ['ADD_CONUS_SUBREGIONS']

vday = os.environ['VDATE'] 

if verif_case == 'severe':
    vhr = '12'
else:
    vhr = os.environ['cyc']

YYYY = int(vday[0:4])
MM   = int(vday[4:6])
DD   = int(vday[6:8])
HH   = int(vhr)

valid_time = datetime.datetime(YYYY,MM,DD,HH,0,0)



# Define initial mask_str to include CONUS Bukovsky mask on correct vx_grid
mask_str = FIX_DIR+'/masks/Bukovsky_'+vx_grid+'_CONUS.nc'


# Write updated mask list to a file for reading later
with open(WORK_DIR+'/mask_list','wt') as outfile:
    outfile.write(mask_str)


conus_regions = ['CONUS_East','CONUS_West','CONUS_Central','CONUS_South']
conus_subregions = ['Appalachia','CPlains','DeepSouth','GreatBasin',
                    'GreatLakes','Mezquital','MidAtlantic','NorthAtlantic',
                    'NPlains','NRockies','PacificNW','PacificSW','Prairie',
                    'Southeast','Southwest','SPlains','SRockies']


if add_conus_regions == 'True':
    for vx_mask in conus_regions:
        mask_str = mask_str + ','+FIX_DIR+'/masks/Bukovsky_'+vx_grid+'_'+vx_mask+'.nc' 

if add_conus_subregions == 'True':
    for vx_mask in conus_subregions:
        mask_str = mask_str + ','+FIX_DIR+'/masks/Bukovsky_'+vx_grid+'_'+vx_mask+'.nc' 



# Define SPC outlook issuance time based on valid hour
valid_hour = int(valid_time.strftime('%H'))

if valid_hour <= 12:
    day1_obj = valid_time + datetime.timedelta(hours=-24)
    day2_obj = valid_time + datetime.timedelta(hours=-48)
    day3_obj = valid_time + datetime.timedelta(hours=-72)
elif valid_hour > 12:
    day1_obj = valid_time
    day2_obj = valid_time + datetime.timedelta(hours=-24)
    day3_obj = valid_time + datetime.timedelta(hours=-48)
    
day1_PDY = day1_obj.strftime('%Y%m%d')
day2_PDY = day2_obj.strftime('%Y%m%d')
day3_PDY = day3_obj.strftime('%Y%m%d')

issuance_times = [day1_PDY, day2_PDY, day3_PDY]


# Add SPC mask files to list if outlook(s) exists

for DAY in range(1,4):
    search_path = OTLK_DIR+'/spc_otlk.'+issuance_times[DAY-1]+'/spc_otlk.day'+str(DAY)+'*'+vx_grid+'.nc'
    file_list = [f for f in glob.glob(search_path)]

    for mask in file_list:
        mask_str = mask_str + ','+mask


# Write updated mask list to a file for reading later
with open(WORK_DIR+'/mask_list','wt') as outfile:
    outfile.write(mask_str)


exit()
