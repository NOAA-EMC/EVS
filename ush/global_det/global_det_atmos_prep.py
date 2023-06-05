#!/usr/bin/env python3
'''
Name: global_det_atmos_prep.py
Contact(s): Mallory Row
Abstract: 
'''

import os
import datetime
import glob
import shutil
import global_det_atmos_util as gda_util
import sys

print("BEGIN: "+os.path.basename(__file__))

cwd = os.getcwd()
print("Working in: "+cwd)

# Read in common environment variables
DATA = os.environ['DATA']
COMINcfs = os.environ['COMINcfs']
COMINcmc = os.environ['COMINcmc']
COMINcmc_precip = os.environ['COMINcmc_precip']
COMINcmc_regional_precip = os.environ['COMINcmc_regional_precip']
COMINdwd_precip = os.environ['COMINdwd_precip']
COMINecmwf = os.environ['COMINecmwf']
COMINecmwf_precip = os.environ['COMINecmwf_precip']
COMINfnmoc = os.environ['COMINfnmoc']
COMINimd = os.environ['COMINimd']
COMINjma = os.environ['COMINjma']
COMINjma_precip = os.environ['COMINjma_precip']
COMINmetfra_precip = os.environ['COMINmetfra_precip']
COMINukmet = os.environ['COMINukmet']
COMINukmet_precip = os.environ['COMINukmet_precip']
COMINosi_saf = os.environ['COMINosi_saf']
COMINghrsst_ospo = os.environ['COMINghrsst_ospo']
COMINget_d = os.environ['COMINget_d']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']
INITDATE = os.environ['INITDATE']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
MODELNAME = os.environ['MODELNAME'].split(' ')
OBSNAME = os.environ['OBSNAME'].split(' ')

# Make COMOUT directory for dates
COMOUT_INITDATE = COMOUT+'.'+INITDATE
if not os.path.exists(COMOUT_INITDATE):
    os.makedirs(COMOUT_INITDATE)

###### MODELS
# Get operational global deterministic model data
# Climate Forecast System - cfs
# Japan Meteorological Agency - jma
# European Centre for Medium-Range Weather Forecasts - ecmwf
# Met Office (UK) - ukmet
# National Centre for Medium Range Weather Forecasting (India) - imd
# Canadian Meteorological Centre - cmc
# Fleet Numerical Meteorology and Oceanography Center (US Navy) - fnmoc
# Climate Forecast System - cfs
# Canadian Meteorological Centre - Regional - cmc_regional
# Deutscher Wetterdienst (German) - dwd
# Météo-France - metfra

