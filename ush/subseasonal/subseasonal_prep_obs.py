#!/usr/bin/env python3
'''
Name: subseasonal_prep_obs.py
Contact(s): Shannon Shields
Abstract: This script is run by exevs_subseasonal_obs_prep.sh
          in scripts/prep/subseasonal. This script retrieves
          obs data for subseasonal prep step.
'''

import os
import datetime
import glob
import shutil
import subseasonal_util as sub_util
import sys

print("BEGIN: "+os.path.basename(__file__))

cwd = os.getcwd()
print("Working in: "+cwd)

# Read in common environment variables
DATA = os.environ['DATA']
COMINgfs = os.environ['COMINgfs']
DCOMINecmwf = os.environ['DCOMINecmwf']
DCOMINosi = os.environ['DCOMINosi']
DCOMINghrsst = os.environ['DCOMINghrsst']
DCOMINumd = os.environ['DCOMINumd']
COMINnam = os.environ['COMINnam']
COMINccpa = os.environ['COMINccpa']
COMOUT = os.environ['COMOUT']
SENDCOM = os.environ['SENDCOM']
INITDATE = os.environ['INITDATE']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
OBSNAME = os.environ['OBSNAME'].split(' ')

# Make COMOUT directory for dates
COMOUT_INITDATE = COMOUT+'.'+INITDATE
if not os.path.exists(COMOUT_INITDATE):
    os.makedirs(COMOUT_INITDATE)

###### OBS
# Get operational observation data
# Northern & Southern Hemisphere 10 km OSI-SAF multi-sensor analysis - osi_saf
subseasonal_obs_dict = {
    'gfs': {'prod_file_format': os.path.join(COMINgfs, 'gfs.'
                                             +'{init?fmt=%Y%m%d}',
                                             '{init?fmt=%2H}',
                                             'atmos', 'gfs.t{init?fmt=%2H}z'
                                             +'.pgrb2.1p00.anl'),
                      'arch_file_format': os.path.join(COMOUT_INITDATE,                                                              'gfs',
                                                       'gfs.'
                                                       +'{init?fmt=%Y%m%d%H}'
                                                       +'.anl'),
                      'vhours': ['00', '12']},
    'ecmwf': {'prod_file_format': os.path.join(DCOMINecmwf,
                                               '{init?fmt=%Y%m%d}',
                                               'wgrbbul',
                                               'ecmwf',
                                               'DCD{init?fmt=%m%d%H}00'
                                               +'{init?fmt=%m%d%H}001'),
                      'arch_file_format': os.path.join(COMOUT_INITDATE,                                                              'ecmwf',
                                                       'ecmwf.'
                                                       +'{init?fmt=%Y%m%d%H}'
                                                       +'.anl'),
                      'vhours': ['00', '12']},
    'osi': {'daily_prod_file_format': os.path.join(DCOMINosi,
                                                   '{init_shift?fmt=%Y%m%d'
                                                   +'?shift=-12}',
                                                   'seaice', 'osisaf',
                                                   'ice_conc_{hem?fmt=str}_'
                                                   +'polstere-100_multi_'
                                                   +'{init_shift?fmt=%Y%m%d%H'
                                                   +'?shift=-12}'
                                                   +'00.nc'),
                'daily_arch_file_format': os.path.join(COMOUT_INITDATE,
                                                       'osi_saf',
                                                       'osi_saf.multi.'
                                                       +'{init_shift?fmt=%Y%m%d%H'
                                                       +'?shift=-24}to'
                                                       +'{init?fmt=%Y%m%d%H}'
                                                       +'_G003.nc'),
                'vhours': ['00']},
    'ghrsst': {'daily_prod_file_format': os.path.join(DCOMINghrsst,
                                                      '{init_shift?fmt=%Y%m%d'
                                                      +'?shift=-24}',
                                                      'validation_data', 
                                                      'marine', 
                                                      'ghrsst',
                                                      '{init_shift?fmt=%Y%m%d'
                                                      +'?shift=-24}_'
                                                      +'OSPO_L4_'
                                                      +'GHRSST.nc'),
                      'daily_arch_file_format': os.path.join(COMOUT_INITDATE,
                                                             'ghrsst_ospo',
                                                             'ghrsst_ospo.'
                                                             +'{init_shift?fmt=%Y%m%d%H'
                                                             +'?shift=-24}to'
                                                             +'{init?fmt=%Y%m%d%H}'
                                                             +'.nc'),
                      'vhours': ['00']},
    'umd': {'prod_file_format': os.path.join(DCOMINumd, 
                                             '{init?fmt=%Y%m%d}',
                                             'validation_data',
                                             'landsfc',
                                             'olr',
                                             'olr-daily_'
                                             +'v01r02-preliminary_'
                                             +'{init?fmt=%Y}0101_'
                                             +'latest.nc'),
                      'arch_file_format': os.path.join(COMOUT_INITDATE,
                                                       'umd',
                                                       'umd.olr.'
                                                       '{init?fmt=%Y%m%d}.nc'),
                      'vhours': ['00']},

    'nam': {'arch_file_format': os.path.join(COMOUT_INITDATE,
                                             'prepbufr_nam',
                                             'prepbufr.nam.'
                                             +'{init?fmt=%Y%m%d%H}'),
                      'vhours': ['00', '12']},
    'ccpa': {'prod_file_format': os.path.join(COMINccpa, 'ccpa.'
                                              +'{init?fmt=%Y%m%d}',
                                              '{init?fmt=%2H}',
                                              'ccpa.t{init?fmt=%2H}z'
                                              +'.06h.1p0.conus.gb2'),
                      'arch_file_format': os.path.join(COMOUT_INITDATE,
                                                       'ccpa',
                                                       'pcp_combine_precip_'
                                                       +'accum24hr_24hrCCPA_'
                                                       +'{init?fmt=%Y%m%d}12'
                                                       +'.nc'),
                      'vhours': ['00', '06', '12', '18']},
}

