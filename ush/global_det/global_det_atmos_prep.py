#!/usr/bin/env python3
'''
Name: global_det_atmos_prep.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This does the prep work for global determinstic
          model files and observation files.
Run By: scripts/prep/global_det/exevs_global_det_atmos_prep.sh
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
COMINgfs = os.environ['COMINgfs']
DCOMINcmc_precip = os.environ['DCOMINcmc_precip']
DCOMINcmc_regional_precip = os.environ['DCOMINcmc_regional_precip']
DCOMINdwd_precip = os.environ['DCOMINdwd_precip']
DCOMINecmwf = os.environ['DCOMINecmwf']
DCOMINecmwf_precip = os.environ['DCOMINecmwf_precip']
DCOMINfnmoc = os.environ['DCOMINfnmoc']
DCOMINimd = os.environ['DCOMINimd']
DCOMINjma = os.environ['DCOMINjma']
DCOMINjma_precip = os.environ['DCOMINjma_precip']
DCOMINmetfra_precip = os.environ['DCOMINmetfra_precip']
DCOMINukmet = os.environ['DCOMINukmet']
DCOMINukmet_precip = os.environ['DCOMINukmet_precip']
DCOMINosi_saf = os.environ['DCOMINosi_saf']
DCOMINghrsst_ospo = os.environ['DCOMINghrsst_ospo']
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
output_INITDATE = COMOUT+'.'+INITDATE
gda_util.make_dir(output_INITDATE)

###### MODELS
# Get operational global deterministic model data
# Global Forecast System - gfs
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
# Met-France - metfra

global_det_model_dict = {
    'cfs': {'input_fcst_file_format': os.path.join(COMINcfs,
                                                  '{init?fmt=%H}',
                                                  '6hrly_grib_01',
                                                  'pgbf{valid?fmt=%Y%m%d%H}.01'
                                                  +'.{init?fmt=%Y%m%d%H}'
                                                  +'.grb2'),
            'inithours': ['00', '06', '12', '18'],
            'fcst_hrs': range(0, 384+6, 6)},
    'cmc': {'input_fcst_file_format': os.path.join(COMINcmc,
                                                   'cmc_{init?fmt=%Y%m%d%H}'
                                                   +'f{lead?fmt=%3H}'),
            'input_anl_file_format': os.path.join(COMINcmc,
                                                  'cmc_{init?fmt=%Y%m%d%H}'
                                                  +'f000'),
            'input_precip_file_format': os.path.join(DCOMINcmc_precip,
                                                     'cmcglb_'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'{lead_shift?fmt=%3H?'
                                                     +'shift=-24}_'
                                                     +'{lead?fmt=%3H}.grb2'),
            'inithours': ['00', '12'],
            'fcst_hrs': range(0, 240+6, 6)},
    'cmc_regional': {'input_precip_file_format': os.path.join(DCOMINcmc_regional_precip,
                                                              'cmc_'
                                                              +'{init?fmt=%Y%m%d%H}_'
                                                              +'{lead_shift?fmt=%3H?'
                                                              +'shift=-24}_'
                                                              +'{lead?fmt=%3H}'),
                     'inithours': ['00', '12'],
                     'fcst_hrs': range(24, 48+12, 12)},
    'dwd': {'input_precip_file_format': os.path.join(DCOMINdwd_precip, 'dwd_'
                                                     +'{init?fmt=%Y%m%d%H}_'
                                                     +'{lead_shift?fmt=%3H?'
                                                     +'shift=-24}_'
                                                     +'{lead?fmt=%3H}'),
            'inithours': ['00', '12'],
            'fcst_hrs': range(24, 72+12, 12)},
    'ecmwf': {'input_fcst_file_format': os.path.join(DCOMINecmwf,
                                                     'U1D{init?fmt=%m%d%H}00'
                                                     +'{valid?fmt=%m%d%H}001'),
              'input_anl_file_format': os.path.join(DCOMINecmwf,
                                                    'U1D{init?fmt=%m%d%H}00'
                                                    +'{init?fmt=%m%d%H}011'),
              'input_precip_file_format': os.path.join(DCOMINecmwf_precip,
                                                       'UWD{init?fmt=%Y%m%d%H%M}'
                                                       +'{valid?fmt=%m%d%H%M}1'),
              'inithours': ['00', '12'],
              'fcst_hrs': range(0, 240+6, 6)},
    'fnmoc': {'input_fcst_file_format': os.path.join(DCOMINfnmoc,
                                                     'US058GMET-OPSbd2.NAVGEM'
                                                     +'{lead?fmt=%3H}-'
                                                     +'{init?fmt=%Y%m%d%H}-'
                                                     +'NOAA-halfdeg.gr2'),
              'input_anl_file_format': os.path.join(DCOMINfnmoc,
                                                    'US058GMET-OPSbd2.NAVGEM'
                                                    +'000-'
                                                    +'{init?fmt=%Y%m%d%H}-'
                                                    +'NOAA-halfdeg.gr2'),
              'inithours': ['00', '12'],
              'fcst_hrs': range(0, 180+6, 6)},
    'gfs': {'input_wmo_file_format': os.path.join(COMINgfs, '{init?fmt=%2H}',
                                                  'atmos', 'gfs.'
                                                  +'t{init?fmt=%2H}z.master.'
                                                  +'grb2f{lead?fmt=%3H}'),
            'inithours': ['00', '12'],
            'fcst_hrs': list(range(0, 72+3, 3))
                        + list(range(78, 240+6, 6))},
    'imd': {'input_fcst_file_format': os.path.join(DCOMINimd,
                                                   'gdas1.t{init?fmt=%2H}z.'
                                                   +'grbf{lead?fmt=%2H}'),
            'input_anl_file_format': os.path.join(DCOMINimd,
                                                  'gdas1.t{init?fmt=%2H}z.'
                                                  +'grbf00'),
            'inithours': ['00', '12'],
            'fcst_hrs': range(0, 240+6, 6)},
    'jma': {'input_fcst_file_format': os.path.join(DCOMINjma,
                                                   'jma_{hem?fmt=str}'
                                                   +'_{init?fmt=%H}'),
            'input_anl_file_format': os.path.join(DCOMINjma,
                                                  'jma_{hem?fmt=str}'
                                                  +'_{init?fmt=%H}'),
            'input_precip_file_format': os.path.join(DCOMINjma_precip, 'jma_'
                                                     +'{init?fmt=%Y%m%d%H}00'
                                                     +'.grib'),
            'inithours': ['00', '12'],
            'fcst_hrs': range(0, 192+24, 24)},
    'metfra': {'input_precip_file_format': os.path.join(DCOMINmetfra_precip,
                                                        'METFRA_'
                                                        +'{init?fmt=%H}_'
                                                        +'{init?fmt=%Y%m%d}.gz'),
               'inithours': ['00', '12'],
               'fcst_hrs': range(24, 72+12, 12)},
    'ukmet': {'input_fcst_file_format': os.path.join(DCOMINukmet,
                                                     'GAB{init?fmt=%2H}'
                                                     +'{letter?fmt=str}.GRB'),
              'input_anl_file_format': os.path.join(DCOMINukmet,
                                                    'GAB{init?fmt=%2H}AAT.GRB'),
              #'input_precip_file_format': os.path.join(DCOMINukmet_precip, 'ukmo.'
              #                                         +'{init?fmt=%Y%m%d%H}'),
              'inithours': ['00', '12'],
              'fcst_hrs': range(0, 144+6, 6)}
}

tmp_fcst_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                    '{model?fmt=%str}',
                                    '{model?fmt=%str}.t{init?fmt=%2H}z.'
                                    +'f{lead?fmt=%3H}')
tmp_anl_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                   '{model?fmt=%str}',
                                   '{model?fmt=%str}.t{init?fmt=%2H}z.anl')
tmp_precip_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                      '{model?fmt=%str}',
                                      '{model?fmt=%str}.precip.'
                                      +'t{init?fmt=%2H}z.'
                                      +'f{lead?fmt=%3H}')
tmp_wmo_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                   '{model?fmt=%str}',
                                   '{model?fmt=%str}.wmo.'
                                   +'t{init?fmt=%2H}z.'
                                   +'f{lead?fmt=%3H}')

for MODEL in MODELNAME:
    if MODEL not in list(global_det_model_dict.keys()):
        print("FATAL ERROR: "+MODEL+" not recongized")
        sys.exit(1)
    if MODEL == 'cmc_regional':
        max_precip_fhr = 48
    else:
        max_precip_fhr = 72
    print("---- Prepping data for "+MODEL+" for init "+INITDATE)
    model_dict = global_det_model_dict[MODEL]
    for inithour in model_dict['inithours']:
        CDATE = INITDATE+inithour
        CDATE_dt = datetime.datetime.strptime(CDATE, '%Y%m%d%H')
        # Forecast files
        if MODEL == 'jma' and inithour == '00':
            fcst_hrs = range(0, 72+24, 24)
        else:
            fcst_hrs = model_dict['fcst_hrs']
        for fcst_hr in fcst_hrs:
            VDATE_dt = CDATE_dt + datetime.timedelta(hours=int(fcst_hr))
            # Forecast files
            if 'input_fcst_file_format' in list(model_dict.keys()):
                input_fcst_file = gda_util.format_filler(
                    model_dict['input_fcst_file_format'], VDATE_dt, CDATE_dt,
                    str(fcst_hr), {}
                )
                tmp_fcst_file = gda_util.format_filler(
                    tmp_fcst_file_format, VDATE_dt, CDATE_dt,
                    str(fcst_hr), {'model': MODEL}
                )
                output_fcst_file = os.path.join(
                    output_INITDATE, MODEL, tmp_fcst_file.rpartition('/')[2]
                )
                if not os.path.exists(output_fcst_file):
                    print("----> Trying to create "+tmp_fcst_file)
                    log_missing_file = os.path.join(
                        DATA, 'mail_missing_'+MODEL+'_fhr'
                        +str(fcst_hr).zfill(3)+'_init'
                        +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
                    )
                    tmp_fcst_file_dir = tmp_fcst_file.rpartition('/')[0]
                    gda_util.make_dir(tmp_fcst_file_dir)
                    if MODEL in ['ecmwf']:
                         gda_util.run_shell_command(['chmod', '750',
                                                     tmp_fcst_file_dir])
                         gda_util.run_shell_command(['chgrp', 'rstprod',
                                                     tmp_fcst_file_dir])
                    if MODEL == 'jma':
                        gda_util.prep_prod_jma_file(input_fcst_file,
                                                    tmp_fcst_file,
                                                    CDATE_dt,
                                                    str(fcst_hr),
                                                    'full',
                                                    log_missing_file)
                    elif MODEL == 'ecmwf':
                        if fcst_hr == 0:
                            input_fcst_file = input_fcst_file[:-2]+'11'
                        gda_util.prep_prod_ecmwf_file(input_fcst_file,
                                                      tmp_fcst_file,
                                                      CDATE_dt,
                                                      str(fcst_hr),
                                                      'full',
                                                      log_missing_file)
                    elif MODEL == 'ukmet':
                        gda_util.prep_prod_ukmet_file(input_fcst_file,
                                                      tmp_fcst_file,
                                                      CDATE_dt,
                                                      str(fcst_hr),
                                                      'full',
                                                      log_missing_file)
                    elif MODEL == 'fnmoc':
                        gda_util.prep_prod_fnmoc_file(input_fcst_file,
                                                      tmp_fcst_file,
                                                      CDATE_dt,
                                                      str(fcst_hr),
                                                      'full',
                                                      log_missing_file)
                    elif MODEL == 'imd':
                        gda_util.prep_prod_imd_file(input_fcst_file,
                                                    tmp_fcst_file,
                                                    CDATE_dt,
                                                    str(fcst_hr),
                                                    'full',
                                                    log_missing_file)
                    elif MODEL == 'cmc':
                        gda_util.prep_prod_cmc_file(input_fcst_file,
                                                    tmp_fcst_file,
                                                    CDATE_dt,
                                                    str(fcst_hr),
                                                    'full',
                                                    log_missing_file)
                    else:
                        gda_util.copy_file(input_fcst_file, tmp_fcst_file)
                        if not os.path.exists(input_fcst_file):
                            gda_util.log_missing_file_model(
                                log_missing_file, input_fcst_file, MODEL,
                                CDATE_dt, str(fcst_hr).zfill(3)
                            )
                    if SENDCOM == 'YES':
                        gda_util.copy_file(tmp_fcst_file, output_fcst_file)
                        if MODEL == 'ecmwf' \
                                and os.path.exists(output_fcst_file):
                            gda_util.run_shell_command(
                                ['chmod', '640', output_fcst_file]
                            )
                            gda_util.run_shell_command(
                                ['chgrp', 'rstprod', output_fcst_file]
                            )
                else:
                    print(f"{output_fcst_file} exists")
            # Forecast files: Precip
            if 'input_precip_file_format' in list(model_dict.keys()):
                input_precip_file = gda_util.format_filler(
                    model_dict['input_precip_file_format'], VDATE_dt,
                    CDATE_dt, str(fcst_hr), {}
                )
                tmp_precip_file = gda_util.format_filler(
                    tmp_precip_file_format, VDATE_dt,
                    CDATE_dt, str(fcst_hr), {'model': MODEL}
                )
                output_precip_file = os.path.join(
                    output_INITDATE, MODEL, tmp_precip_file.rpartition('/')[2]
                )
                if not os.path.exists(output_precip_file):
                    if fcst_hr >= 24 and VDATE_dt.strftime('%H') == '12' \
                            and fcst_hr <= max_precip_fhr \
                            and fcst_hr % 24 == 0:
                        print("----> Trying to create "+tmp_precip_file)
                        log_missing_file = os.path.join(
                            DATA, 'mail_missing_'+MODEL+'_fhr'
                            +str(fcst_hr).zfill(3)+'_init'
                            +CDATE_dt.strftime('%Y%m%d%H')+'_precip.sh'
                        )
                        tmp_precip_file_dir = (
                            tmp_precip_file.rpartition('/')[0]
                        )
                        gda_util.make_dir(tmp_precip_file_dir)
                        if MODEL in ['ecmwf']:
                             gda_util.run_shell_command(
                                 ['chmod', '750', tmp_precip_file_dir]
                             )
                             gda_util.run_shell_command(
                                 ['chgrp', 'rstprod',
                                   tmp_precip_file_dir]
                             )
                        if MODEL == 'jma':
                            gda_util.prep_prod_jma_file(input_precip_file,
                                                        tmp_precip_file,
                                                        CDATE_dt,
                                                        str(fcst_hr),
                                                        'precip',
                                                        log_missing_file)
                        elif MODEL == 'ecmwf':
                            if inithour == '12':
                                gda_util.prep_prod_ecmwf_file(input_precip_file,
                                                              tmp_precip_file,
                                                              CDATE_dt,
                                                              str(fcst_hr),
                                                              'precip',
                                                              log_missing_file)
                        elif MODEL == 'ukmet':
                            gda_util.prep_prod_ukmet_file(input_precip_file,
                                                          tmp_precip_file,
                                                          CDATE_dt,
                                                          str(fcst_hr),
                                                          'precip',
                                                           log_missing_file)
                        elif MODEL == 'fnmoc':
                            gda_util.prep_prod_fnmoc_file(input_precip_file,
                                                          tmp_precip_file,
                                                          str(fcst_hr),
                                                          'precip',
                                                          log_missing_file)
                        elif MODEL == 'dwd':
                            gda_util.prep_prod_dwd_file(input_precip_file,
                                                        tmp_precip_file,
                                                        CDATE_dt,
                                                        str(fcst_hr),
                                                        'precip',
                                                        log_missing_file)
                        elif MODEL == 'metfra':
                            gda_util.prep_prod_metfra_file(input_precip_file,
                                                           tmp_precip_file,
                                                           CDATE_dt,
                                                           str(fcst_hr),
                                                           'precip',
                                                           log_missing_file)
                        elif MODEL == 'cmc':
                            gda_util.prep_prod_cmc_file(input_precip_file,
                                                        tmp_precip_file,
                                                        CDATE_dt,
                                                        str(fcst_hr),
                                                        'precip',
                                                        log_missing_file)
                        elif MODEL == 'cmc_regional':
                            gda_util.prep_prod_cmc_regional_file(
                                input_precip_file, tmp_precip_file, CDATE_dt,
                                str(fcst_hr), 'precip', log_missing_file
                            )
                        else:
                            gda_util.copy_file(input_precip_file,
                                               tmp_precip_file)
                            if not os.path.exists(input_precip_file):
                                gda_util.log_missing_file_model(
                                    log_missing_file, input_precip_file, MODEL,
                                    CDATE_dt, str(fcst_hr).zfill(3)
                                )
                        if SENDCOM == 'YES':
                            gda_util.copy_file(tmp_precip_file,
                                               output_precip_file)
                            if MODEL == 'ecmwf' \
                                    and os.path.exists(output_precip_file):
                                gda_util.run_shell_command(
                                    ['chmod', '640', output_precip_file]
                                )
                                gda_util.run_shell_command(
                                    ['chgrp', 'rstprod', output_precip_file]
                                )
                else:
                    print(f"{output_precip_file} exists")
            # Forecast files: WMO
            if 'input_wmo_file_format' in list(model_dict.keys()):
                input_wmo_file = gda_util.format_filler(
                    model_dict['input_wmo_file_format'], VDATE_dt, CDATE_dt,
                    str(fcst_hr), {}
                )
                tmp_wmo_file = gda_util.format_filler(
                    tmp_wmo_file_format, VDATE_dt,
                    CDATE_dt, str(fcst_hr), {'model': MODEL}
                )
                output_wmo_file = os.path.join(
                    output_INITDATE, MODEL, tmp_wmo_file.rpartition('/')[2]
                )
                if not os.path.exists(output_wmo_file):
                    print("----> Trying to create "+tmp_wmo_file)
                    log_missing_file = os.path.join(
                        DATA, 'mail_missing_'+MODEL+'_fhr'
                        +str(fcst_hr).zfill(3)+'_init'
                        +CDATE_dt.strftime('%Y%m%d%H')+'_wmo.sh'
                    )
                    tmp_wmo_file_dir = (
                        tmp_wmo_file.rpartition('/')[0]
                    )
                    gda_util.make_dir(tmp_wmo_file_dir)
                    if MODEL == 'gfs':
                        gda_util.prep_prod_gfs_file(input_wmo_file,
                                                    tmp_wmo_file,
                                                    CDATE_dt, str(fcst_hr),
                                                    'wmo', log_missing_file)
                    else:
                        print("ERROR: WMO file generation only for gfs")
                        sys.exit(1)
                    if SENDCOM == 'YES':
                        gda_util.copy_file(tmp_wmo_file,
                                           output_wmo_file)
                else:
                    print(f"{output_wmo_file} exists")
        # Analysis file
        if 'input_anl_file_format' in list(model_dict.keys()):
            input_anl_file = gda_util.format_filler(
                model_dict['input_anl_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            tmp_anl_file = gda_util.format_filler(
                tmp_anl_file_format, CDATE_dt, CDATE_dt,
                'anl', {'model': MODEL}
            )
            output_anl_file = os.path.join(
                output_INITDATE, MODEL, tmp_anl_file.rpartition('/')[2]
            )
            if not os.path.exists(output_anl_file):
                print("----> Trying to create "+tmp_anl_file)
                log_missing_file = os.path.join(
                        DATA, 'mail_missing_'+MODEL+'_anl_valid'
                        +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
                    )
                tmp_anl_file_dir = tmp_anl_file.rpartition('/')[0]
                gda_util.make_dir(tmp_anl_file_dir)
                if MODEL in ['ecmwf']:
                     gda_util.run_shell_command(['chmod', '750',
                                                 tmp_anl_file_dir])
                     gda_util.run_shell_command(['chgrp', 'rstprod',
                                                 tmp_anl_file_dir])
                if MODEL == 'jma':
                    gda_util.prep_prod_jma_file(input_anl_file,
                                                tmp_anl_file,
                                                CDATE_dt,
                                                'anl',
                                                'full',
                                                log_missing_file)
                elif MODEL == 'ecmwf':
                    gda_util.prep_prod_ecmwf_file(input_anl_file,
                                                  tmp_anl_file,
                                                  CDATE_dt,
                                                  'anl',
                                                  'full',
                                                  log_missing_file)
                elif MODEL == 'ukmet':
                    gda_util.prep_prod_ukmet_file(input_anl_file,
                                                  tmp_anl_file,
                                                  CDATE_dt,
                                                  'anl',
                                                  'full',
                                                  log_missing_file)
                elif MODEL == 'fnmoc':
                    gda_util.prep_prod_fnmoc_file(input_anl_file,
                                                  tmp_anl_file,
                                                  CDATE_dt,
                                                  'anl',
                                                  'full',
                                                  log_missing_file)
                elif MODEL == 'imd':
                    gda_util.prep_prod_imd_file(input_anl_file,
                                                tmp_anl_file,
                                                CDATE_dt,
                                                'anl',
                                                'full',
                                                log_missing_file)
                elif MODEL == 'cmc':
                    gda_util.prep_prod_cmc_file(input_anl_file,
                                                tmp_anl_file,
                                                CDATE_dt,
                                                'anl',
                                                'full',
                                                log_missing_file)
                else:
                    gda_util.copy_file(input_anl_file, tmp_anl_file)
                    if not os.path.exists(input_anl_file):
                        gda_util.log_missing_file_model(
                            log_missing_file, input_anl_file, MODEL,
                            CDATE_dt, 'anl'
                        )
                if SENDCOM == 'YES':
                    gda_util.copy_file(tmp_anl_file, output_anl_file)
                    if MODEL == 'ecmwf' and os.path.exists(output_anl_file):
                        gda_util.run_shell_command(
                            ['chmod', '640', output_anl_file]
                        )
                        gda_util.run_shell_command(
                            ['chgrp', 'rstprod', output_anl_file]
                        )
            else:
                print(f"{output_anl_file} exists")

###### OBS
# Get operational observation data
# Northern & Southern Hemisphere 10 km OSI-SAF multi-sensor analysis - osi_saf
# Group for High Resolution Sea Surface Temperature (GHRSST) Level 4 SST analysis for Office of Satellite and Product Operations (OSPO)- ghrsst_ospo

global_det_obs_dict = {
    'osi_saf': {'input_file_format': os.path.join(DCOMINosi_saf,
                                                  '{init_shift?fmt=%Y%m%d'
                                                  +'?shift=-12}',
                                                  'seaice', 'osisaf',
                                                  'ice_conc_{hem?fmt=str}_'
                                                  +'polstere-100_multi_'
                                                  +'{init_shift?fmt=%Y%m%d%H'
                                                  +'?shift=-12}00.nc'),
                'tmp_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                                'osi_saf', 'osi_saf.multi.'
                                                +'{hem?fmt=str}.'
                                                +'{init_shift?fmt=%Y%m%d%H'
                                                +'?shift=-24}to'
                                                +'{init?fmt=%Y%m%d%H}.nc'),
                'inithours': ['00']},
    'ghrsst_ospo': {'input_file_format': os.path.join(DCOMINghrsst_ospo,
                                                      '{init_shift?fmt=%Y%m%d'
                                                      +'?shift=-24}',
                                                      'validation_data', 'marine',
                                                      'ghrsst',
                                                      '{init_shift?fmt=%Y%m%d'
                                                      +'?shift=-24}_OSPO_L4_'
                                                      +'GHRSST.nc'),
                    'tmp_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                                    'ghrsst_ospo',
                                                    'ghrsst_ospo.'
                                                    +'{init_shift?fmt=%Y%m%d%H'
                                                    +'?shift=-24}to'
                                                    +'{init?fmt=%Y%m%d%H}.nc'),
                    'inithours': ['00']},
}

for OBS in OBSNAME:
    if OBS not in list(global_det_obs_dict.keys()):
        print("FATAL ERROR: "+OBS+" not recongized")
        sys.exit(1)
    print("---- Prepping data for "+OBS+" for init "+INITDATE)
    obs_dict = global_det_obs_dict[OBS]
    for inithour in obs_dict['inithours']:
        CDATE = INITDATE+inithour
        CDATE_dt = datetime.datetime.strptime(CDATE, '%Y%m%d%H')
        input_file = gda_util.format_filler(
            obs_dict['input_file_format'], CDATE_dt, CDATE_dt,
            'anl', {}
        )
        tmp_file = gda_util.format_filler(
           obs_dict['tmp_file_format'], CDATE_dt, CDATE_dt,
           'anl', {}
        )
        output_file = os.path.join(
            output_INITDATE, OBS, tmp_file.rpartition('/')[2]
        )
        tmp_file_dir = tmp_file.rpartition('/')[0]
        gda_util.make_dir(tmp_file_dir)
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
                input_hem_file = input_file.replace('{hem?fmt=str}', hem)
                tmp_hem_file = tmp_file.replace('{hem?fmt=str}', hem)
                output_hem_file = output_file.replace('{hem?fmt=str}', hem)
                if not os.path.exists(output_hem_file):
                    print("----> Trying to create "+tmp_hem_file)
                    gda_util.prep_prod_osi_saf_file(
                        input_hem_file, tmp_hem_file, CDATE_dt,
                        log_missing_file
                    )
                    if SENDCOM == 'YES':
                        gda_util.copy_file(tmp_hem_file, output_hem_file)
                else:
                    print(f"{output_hem_file} exists")
        elif OBS == 'ghrsst_ospo':
            log_missing_file = os.path.join(
                DATA, 'mail_missing_'+OBS+'_valid'
                +CDATE_dt.strftime('%Y%m%d%H')+'.sh'
            )
            if not os.path.exists(output_file):
                print("----> Trying to create "+tmp_file)
                gda_util.prep_prod_ghrsst_ospo_file(
                    input_file, tmp_file, CDATE_dt,
                    log_missing_file
                )
                if SENDCOM == 'YES':
                    gda_util.copy_file(tmp_file, output_file)
            else:
                print(f"{output_file} exists")

print("END: "+os.path.basename(__file__))