global_det_model_dict = {
    'cfs': {'COMIN_fcst_file_format': os.path.join(COMINcfs,
                                                  '{init?fmt=%H}',
                                                  '6hrly_grib_01',
                                                  'pgbf{valid?fmt=%Y%m%d%H}.01'
                                                  +'.{init?fmt=%Y%m%d%H}'
                                                  +'.grb2'),
            'cycles': ['00', '06', '12', '18'],
            'fcst_hrs': range(0, 384+6, 6)},
    'cmc': {'COMIN_fcst_file_format': os.path.join(COMINcmc,
                                                   'cmc_{init?fmt=%Y%m%d%H}'
                                                   +'f{lead?fmt=%3H}'),
            'COMIN_anl_file_format': os.path.join(COMINcmc,
                                                  'cmc_{init?fmt=%Y%m%d%H}'
                                                  +'f000'),
            'COMIN_precip_file_format': os.path.join(COMINcmc_precip,
                                                     'cmcglb_'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'{lead_shift?fmt=%3H?'
                                                     +'shift=-24}_'
                                                     +'{lead?fmt=%3H}.grb2'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 240+6, 6)},
    'cmc_regional': {'COMIN_precip_file_format': os.path.join(COMINcmc_regional_precip,
                                                              'cmc_'
                                                              +'{init?fmt=%Y%m%d%H}_'
                                                              +'{lead_shift?fmt=%3H?'
                                                              +'shift=-24}_'
                                                              +'{lead?fmt=%3H}'),
                     'cycles': ['00', '12'],
                     'fcst_hrs': range(24, 48+12, 12)},
    'dwd': {'COMIN_precip_file_format': os.path.join(COMINdwd_precip, 'dwd_'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'{lead_shift?fmt=%3H?'
                                                     +'shift=-24}_'
                                                     +'{lead?fmt=%3H}'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(24, 72+12, 12)},
    'ecmwf': {'COMIN_fcst_file_format': os.path.join(COMINecmwf,
                                                     'U1D{init?fmt=%m%d%H}00'
                                                     +'{valid?fmt=%m%d%H}001'),
              'COMIN_anl_file_format': os.path.join(COMINecmwf,
                                                    'U1D{init?fmt=%m%d%H}00'
                                                    +'{init?fmt=%m%d%H}011'),
              'COMIN_precip_file_format': os.path.join(COMINecmwf_precip,
                                                       'UWD{init?fmt=%Y%m%d%H%M}'
                                                       +'{valid?fmt=%m%d%H%M}1'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 240+6, 6)},
    'fnmoc': {'COMIN_fcst_file_format': os.path.join(COMINfnmoc,
                                                     'US058GMET-OPSbd2.NAVGEM'
                                                     +'{lead?fmt=%3H}-'
                                                     +'{init?fmt=%Y%m%d%H}-'
                                                     +'NOAA-halfdeg.gr2'),
              'COMIN_anl_file_format': os.path.join(COMINfnmoc,
                                                    'US058GMET-OPSbd2.NAVGEM'
                                                    +'000-'
                                                    +'{init?fmt=%Y%m%d%H}-'
                                                    +'NOAA-halfdeg.gr2'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 180+6, 6)},
    'imd': {'COMIN_fcst_file_format': os.path.join(COMINimd,
                                                   'gdas1.t{init?fmt=%2H}z.'
                                                   +'grbf{lead?fmt=%2H}'),
            'COMIN_anl_file_format': os.path.join(COMINimd,
                                                  'gdas1.t{init?fmt=%2H}z.'
                                                  +'grbf00'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 240+6, 6)},
    'jma': {'COMIN_fcst_file_format': os.path.join(COMINjma,
                                                   'jma_{hem?fmt=str}'
                                                   +'_{init?fmt=%H}'),
            'COMIN_anl_file_format': os.path.join(COMINjma,
                                                  'jma_{hem?fmt=str}'
                                                  +'_{init?fmt=%H}'),
            'COMIN_precip_file_format': os.path.join(COMINjma_precip, 'jma_'
                                                     +'{init?fmt=%Y%m%d%H}00'
                                                     +'.grib'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 192+24, 24)},
    'metfra': {'COMIN_precip_file_format': os.path.join(COMINmetfra_precip,
                                                        'METFRA_'
                                                        +'{init?fmt=%H}_'
                                                        +'{init?fmt=%Y%m%d}'),
               'cycles': ['00', '12'],
               'fcst_hrs': range(24, 72+12, 12)},
    'ukmet': {'COMIN_fcst_file_format': os.path.join(COMINukmet,
                                                     'GAB{init?fmt=%2H}'
                                                     +'{letter?fmt=str}.GRB'),
              'COMIN_anl_file_format': os.path.join(COMINukmet,
                                                    'GAB{init?fmt=%2H}AAT.GRB'),
              'COMIN_precip_file_format': os.path.join(COMINukmet_precip, 'ukmo.'
                                                       +'{init?fmt=%Y%m%d%H}'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 144+6, 6)}
}

DATA_fcst_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                     '{model?fmt=%str}',
                                     '{model?fmt=%str}.t{init?fmt=%2H}z.'
                                     +'f{lead?fmt=%3H}')
DATA_anl_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                    '{model?fmt=%str}',
                                    '{model?fmt=%str}.t{init?fmt=%2H}z.anl')
DATA_precip_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                       '{model?fmt=%str}',
                                       '{model?fmt=%str}.precip.'
                                       +'t{init?fmt=%2H}z.'
                                       +'f{lead?fmt=%3H}')

