'''
Name: global_det_atmos_prep_prod_archive.py
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
COMROOT = os.environ['COMROOT']
COMOUT = os.environ['COMOUT']
DCOMROOT = os.environ['DCOMROOT']
INITDATE = os.environ['INITDATE']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
model_list = os.environ['model_list'].split(' ')
gfs_ver = os.environ['gfs_ver']
cmc_ver = os.environ['cmc_ver']
cfs_ver = os.environ['cfs_ver']

# Get operational global deterministic model data
# Global Forecast System - gfs
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
    'gfs': {'prod_fcst_file_format': os.path.join(COMROOT, 'gfs', gfs_ver,
                                                  'gfs.{init?fmt=%Y%m%d}',
                                                  '{init?fmt=%2H}',
                                                  'atmos',
                                                  'gfs.t{init?fmt=%2H}z.'
                                                  +'pgrb2.0p50.'
                                                  +'f{lead?fmt=%3H}'),
            'prod_anl_file_format': os.path.join(COMROOT, 'gfs', gfs_ver,
                                                 'gfs.{init?fmt=%Y%m%d}',
                                                 '{init?fmt=%2H}',
                                                 'atmos',
                                                 'gfs.t{init?fmt=%2H}z.'
                                                 +'pgrb2.0p50.anl'),
            'prod_precip_file_format': os.path.join(COMROOT, 'gfs', gfs_ver,
                                                    'gfs.{init?fmt=%Y%m%d}',
                                                    '{init?fmt=%2H}',
                                                    'atmos',
                                                    'gfs.t{init?fmt=%2H}z.'
                                                    +'pgrb2.0p25.'
                                                    +'f{lead?fmt=%3H}'),
            'cycles': ['00', '06', '12', '18'],
            'fcst_hrs': range(0, 384+3, 3)},
    'jma': {'prod_fcst_file_format': os.path.join(DCOMROOT,
                                                  '{init?fmt=%Y%m%d}',
                                                  'wgrbbul',
                                                  'jma_{hem?fmt=str}'
                                                  +'_{init?fmt=%H}'),
            'prod_anl_file_format': os.path.join(DCOMROOT,
                                                 '{init?fmt=%Y%m%d}',
                                                 'wgrbbul',
                                                 'jma_{hem?fmt=str}'
                                                 +'_{init?fmt=%H}'),
            'prod_precip_file_format': os.path.join(DCOMROOT,
                                                    '{init?fmt=%Y%m%d}',
                                                    'qpf_verif', 'jma_'
                                                    +'{init?fmt=%Y%m%d%H}00'
                                                    +'.grib'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 72+12, 12)},
    'ecmwf': {'prod_fcst_file_format': os.path.join(DCOMROOT,
                                                    '{init?fmt=%Y%m%d}',
                                                    'wgrbbul', 'ecmwf',
                                                    'U1D{init?fmt=%m%d%H}00'
                                                    +'{valid?fmt=%m%d%H}001'),
              'prod_anl_file_format': os.path.join(DCOMROOT,
                                                   '{init?fmt=%Y%m%d}',
                                                   'wgrbbul', 'ecmwf',
                                                   'U1D{init?fmt=%m%d%H}00'
                                                   +'{init?fmt=%m%d%H}011'),
              'prod_precip_file_format': os.path.join(DCOMROOT,
                                                      '{init?fmt=%Y%m%d}',
                                                      'qpf_verif',
                                                      'UWD{init?fmt=%Y%m%d%H%M}'
                                                      +'{valid?fmt=%m%d%H%M}1'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 240+12, 12)},
    'ukmet': {'prod_fcst_file_format': os.path.join(DCOMROOT,
                                                    '{init?fmt=%Y%m%d}',
                                                    'wgrbbul', 'ukmet_hires',
                                                    'GAB{init?fmt=%2H}'
                                                    +'{letter?fmt=str}.GRB'),
              'prod_anl_file_format': os.path.join(DCOMROOT,
                                                   '{init?fmt=%Y%m%d}',
                                                   'wgrbbul', 'ukmet_hires',
                                                   'GAB{init?fmt=%2H}AAT.GRB'),
              'prod_precip_file_format': os.path.join(DCOMROOT,
                                                      '{init?fmt=%Y%m%d}',
                                                      'qpf_verif', 'ukmo.'
                                                      +'{init?fmt=%Y%m%d%H}'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 144+12, 12)},
    'imd': {'prod_fcst_file_format': os.path.join(DCOMROOT,
                                                  '{init?fmt=%Y%m%d}',
                                                  'wgrbbul', 'ncmrwf_gdas',
                                                  'gdas1.t{init?fmt=%2H}z.'
                                                  +'grbf{lead?fmt=%2H}'),
            'prod_anl_file_format': os.path.join(DCOMROOT,
                                                 '{init?fmt=%Y%m%d}',
                                                 'wgrbbul', 'ncmrwf_gdas',
                                                 'gdas1.t{init?fmt=%2H}z.'
                                                 +'grbf00'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 240+12, 12)},
    'cmc': {'prod_fcst_file_format': os.path.join(COMROOT, 'cmc', cmc_ver,
                                                  'cmc.{init?fmt=%Y%m%d}',
                                                  'cmc_{init?fmt=%Y%m%d%H}'
                                                  +'f{lead?fmt=%3H}'),
            'prod_anl_file_format': os.path.join(COMROOT, 'cmc', cmc_ver,
                                                 'cmc.{init?fmt=%Y%m%d}',
                                                 'cmc_{init?fmt=%Y%m%d%H}'
                                                 +'f000'),
            'prod_precip_file_format': os.path.join(DCOMROOT,
                                                    '{init?fmt=%Y%m%d}',
                                                    'qpf_verif','cmcglb_'
                                                    +'{init?fmt=%Y%m%d%H}_'
                                                    +'{lead_shift?fmt=%3H?'
                                                    +'shift=-24}_'
                                                    +'{lead?fmt=%3H}.grb2'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 240+12, 12)},
    'cmc_regional': {'prod_precip_file_format': os.path.join(DCOMROOT,
                                                             '{init?fmt=%Y%m%d}',
                                                             'qpf_verif','cmc_'
                                                             +'{init?fmt=%Y%m%d%H}_'
                                                             +'{lead_shift?fmt=%3H?'
                                                             +'shift=-24}_'
                                                             +'{lead?fmt=%3H}'),
                     'cycles': ['00', '12'],
                     'fcst_hrs': range(24, 48+12, 12)},
    'fnmoc': {'prod_fcst_file_format': os.path.join(DCOMROOT, 'navgem',
                                                    'US058GMET-OPSbd2.NAVGEM'
                                                    +'{lead?fmt=%3H}-'
                                                    +'{init?fmt=%Y%m%d%H}-'
                                                    +'NOAA-halfdeg.gr2'),
              'prod_anl_file_format': os.path.join(DCOMROOT, 'navgem',
                                                    'US058GMET-OPSbd2.NAVGEM'
                                                    +'000-'
                                                    +'{init?fmt=%Y%m%d%H}-'
                                                    +'NOAA-halfdeg.gr2'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 180+12, 12)},
    'cfs': {'prod_fcst_file_format': os.path.join(COMROOT, 'cfs', cfs_ver,
                                                  'cfs.{init?fmt=%Y%m%d}',
                                                  '{init?fmt=%H}',
                                                  '6hrly_grib_01',
                                                  'pgbf{valid?fmt=%Y%m%d%H}.01'
                                                  +'.{init?fmt=%Y%m%d%H}'
                                                  +'.grb2'),
            'prod_anl_file_format': os.path.join(COMROOT, 'cfs', cfs_ver,
                                                 'cdas.{init?fmt=%Y%m%d}',
                                                 'cdas1.t{init?fmt=%H}z.'
                                                 +'pgrblanl'),
            'cycles': ['00'],
            'fcst_hrs': range(0, 384+6, 6)},
    'dwd': {'prod_precip_file_format': os.path.join(DCOMROOT,
                                                    '{init?fmt=%Y%m%d}',
                                                    'qpf_verif','dwd_'
                                                    +'{init?fmt=%Y%m%d%H}_'
                                                    +'{lead_shift?fmt=%3H?'
                                                    +'shift=-24}_'
                                                    +'{lead?fmt=%3H}'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(24, 72+12, 12)},
    'metfra': {'prod_precip_file_format': os.path.join(DCOMROOT,
                                                       '{init?fmt=%Y%m%d}',
                                                       'qpf_verif','METFRA_'
                                                       +'{init?fmt=%H}_'
                                                       +'{init?fmt=%Y%m%d}'),
               'cycles': ['00', '12'],
               'fcst_hrs': range(24, 72+12, 12)}
}
arch_fcst_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                     '{model?fmt=%str}',
                                     '{model?fmt=%str}.t{init?fmt=%2H}z.'
                                     +'f{lead?fmt=%3H}')
arch_anl_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                    '{model?fmt=%str}',
                                    '{model?fmt=%str}.t{init?fmt=%2H}z.anl')
arch_precip_file_format = os.path.join(DATA, RUN+'.'+INITDATE,
                                       '{model?fmt=%str}',
                                       '{model?fmt=%str}.precip.'
                                       +'t{init?fmt=%2H}z.'
                                       +'f{lead?fmt=%3H}')

for MODEL in model_list:
    if MODEL not in list(global_det_model_dict.keys()):
        print("ERROR: "+MODEL+" not recongized")
        sys.exit(1)
    print("---- Prepping data for "+MODEL+" for init "+INITDATE)
    model_dict = global_det_model_dict[MODEL]
    for cycle in model_dict['cycles']:
        CDATE = INITDATE+cycle
        CDATE_dt = datetime.datetime.strptime(CDATE, '%Y%m%d%H')
        # Forecast files
        for fcst_hr in model_dict['fcst_hrs']:
            VDATE_dt = CDATE_dt + datetime.timedelta(hours=int(fcst_hr))
            if 'prod_fcst_file_format' in list(model_dict.keys()):
                prod_fcst_file = gda_util.format_filler(
                    model_dict['prod_fcst_file_format'], VDATE_dt, CDATE_dt,
                    str(fcst_hr), {}
                )
                arch_fcst_file = gda_util.format_filler(
                    arch_fcst_file_format, VDATE_dt, CDATE_dt,
                    str(fcst_hr), {'model': MODEL}
                )
                if not os.path.exists(arch_fcst_file):
                    print("----> Trying to create "+arch_fcst_file)
                    arch_fcst_file_dir = arch_fcst_file.rpartition('/')[0]
                    if not os.path.exists(arch_fcst_file_dir):
                        os.makedirs(arch_fcst_file_dir)
                        if MODEL in ['ecmwf']:
                             gda_util.run_shell_command(['chmod', '750',
                                                         arch_fcst_file_dir])
                             gda_util.run_shell_command(['chgrp', 'rstprod',
                                                         arch_fcst_file_dir])
                    if MODEL == 'gfs':
                        gda_util.prep_prod_gfs_file(prod_fcst_file,
                                                    arch_fcst_file,
                                                    str(fcst_hr),
                                                    'full')
                    elif MODEL == 'jma':
                        gda_util.prep_prod_jma_file(prod_fcst_file,
                                                    arch_fcst_file,
                                                    str(fcst_hr),
                                                    'full')
                    elif MODEL == 'ecmwf':
                        gda_util.prep_prod_ecmwf_file(prod_fcst_file,
                                                      arch_fcst_file,
                                                      str(fcst_hr),
                                                     'full')
                    elif MODEL == 'ukmet':
                        gda_util.prep_prod_ukmet_file(prod_fcst_file,
                                                      arch_fcst_file,
                                                      str(fcst_hr),
                                                      'full')
                    elif MODEL == 'fnmoc':
                        gda_util.prep_prod_fnmoc_file(prod_fcst_file,
                                                      arch_fcst_file,
                                                      str(fcst_hr),
                                                      'full')
                    else:
                        gda_util.copy_file(prod_fcst_file, arch_fcst_file)
            if 'prod_precip_file_format' in list(model_dict.keys()):
                prod_precip_file = gda_util.format_filler(
                    model_dict['prod_precip_file_format'], VDATE_dt,
                    CDATE_dt, str(fcst_hr), {}
                )
                arch_precip_file = gda_util.format_filler(
                    arch_precip_file_format, VDATE_dt,
                    CDATE_dt, str(fcst_hr), {'model': MODEL}
                )
                if not os.path.exists(arch_precip_file) and fcst_hr != 0:
                    print("----> Trying to create "+arch_precip_file)
                    arch_precip_file_dir = (
                        arch_precip_file.rpartition('/')[0]
                    )
                    if not os.path.exists(arch_precip_file_dir):
                        os.makedirs(arch_precip_file_dir)
                        if MODEL in ['ecmwf']:
                             gda_util.run_shell_command(
                                 ['chmod', '750', arch_precip_file_dir]
                             )
                             gda_util.run_shell_command(
                                 ['chgrp', 'rstprod',
                                   arch_precip_file_dir]
                             )
                    if MODEL == 'gfs':
                        gda_util.prep_prod_gfs_file(prod_precip_file,
                                                    arch_precip_file,
                                                    str(fcst_hr),
                                                    'precip')
                    elif MODEL == 'jma':
                        gda_util.prep_prod_jma_file(prod_precip_file,
                                                    arch_precip_file,
                                                    str(fcst_hr),
                                                    'precip')
                    elif MODEL == 'ecmwf':
                        gda_util.prep_prod_ecmwf_file(prod_precip_file,
                                                      arch_precip_file,
                                                      str(fcst_hr),
                                                      'precip')
                    elif MODEL == 'ukmet':
                        gda_util.prep_prod_ukmet_file(prod_precip_file,
                                                      arch_precip_file,
                                                      str(fcst_hr),
                                                      'precip')
                    elif MODEL == 'fnmoc':
                        gda_util.prep_prod_fnmoc_file(prod_precip_file,
                                                      arch_precip_file,
                                                      str(fcst_hr),
                                                      'precip')
                    elif MODEL == 'dwd':
                        gda_util.prep_prod_dwd_file(prod_precip_file,
                                                    arch_precip_file,
                                                    str(fcst_hr),
                                                    'precip')
                    elif MODEL == 'metfra':
                        gda_util.prep_prod_metfra_file(prod_precip_file,
                                                       arch_precip_file,
                                                       str(fcst_hr),
                                                       'precip')
                    else:
                        gda_util.copy_file(prod_precip_file,
                                           arch_precip_file)
        # Analysis file
        if 'prod_anl_file_format' in list(model_dict.keys()):
            prod_anl_file = gda_util.format_filler(
                model_dict['prod_anl_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            arch_anl_file = gda_util.format_filler(
                arch_anl_file_format, CDATE_dt, CDATE_dt,
                'anl', {'model': MODEL}
            )
            if not os.path.exists(arch_anl_file):
                arch_anl_file_dir = arch_anl_file.rpartition('/')[0]
                if not os.path.exists(arch_anl_file_dir):
                    os.makedirs(arch_anl_file_dir)
                    if MODEL in ['ecmwf']:
                         gda_util.run_shell_command(['chmod', '750',
                                                     arch_anl_file_dir])
                         gda_util.run_shell_command(['chgrp', 'rstprod',
                                                     arch_anl_file_dir])
                print("----> Trying to create "+arch_anl_file)
                if MODEL == 'gfs':
                    gda_util.prep_prod_gfs_file(prod_anl_file,
                                                arch_anl_file,
                                                'anl',
                                                'full')
                elif MODEL == 'jma':
                    gda_util.prep_prod_jma_file(prod_anl_file,
                                                arch_anl_file,
                                                'anl',
                                                'full')
                elif MODEL == 'ecmwf':
                    gda_util.prep_prod_ecmwf_file(prod_anl_file,
                                                  arch_anl_file,
                                                  'anl',
                                                  'full')
                elif MODEL == 'ukmet':
                    gda_util.prep_prod_ukmet_file(prod_anl_file,
                                                  arch_anl_file,
                                                  'anl',
                                                  'full')
                elif MODEL == 'fnmoc':
                    gda_util.prep_prod_fnmoc_file(prod_anl_file,
                                                  arch_anl_file,
                                                  'anl',
                                                  'full')
                else:
                    gda_util.copy_file(prod_anl_file, arch_anl_file)

print("END: "+os.path.basename(__file__))
