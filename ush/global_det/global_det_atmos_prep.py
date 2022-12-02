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
COMINghrsst_median = os.environ['COMINghrsst_median']
COMINget_d = os.environ['COMINget_d']
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
    'cfs': {'prod_fcst_file_format': os.path.join(COMINcfs,
                                                  '{init?fmt=%H}',
                                                  '6hrly_grib_01',
                                                  'pgbf{valid?fmt=%Y%m%d%H}.01'
                                                  +'.{init?fmt=%Y%m%d%H}'
                                                  +'.grb2'),
            'cycles': ['00', '06', '12', '18'],
            'fcst_hrs': range(0, 384+6, 6)},
    'cmc': {'prod_fcst_file_format': os.path.join(COMINcmc,
                                                  'cmc_{init?fmt=%Y%m%d%H}'
                                                  +'f{lead?fmt=%3H}'),
            'prod_anl_file_format': os.path.join(COMINcmc,
                                                 'cmc_{init?fmt=%Y%m%d%H}'
                                                 +'f000'),
            'prod_precip_file_format': os.path.join(COMINcmc_precip, 'cmcglb_'
                                                    +'{init?fmt=%Y%m%d%H}_'
                                                    +'{lead_shift?fmt=%3H?'
                                                    +'shift=-24}_'
                                                    +'{lead?fmt=%3H}.grb2'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 240+6, 6)},
    'cmc_regional': {'prod_precip_file_format': os.path.join(COMINcmc_regional_precip,
                                                             'cmc_'
                                                             +'{init?fmt=%Y%m%d%H}_'
                                                             +'{lead_shift?fmt=%3H?'
                                                             +'shift=-24}_'
                                                             +'{lead?fmt=%3H}'),
                     'cycles': ['00', '12'],
                     'fcst_hrs': range(24, 48+12, 12)},
    'dwd': {'prod_precip_file_format': os.path.join(COMINdwd_precip, 'dwd_'
                                                    +'{init?fmt=%Y%m%d%H}_'
                                                    +'{lead_shift?fmt=%3H?'
                                                    +'shift=-24}_'
                                                    +'{lead?fmt=%3H}'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(24, 72+12, 12)},
    'ecmwf': {'prod_fcst_file_format': os.path.join(COMINecmwf,
                                                    'U1D{init?fmt=%m%d%H}00'
                                                    +'{valid?fmt=%m%d%H}001'),
              'prod_anl_file_format': os.path.join(COMINecmwf,
                                                   'U1D{init?fmt=%m%d%H}00'
                                                   +'{init?fmt=%m%d%H}011'),
              'prod_precip_file_format': os.path.join(COMINecmwf_precip,
                                                      'UWD{init?fmt=%Y%m%d%H%M}'
                                                      +'{valid?fmt=%m%d%H%M}1'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 240+6, 6)},
    'fnmoc': {'prod_fcst_file_format': os.path.join(COMINfnmoc,
                                                    'US058GMET-OPSbd2.NAVGEM'
                                                    +'{lead?fmt=%3H}-'
                                                    +'{init?fmt=%Y%m%d%H}-'
                                                    +'NOAA-halfdeg.gr2'),
              'prod_anl_file_format': os.path.join(COMINfnmoc,
                                                    'US058GMET-OPSbd2.NAVGEM'
                                                    +'000-'
                                                    +'{init?fmt=%Y%m%d%H}-'
                                                    +'NOAA-halfdeg.gr2'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 180+6, 6)},
    'imd': {'prod_fcst_file_format': os.path.join(COMINimd,
                                                  'gdas1.t{init?fmt=%2H}z.'
                                                  +'grbf{lead?fmt=%2H}'),
            'prod_anl_file_format': os.path.join(COMINimd,
                                                 'gdas1.t{init?fmt=%2H}z.'
                                                 +'grbf00'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 240+6, 6)},
    'jma': {'prod_fcst_file_format': os.path.join(COMINjma,
                                                  'jma_{hem?fmt=str}'
                                                  +'_{init?fmt=%H}'),
            'prod_anl_file_format': os.path.join(COMINjma,
                                                 'jma_{hem?fmt=str}'
                                                 +'_{init?fmt=%H}'),
            'prod_precip_file_format': os.path.join(COMINjma_precip, 'jma_'
                                                    +'{init?fmt=%Y%m%d%H}00'
                                                    +'.grib'),
            'cycles': ['00', '12'],
            'fcst_hrs': range(0, 192+24, 24)},
    'metfra': {'prod_precip_file_format': os.path.join(COMINmetfra_precip,
                                                       'METFRA_'
                                                       +'{init?fmt=%H}_'
                                                       +'{init?fmt=%Y%m%d}'),
               'cycles': ['00', '12'],
               'fcst_hrs': range(24, 72+12, 12)},
    'ukmet': {'prod_fcst_file_format': os.path.join(COMINukmet,
                                                    'GAB{init?fmt=%2H}'
                                                    +'{letter?fmt=str}.GRB'),
              'prod_anl_file_format': os.path.join(COMINukmet,
                                                   'GAB{init?fmt=%2H}AAT.GRB'),
              'prod_precip_file_format': os.path.join(COMINukmet_precip, 'ukmo.'
                                                      +'{init?fmt=%Y%m%d%H}'),
              'cycles': ['00', '12'],
              'fcst_hrs': range(0, 144+6, 6)}
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

for MODEL in MODELNAME:
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
                COMOUT_fcst_file = os.path.join(
                    COMOUT_INITDATE, MODEL, arch_fcst_file.rpartition('/')[2]
                )
                if not os.path.exists(COMOUT_fcst_file) \
                        and not os.path.exists(arch_fcst_file):
                    print("----> Trying to create "+arch_fcst_file)
                    arch_fcst_file_dir = arch_fcst_file.rpartition('/')[0]
                    if not os.path.exists(arch_fcst_file_dir):
                        os.makedirs(arch_fcst_file_dir)
                        if MODEL in ['ecmwf']:
                             gda_util.run_shell_command(['chmod', '750',
                                                         arch_fcst_file_dir])
                             gda_util.run_shell_command(['chgrp', 'rstprod',
                                                         arch_fcst_file_dir])
                    if MODEL == 'jma':
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
                COMOUT_precip_file = os.path.join(
                    COMOUT_INITDATE, MODEL, arch_precip_file.rpartition('/')[2]
                )
                if not os.path.exists(COMOUT_precip_file) \
                        and not os.path.exists(arch_precip_file) and fcst_hr != 0:
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
                    if MODEL == 'jma':
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
            COMOUT_anl_file = os.path.join(
                COMOUT_INITDATE, MODEL, arch_anl_file.rpartition('/')[2]
            )
            if not os.path.exists(COMOUT_anl_file) \
                    and not os.path.exists(arch_anl_file):
                arch_anl_file_dir = arch_anl_file.rpartition('/')[0]
                if not os.path.exists(arch_anl_file_dir):
                    os.makedirs(arch_anl_file_dir)
                    if MODEL in ['ecmwf']:
                         gda_util.run_shell_command(['chmod', '750',
                                                     arch_anl_file_dir])
                         gda_util.run_shell_command(['chgrp', 'rstprod',
                                                     arch_anl_file_dir])
                print("----> Trying to create "+arch_anl_file)
                if MODEL == 'jma':
                    gda_util.prep_prod_jma_file(prod_anl_file,
                                                arch_anl_file,
                                                'anl',
                                                'full')
                elif MODEL == 'ecmwf':
                    gda_util.prep_prod_ecmwf_file(prod_anl_file,
                                                  arch_anl_file,
                                                  'anl',
                                                  'full')
                    if os.path.exists(arch_anl_file):
                        ecmwf_f000_file = gda_util.format_filler(
                            arch_fcst_file_format, CDATE_dt, CDATE_dt,
                            '00', {'model': MODEL}
                        )
                        shutil.copy2(arch_anl_file, ecmwf_f000_file)
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

###### OBS
# Get operational observation data
# Nortnern & Southern Hemisphere 10 km OSI-SAF multi-sensor analysis - osi_saf
global_det_obs_dict = {
    'osi_saf': {'daily_prod_file_format': os.path.join(COMINosi_saf,
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
                'cycles': ['00']},
    'ghrsst_median': {'prod_file_format': os.path.join(COMINghrsst_median,
                                                       '{init_shift?fmt=%Y%m%d'
                                                       +'?shift=-12}',
                                                       'validation_data', 'marine', 
                                                       'ghrsst',
                                                       '{init_shift?fmt=%Y%m%d%H'
                                                       +'?shift=-12}0000-'
                                                       +'UKMO-L4_GHRSST-'
                                                       +'SSTfnd-GMPE-GLOB-'
                                                       +'v03.0-fv03.0.nc'),
                      'arch_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                                       'ghrsst_median',
                                                       'ghrsst_median.'
                                                       +'{init_shift?fmt=%Y%m%d%H'
                                                       +'?shift=-24}to'
                                                       +'{init?fmt=%Y%m%d%H}.nc'),
                      'cycles': ['00']},
    'get_d': {'prod_file_format': os.path.join(COMINget_d, 'get_d',
                                               'GETDL3_DAL_CONUS_'
                                               +'{init?fmt=%Y%j}_1.0.nc'),
                      'arch_file_format': os.path.join(DATA, RUN+'.'+INITDATE,
                                                       'get_d',
                                                       'get_d.'
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
        else:
            prod_file = gda_util.format_filler(
                obs_dict['prod_file_format'], CDATE_dt, CDATE_dt,
                'anl', {}
            )
            arch_file = gda_util.format_filler(
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
                if OBS == 'ghrsst_median':
                    gda_util.prep_prod_ghrsst_median_file(
                        prod_file, arch_file,
                        datetime.datetime.strptime(CDATE, '%Y%m%d%H')
                    )
                elif OBS == 'get_d':
                    gda_util.prep_prod_get_d_file(
                        prod_file, arch_file,
                        datetime.datetime.strptime(CDATE, '%Y%m%d%H')
                    )

print("END: "+os.path.basename(__file__))