for MODEL in MODELNAME:
    if MODEL not in list(global_det_model_dict.keys()):
        print("ERROR: "+MODEL+" not recongized")
        sys.exit(1)
    if MODEL == 'cmc_regional':
        max_precip_fhr = 48
    else:
        max_precip_fhr = 72
    print("---- Prepping data for "+MODEL+" for init "+INITDATE)
    model_dict = global_det_model_dict[MODEL]
    for cycle in model_dict['cycles']:
        CDATE = INITDATE+cycle
        CDATE_dt = datetime.datetime.strptime(CDATE, '%Y%m%d%H')
        # Forecast files
        if MODEL == 'jma' and cycle == '00':
            fcst_hrs = range(0, 72+24, 24)
        else:
            fcst_hrs = model_dict['fcst_hrs']
        for fcst_hr in fcst_hrs:
            VDATE_dt = CDATE_dt + datetime.timedelta(hours=int(fcst_hr))
            if 'COMIN_fcst_file_format' in list(model_dict.keys()):
                COMIN_fcst_file = gda_util.format_filler(
                    model_dict['COMIN_fcst_file_format'], VDATE_dt, CDATE_dt,
                    str(fcst_hr), {}
                )
                DATA_fcst_file = gda_util.format_filler(
                    DATA_fcst_file_format, VDATE_dt, CDATE_dt,
                    str(fcst_hr), {'model': MODEL}
                )
                COMOUT_fcst_file = os.path.join(
                    COMOUT_INITDATE, MODEL, DATA_fcst_file.rpartition('/')[2]
                )
                if not os.path.exists(COMOUT_fcst_file):
                    print("----> Trying to create "+DATA_fcst_file)
                    log_missing_file = os.path.join(
                        DATA, 'mail_missing_'+MODEL+'_fhr'
                        +str(fcst_hr).zfill(3)+'_init'
                        +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
                    )
                    DATA_fcst_file_dir = DATA_fcst_file.rpartition('/')[0]
                    if not os.path.exists(DATA_fcst_file_dir):
                        os.makedirs(DATA_fcst_file_dir)
                        if MODEL in ['ecmwf']:
                             gda_util.run_shell_command(['chmod', '750',
                                                         DATA_fcst_file_dir])
                             gda_util.run_shell_command(['chgrp', 'rstprod',
                                                         DATA_fcst_file_dir])
                    if MODEL == 'jma':
                        gda_util.prep_prod_jma_file(COMIN_fcst_file,
                                                    DATA_fcst_file,
                                                    CDATE_dt,
                                                    str(fcst_hr),
                                                    'full',
                                                    log_missing_file)
                    elif MODEL == 'ecmwf':
                        if fcst_hr == 0:
                            COMIN_fcst_file = COMIN_fcst_file[:-2]+'11'
                        gda_util.prep_prod_ecmwf_file(COMIN_fcst_file,
                                                      DATA_fcst_file,
                                                      CDATE_dt,
                                                      str(fcst_hr),
                                                      'full',
                                                      log_missing_file)
                    elif MODEL == 'ukmet':
                        gda_util.prep_prod_ukmet_file(COMIN_fcst_file,
                                                      DATA_fcst_file,
                                                      CDATE_dt,
                                                      str(fcst_hr),
                                                      'full',
                                                      log_missing_file)
                    elif MODEL == 'fnmoc':
                        gda_util.prep_prod_fnmoc_file(COMIN_fcst_file,
                                                      DATA_fcst_file,
                                                      CDATE_dt,
                                                      str(fcst_hr),
                                                      'full',
                                                      log_missing_file)
                    else:
                        gda_util.copy_file(COMIN_fcst_file, DATA_fcst_file)
                        if not os.path.exists(COMIN_fcst_file):
                            gda_util.log_missing_file_model(
                                log_missing_file, COMIN_fcst_file, MODEL,
                                CDATE_dt, str(fcst_hr).zfill(3)
                            )
                    if SENDCOM == 'YES':
                        gda_util.copy_file(DATA_fcst_file, COMOUT_fcst_file)
                else:
                    print(f"{COMOUT_fcst_file} exists")
            if 'COMIN_precip_file_format' in list(model_dict.keys()):
                COMIN_precip_file = gda_util.format_filler(
                    model_dict['COMIN_precip_file_format'], VDATE_dt,
                    CDATE_dt, str(fcst_hr), {}
                )
                DATA_precip_file = gda_util.format_filler(
                    DATA_precip_file_format, VDATE_dt,
                    CDATE_dt, str(fcst_hr), {'model': MODEL}
                )
                COMOUT_precip_file = os.path.join(
                    COMOUT_INITDATE, MODEL, DATA_precip_file.rpartition('/')[2]
                )
                if not os.path.exists(COMOUT_precip_file):
                    if fcst_hr >= 24 and VDATE_dt.strftime('%H') == '12' \
                            and fcst_hr <= max_precip_fhr \
                            and fcst_hr % 24 == 0:
                        print("----> Trying to create "+DATA_precip_file)
                        log_missing_file = os.path.join(
                            DATA, 'mail_missing_'+MODEL+'_fhr'
                            +str(fcst_hr).zfill(3)+'_init'
                            +CDATE_dt.strftime('%Y%m%d%H')+'_precip.sh'
                        )
                        DATA_precip_file_dir = (
                            DATA_precip_file.rpartition('/')[0]
                        )
                        if not os.path.exists(DATA_precip_file_dir):
                            os.makedirs(DATA_precip_file_dir)
                            if MODEL in ['ecmwf']:
                                 gda_util.run_shell_command(
                                     ['chmod', '750', DATA_precip_file_dir]
                                 )
                                 gda_util.run_shell_command(
                                     ['chgrp', 'rstprod',
                                       DATA_precip_file_dir]
                                 )
                        if MODEL == 'jma':
                            gda_util.prep_prod_jma_file(COMIN_precip_file,
                                                        DATA_precip_file,
                                                        CDATE_dt,
                                                        str(fcst_hr),
                                                        'precip',
                                                        log_missing_file)
                        elif MODEL == 'ecmwf':
                            if cycle == '12':
                                gda_util.prep_prod_ecmwf_file(COMIN_precip_file,
                                                              DATA_precip_file,
                                                              CDATE_dt,
                                                              str(fcst_hr),
                                                              'precip',
                                                              log_missing_file)
                        elif MODEL == 'ukmet':
                            gda_util.prep_prod_ukmet_file(COMIN_precip_file,
                                                          DATA_precip_file,
                                                          CDATE_dt,
                                                          str(fcst_hr),
                                                          'precip',
                                                           log_missing_file)
                        elif MODEL == 'fnmoc':
                            gda_util.prep_prod_fnmoc_file(COMIN_precip_file,
                                                          DATA_precip_file,
                                                          str(fcst_hr),
                                                          'precip',
                                                          log_missing_file)
                        elif MODEL == 'dwd':
                            gda_util.prep_prod_dwd_file(COMIN_precip_file,
                                                        DATA_precip_file,
                                                        CDATE_dt,
                                                        str(fcst_hr),
                                                        'precip',
                                                        log_missing_file)
                        elif MODEL == 'metfra':
                            gda_util.prep_prod_metfra_file(COMIN_precip_file,
                                                           DATA_precip_file,
                                                           CDATE_dt,
                                                           str(fcst_hr),
                                                           'precip',
                                                           log_missing_file)
                        else:
                            gda_util.copy_file(COMIN_precip_file,
                                               DATA_precip_file)
                            if not os.path.exists(COMIN_precip_file):
                                gda_util.log_missing_file_model(
                                    log_missing_file, COMIN_precip_file, MODEL,
                                    CDATE_dt, str(fcst_hr).zfill(3)
                                )
                        if SENDCOM == 'YES':
                            gda_util.copy_file(DATA_precip_file,
                                               COMOUT_precip_file)
                else:
                    print(f"{COMOUT_precip_file} exists")
        # Analysis file
        if 'COMIN_anl_file_format' in list(model_dict.keys()):
            COMIN_anl_file = gda_util.format_filler(
                model_dict['COMIN_anl_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            DATA_anl_file = gda_util.format_filler(
                DATA_anl_file_format, CDATE_dt, CDATE_dt,
                'anl', {'model': MODEL}
            )
            COMOUT_anl_file = os.path.join(
                COMOUT_INITDATE, MODEL, DATA_anl_file.rpartition('/')[2]
            )
            if not os.path.exists(COMOUT_anl_file):
                print("----> Trying to create "+DATA_anl_file)
                log_missing_file = os.path.join(
                        DATA, 'mail_missing_'+MODEL+'_anl_valid'
                        +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
                    )
                DATA_anl_file_dir = DATA_anl_file.rpartition('/')[0]
                if not os.path.exists(DATA_anl_file_dir):
                    os.makedirs(DATA_anl_file_dir)
                    if MODEL in ['ecmwf']:
                         gda_util.run_shell_command(['chmod', '750',
                                                     DATA_anl_file_dir])
                         gda_util.run_shell_command(['chgrp', 'rstprod',
                                                     DATA_anl_file_dir])
                if MODEL == 'jma':
                    gda_util.prep_prod_jma_file(COMIN_anl_file,
                                                DATA_anl_file,
                                                CDATE_dt,
                                                'anl',
                                                'full',
                                                log_missing_file)
                elif MODEL == 'ecmwf':
                    gda_util.prep_prod_ecmwf_file(COMIN_anl_file,
                                                  DATA_anl_file,
                                                  CDATE_dt,
                                                  'anl',
                                                  'full',
                                                  log_missing_file)
                elif MODEL == 'ukmet':
                    gda_util.prep_prod_ukmet_file(COMIN_anl_file,
                                                  DATA_anl_file,
                                                  CDATE_dt,
                                                  'anl',
                                                  'full',
                                                  log_missing_file)
                elif MODEL == 'fnmoc':
                    gda_util.prep_prod_fnmoc_file(COMIN_anl_file,
                                                  DATA_anl_file,
                                                  CDATE_dt,
                                                  'anl',
                                                  'full',
                                                  log_missing_file)
                else:
                    gda_util.copy_file(COMIN_anl_file, DATA_anl_file)
                    if not os.path.exists(COMIN_anl_file):
                        gda_util.log_missing_file_model(
                            log_missing_file, COMIN_anl_file, MODEL,
                            CDATE_dt, 'anl'
                        )
                if SENDCOM == 'YES':
                    gda_util.copy_file(DATA_anl_file, COMOUT_anl_file)
            else:
                print(f"{COMOUT_anl_file} exists")

###### OBS
# Get operational observation data
# Nortnern & Southern Hemisphere 10 km OSI-SAF multi-sensor analysis - osi_saf
global_det_obs_dict = {
    'osi_saf': {'COMIN_file_format': os.path.join(COMINosi_saf,
                                                  '{init_shift?fmt=%Y%m%d'
                                                  +'?shift=-12}',
                                                  'seaice', 'osisaf',
                                                  'ice_conc_{hem?fmt=str}_'
                                                  +'polstere-100_multi_'
                                                  +'{init_shift?fmt=%Y%m%d%H'
                                                  +'?shift=-12}00.nc'),
                'DATA_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                                 'osi_saf', 'osi_saf.multi.'
                                                 +'{hem?fmt=str}.'
                                                 +'{init_shift?fmt=%Y%m%d%H'
                                                 +'?shift=-24}to'
                                                 +'{init?fmt=%Y%m%d%H}.nc'),
                'cycles': ['00']},
    'ghrsst_ospo': {'COMIN_file_format': os.path.join(COMINghrsst_ospo,
                                                      '{init_shift?fmt=%Y%m%d'
                                                      +'?shift=-24}',
                                                      'validation_data', 'marine',
                                                      'ghrsst',
                                                      '{init_shift?fmt=%Y%m%d'
                                                      +'?shift=-24}_OSPO_L4_'
                                                      +'GHRSST.nc'),
                    'DATA_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                                     'ghrsst_ospo',
                                                     'ghrsst_ospo.'
                                                     +'{init_shift?fmt=%Y%m%d%H'
                                                     +'?shift=-24}to'
                                                     +'{init?fmt=%Y%m%d%H}.nc'),
                    'cycles': ['00']},
    'get_d': {'COMIN_file_format': os.path.join(COMINget_d, 'get_d',
                                                'GETDL3_DAL_CONUS_'
                                                +'{init?fmt=%Y%j}_1.0.nc'),
              'DATA_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                               'get_d', 'get_d.'
                                               '{init_shift?fmt=%Y%m%d%H'
                                               +'?shift=-24}to'
                                               '{init?fmt=%Y%m%d%H}.nc'),
              'cycles': ['00']},
}