for OBS in OBSNAME:
    if OBS not in list(subseasonal_obs_dict.keys()):
        print("FATAL ERROR: "+OBS+" not recognized")
        sys.exit(1)
    print("---- Prepping data for "+OBS+" for init "+INITDATE)
    obs_dict = subseasonal_obs_dict[OBS]
    for vhour in obs_dict['vhours']:
        CDATE = INITDATE+vhour
        CDATE_dt = datetime.datetime.strptime(CDATE, '%Y%m%d%H')
        log_missing_file = os.path.join(
            DATA, 'mail_missing_'+OBS+'_valid'
            +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
        )
        if vhour == '18':
            CDATEm1_dt = (CDATE_dt
                         + datetime.timedelta(hours=-24))
            log_missing_file = os.path.join(
                DATA, 'mail_missing_'+OBS+'_valid'
                +CDATEm1_dt.strftime('%Y%m%d%H')+'.sh'
            )
        if OBS == 'nam':
            offset_hr = str(int(CDATE_dt.strftime('%H'))%6
            ).zfill(2)
            offset_CDATE_dt = (
                CDATE_dt + datetime.timedelta(hours=int(offset_hr))
            )
            prod_file_format = os.path.join(COMINnam, 'nam.'
                                            +'{init?fmt=%Y%m%d}',
                                            'nam.t{init?fmt=%2H}z.'
                                            +'prepbufr.tm'+offset_hr)
            prod_file = sub_util.format_filler(
                prod_file_format, offset_CDATE_dt, 
                offset_CDATE_dt, 'anl', {}
            )
            arch_file = sub_util.format_filler(
                obs_dict['arch_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            COMOUT_file = os.path.join(
                COMOUT_INITDATE, OBS, arch_file.rpartition('/')[2]
            )
            if not os.path.exists(COMOUT_file) \
                    and not os.path.exists(arch_file):
                arch_file_dir = arch_file.rpartition('/')[0]
                if not os.path.exists(arch_file_dir):
                    os.makedirs(arch_file_dir)
                print("----> Trying to create "+arch_file)
                if SENDCOM == 'YES':
                    sub_util.copy_file(prod_file, arch_file)
                    if os.path.exists(arch_file):
                        sub_util.run_shell_command(
                            ['chmod', '640', arch_file]
                        )
                        sub_util.run_shell_command(
                            ['chgrp', 'rstprod', arch_file]
                        )
                if not os.path.exists(prod_file):
                    sub_util.log_missing_file_obs(
                        log_missing_file, prod_file, OBS,
                        CDATE_dt
                    )
        elif OBS == 'osi':
            daily_prod_file = sub_util.format_filler(
                obs_dict['daily_prod_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            daily_arch_file = sub_util.format_filler(
                obs_dict['daily_arch_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            daily_COMOUT_file = os.path.join(
                COMOUT_INITDATE, 'osi_saf', daily_arch_file.rpartition('/')[2]
            )
            daily_COMOUT_file_format = os.path.join(
                COMOUT+'.{init?fmt=%Y%m%d}', 'osi_saf',
                obs_dict['daily_arch_file_format'].rpartition('/')[2]
            )
            if not os.path.exists(daily_COMOUT_file) \
                    and not os.path.exists(daily_arch_file):
                arch_file_dir = daily_arch_file.rpartition('/')[0]
                if not os.path.exists(arch_file_dir):
                    os.makedirs(arch_file_dir)
                print("----> Trying to create "+daily_arch_file)
                if SENDCOM == 'YES':
                    sub_util.prep_prod_osi_saf_file(
                        daily_prod_file, daily_arch_file,
                        CDATE_dt, log_missing_file
                    )
        elif OBS == 'ghrsst':
            daily_prod_file = sub_util.format_filler(
                obs_dict['daily_prod_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            daily_arch_file = sub_util.format_filler(
                obs_dict['daily_arch_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            daily_COMOUT_file = os.path.join(
                COMOUT_INITDATE, 'ghrsst_ospo', 
                daily_arch_file.rpartition('/')[2]
            )
            daily_COMOUT_file_format = os.path.join(
                COMOUT+'.{init?fmt=%Y%m%d}', 'ghrsst_ospo',
                obs_dict['daily_arch_file_format'].rpartition('/')[2]
            )
            if not os.path.exists(daily_COMOUT_file) \
                    and not os.path.exists(daily_arch_file):
                arch_file_dir = daily_arch_file.rpartition('/')[0]
                if not os.path.exists(arch_file_dir):
                    os.makedirs(arch_file_dir)
                print("----> Trying to create "+daily_arch_file)
                if SENDCOM == 'YES':
                    sub_util.prep_prod_ghrsst_ospo_file(
                        daily_prod_file, daily_arch_file,
                        CDATE_dt, log_missing_file
                    )
        elif OBS == 'ccpa':
            ccpa_dir = os.path.join(
                DATA, STEP, 'data', 'ccpa'
            )
            if not os.path.exists(ccpa_dir):
                os.makedirs(ccpa_dir)
            ccpa_tmp_file_format = os.path.join(
                ccpa_dir,
                'ccpa.6H.{init?fmt=%Y%m%d%H}'
            )
            if vhour == '18':
                prod_file = sub_util.format_filler(
                    obs_dict['prod_file_format'], CDATEm1_dt,
                    CDATEm1_dt, 'anl', {}
                )
                tmp_file = sub_util.format_filler(
                    ccpa_tmp_file_format, CDATEm1_dt,
                    CDATEm1_dt, 'anl', {}
                )
            else:
                prod_file = sub_util.format_filler(
                    obs_dict['prod_file_format'], CDATE_dt,
                    CDATE_dt, 'anl', {}
                )
                tmp_file = sub_util.format_filler(
                    ccpa_tmp_file_format, CDATE_dt,
                    CDATE_dt, 'anl', {}
                )
            if os.path.exists(prod_file):
                sub_util.copy_file(prod_file, tmp_file)
            else:
                if vhour == '18':
                    sub_util.log_missing_file_obs(
                        log_missing_file, prod_file, OBS,
                        CDATEm1_dt
                    )
                else:
                    sub_util.log_missing_file_obs(
                        log_missing_file, prod_file, OBS,
                        CDATE_dt
                    )
        else:
            prod_file = sub_util.format_filler(
                obs_dict['prod_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            arch_file = sub_util.format_filler(
                obs_dict['arch_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            COMOUT_file = os.path.join(
                COMOUT_INITDATE, OBS, arch_file.rpartition('/')[2]
            )
            if not os.path.exists(COMOUT_file) \
                    and not os.path.exists(arch_file):
                arch_file_dir = arch_file.rpartition('/')[0]
                if not os.path.exists(arch_file_dir):
                    os.makedirs(arch_file_dir)
                print("----> Trying to create "+arch_file)
                if OBS == 'gfs':
                    if SENDCOM == 'YES':
                        sub_util.prep_prod_gfs_file(
                            prod_file, arch_file, CDATE_dt, log_missing_file)
                elif OBS == 'ecmwf':
                    if SENDCOM == 'YES':
                        sub_util.copy_file(prod_file, arch_file)
                        if os.path.exists(arch_file):
                            sub_util.run_shell_command(
                                ['chmod', '640', arch_file]
                            )
                            sub_util.run_shell_command(
                                ['chgrp', 'rstprod', arch_file]
                            )
                    if not os.path.exists(prod_file):
                        sub_util.log_missing_file_obs(
                            log_missing_file, prod_file, OBS,
                            CDATE_dt
                        )
                else:
                    if SENDCOM == 'YES':
                        sub_util.copy_file(prod_file, arch_file)
                    if not os.path.exists(prod_file):
                        sub_util.log_missing_file_obs(
                            log_missing_file, prod_file, OBS,
                            CDATE_dt
                        )
    if OBS == 'ccpa':
        all_ccpa_file_exist = sub_util.check_ccpa_prep_files(
            DATA, STEP, INITDATE)
        if all_ccpa_file_exist:
            working_dir_list = []
            working_output_base_dir = os.path.join(
                DATA, STEP, 'METplus_output')
            working_dir_list.append(working_output_base_dir)
            working_dir_list.append(
                os.path.join(working_output_base_dir,
                             'confs')
            )
            working_dir_list.append(
                os.path.join(working_output_base_dir,
                             'logs')
            )
            working_dir_list.append(
                os.path.join(working_output_base_dir,
                             'tmp')
            )
            working_dir_list.append(
                os.path.join(working_output_base_dir,
                             'stage')
            )
            # Create working output directories
            for working_output_dir in working_dir_list:
                if not os.path.exists(working_output_dir):
                    print("Creating working output directory: "+working_output_dir)
                    os.makedirs(working_output_dir, mode=0o755, exist_ok=True)
            metplus_cmd = sub_util.metplus_command(
                'PCPCombine_obs24hrCCPA.conf')
            EDATE = INITDATE+'12'
            EDATE_dt = datetime.datetime.strptime(EDATE, '%Y%m%d%H')
            SDATE_dt = EDATE_dt - datetime.timedelta(days=1)
            arch_file = sub_util.format_filler(
                obs_dict['arch_file_format'], EDATE_dt, EDATE_dt,
                'anl', {}
            )
            if not os.path.exists(arch_file):
                arch_file_dir = arch_file.rpartition('/')[0]
                if not os.path.exists(arch_file_dir):
                    os.makedirs(arch_file_dir)
                print("----> Trying to create "+arch_file)
            # Create file with environment variables and command to source
            env_var_dict = {}
            env_var_dict['STARTDATE'] = SDATE_dt.strftime('%Y%m%d%H')
            env_var_dict['ENDDATE'] = EDATE_dt.strftime('%Y%m%d%H')
            env_var_dict['pcp_arch_file'] = arch_file
            ccpa_file = os.path.join(DATA, STEP, 'metplus_precip.sh')
            file = open(ccpa_file, 'w')
            file.write('#!/bin/bash\n')
            file.write('set -x\n')
            file.write('\n')
            # Write environment variables
            for name, value in env_var_dict.items():
                file.write('export '+name+'='+'"'+value+'"\n')
            file.write('\n')
            # Write METplus command
            file.write(metplus_cmd+'\n')
            file.write('export err=$?; err_chk'+'\n')
            file.close()

print("END: "+os.path.basename(__file__))
