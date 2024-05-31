#! /usr/bin/env python3

'''
Name: global_ens_sea_ice_prep.py
Contact(s): Mallory Row
Abstract: 
'''

import os
import datetime
import glob
import shutil
import global_ens_atmos_util as gda_util
import sys

print("BEGIN: "+os.path.basename(__file__))

cwd = os.getcwd()
print("Working in: "+cwd)

# Read in common environment variables
DATA = os.environ['DATA']
DCOMINosi_saf = os.environ['DCOMINosi_saf']
COMOUT = os.environ['COMOUT']
INITDATE = os.environ['INITDATE']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
OBSNAME = os.environ['OBSNAME'].split(' ')

# Make COMOUT directory for dates
COMOUT_INITDATE = COMOUT+'/'+RUN+'.'+INITDATE
if not os.path.exists(COMOUT_INITDATE):
    os.makedirs(COMOUT_INITDATE)

###### OBS
# Get operational observation data
# Nortnern & Southern Hemisphere 10 km OSI-SAF multi-sensor analysis - osi_saf
global_det_obs_dict = {
    'osi_saf': {'daily_prod_file_format': os.path.join(DCOMINosi_saf,
                                                       '{init_shift?fmt=%Y%m%d'
                                                       +'?shift=-12}',
                                                       'seaice', 'osisaf',
                                                       'ice_conc_{hem?fmt=str}_'
                                                       +'polstere-100_multi_'
                                                       +'{init_shift?fmt=%Y%m%d%H'
                                                       +'?shift=-12}'
                                                       +'00.nc'),
                'daily_arch_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                                       'osi_saf',
                                                       'osi_saf.multi.'
                                                       +'{init_shift?fmt=%Y%m%d%H'
                                                       +'?shift=-24}to'
                                                       +'{init?fmt=%Y%m%d%H}'
                                                       +'_G004.nc'),
                'weekly_arch_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                                       'osi_saf',
                                                       'osi_saf.multi.'
                                                       +'{init_shift?fmt=%Y%m%d%H?'
                                                       +'shift=-168}'
                                                       +'to'
                                                       +'{init?fmt=%Y%m%d%H}'
                                                       +'_G004.nc'),
                'inithours': ['00']},
}

for OBS in OBSNAME:
    if OBS not in list(global_det_obs_dict.keys()):
        print("FATAL ERROR: "+OBS+" not a recognized observation dataset.")
        sys.exit(1)
    print("---- Prepping data for "+OBS+" for init "+INITDATE)
    obs_dict = global_det_obs_dict[OBS]
    for inithour in obs_dict['inithours']:
        CDATE = INITDATE+inithour
        CDATE_dt = datetime.datetime.strptime(CDATE, '%Y%m%d%H')
        if OBS == 'osi_saf':
            CDATEm7_dt = CDATE_dt + datetime.timedelta(hours=-168)
            daily_prod_file = gda_util.format_filler(
                obs_dict['daily_prod_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            daily_arch_file = gda_util.format_filler(
                obs_dict['daily_arch_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            weekly_arch_file = gda_util.format_filler(
                obs_dict['weekly_arch_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            daily_COMOUT_file = os.path.join(
                COMOUT_INITDATE, OBS, daily_arch_file.rpartition('/')[2]
            )
            daily_COMOUT_file_format = os.path.join(
                COMOUT+'.{init?fmt=%Y%m%d}', OBS,
                obs_dict['daily_arch_file_format'].rpartition('/')[2]
            )
            if not os.path.exists(daily_COMOUT_file) \
                    and not os.path.exists(daily_arch_file):
                arch_file_dir = daily_arch_file.rpartition('/')[0]
                if not os.path.exists(arch_file_dir):
                    os.makedirs(arch_file_dir)
                print("----> Trying to create "+daily_arch_file+" and "
                      +weekly_arch_file)
                weekly_file_list = [daily_arch_file]
                CDATEm_dt = CDATE_dt - datetime.timedelta(hours=24)
                while CDATEm_dt > CDATEm7_dt:
                    CDATEm_arch_file = gda_util.format_filler(
                        daily_COMOUT_file_format, CDATEm_dt, CDATEm_dt,
                        'anl', {}
                    )
                    weekly_file_list.append(CDATEm_arch_file)
                    CDATEm_dt = CDATEm_dt - datetime.timedelta(hours=24)
                gda_util.prep_prod_osi_saf_file(
                    daily_prod_file, daily_arch_file,
                    weekly_file_list, weekly_arch_file, (CDATEm7_dt,CDATE_dt)
                )

print("END: "+os.path.basename(__file__))