for OBS in OBSNAME:
    if OBS not in list(global_det_obs_dict.keys()):
        print("ERROR: "+OBS+" not recongized")
        sys.exit(1)
    print("---- Prepping data for "+OBS+" for init "+INITDATE)
    obs_dict = global_det_obs_dict[OBS]
    for cycle in obs_dict['cycles']:
        CDATE = INITDATE+cycle
        CDATE_dt = datetime.datetime.strptime(CDATE, '%Y%m%d%H')
        COMIN_file = gda_util.format_filler(
            obs_dict['COMIN_file_format'], CDATE_dt, CDATE_dt,
            'anl', {}
        )
        DATA_file = gda_util.format_filler(
           obs_dict['DATA_file_format'], CDATE_dt, CDATE_dt,
           'anl', {}
        )
        COMOUT_file = os.path.join(
            COMOUT_INITDATE, OBS, DATA_file.rpartition('/')[2]
        )
        DATA_file_dir = DATA_file.rpartition('/')[0]
        if not os.path.exists(DATA_file_dir):
            os.makedirs(DATA_file_dir)
        log_missing_file = os.path.join(
            DATA, 'mail_missing_'+OBS+'_valid'
            +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
        )
        if OBS == 'osi_saf':
            for hem in ['nh', 'sh']:
                log_missing_file = os.path.join(
                    DATA, 'mail_missing_'+OBS+'_'+hem+'_valid'
                    +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
                )
                COMIN_hem_file = COMIN_file.replace('{hem?fmt=str}', hem)
                DATA_hem_file = DATA_file.replace('{hem?fmt=str}', hem)
                COMOUT_hem_file = COMOUT_file.replace('{hem?fmt=str}', hem)
                if not os.path.exists(COMOUT_hem_file):
                    print("----> Trying to create "+DATA_hem_file)
                    gda_util.prep_prod_osi_saf_file(
                        COMIN_hem_file, DATA_hem_file, CDATE_dt,
                        log_missing_file
                    )
                    if SENDCOM == 'YES':
                        gda_util.copy_file(DATA_hem_file, COMOUT_hem_file)
        elif OBS == 'ghrsst_ospo':
            log_missing_file = os.path.join(
                DATA, 'mail_missing_'+OBS+'_valid'
                +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
            )
            if not os.path.exists(COMOUT_file):
                print("----> Trying to create "+DATA_file)
                gda_util.prep_prod_ghrsst_ospo_file(
                    COMIN_file, DATA_file, CDATE_dt,
                    log_missing_file
                )
                if SENDCOM == 'YES':
                    gda_util.copy_file(DATA_file, COMOUT_file)
        elif OBS == 'get_d':
            log_missing_file = os.path.join(
                DATA, 'mail_missing_'+OBS+'_valid'
                +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
            )
            if not os.path.exists(COMOUT_file):
                print("----> Trying to create "+DATA_file)
                gda_util.prep_prod_get_d_file(
                    COMIN_file, DATA_file, CDATE_dt,
                    log_missing_file
                )
            if SENDCOM == 'YES':
                gda_util.copy_file(DATA_file, COMOUT_file)
        else:
            print(f"{COMOUT_file} exists")

print("END: "+os.path.basename(__file__))
