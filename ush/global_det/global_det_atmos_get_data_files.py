'''
Name: global_det_atmos_get_data_files.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This gets the necessary data files to run
          the  use case.
'''

import os
import datetime
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in common environment variables
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
DATA = os.environ['DATA']
model_list = os.environ['model_list'].split(' ')
model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
machine = os.environ['machine']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
COMROOT_PROD = os.environ['COMROOT_PROD']
DCOMROOT_PROD = os.environ['DCOMROOT_PROD']
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
USER = os.environ['USER']
ccpa_ver = os.environ['ccpa_ver']
obsproc_ver = os.environ['obsproc_ver']

# Make sure in right working directory
cwd = os.getcwd()
if cwd != DATA:
    os.chdir(DATA)

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
if VERIF_CASE_STEP == 'grid2grid_stats':
    # Read in VERIF_CASE_STEP related environment variables
    VERIF_CASE_STEP_pres_levs_truth_format_list = os.environ[
        VERIF_CASE_STEP_abbrev+'_pres_levs_truth_format_list'
    ].split(' ')
    VERIF_CASE_STEP_precip_file_format_list = os.environ[
        VERIF_CASE_STEP_abbrev+'_precip_file_format_list'
    ].split(' ')
    VERIF_CASE_STEP_precip_file_accum_list = os.environ[
        VERIF_CASE_STEP_abbrev+'_precip_file_accum_list'
    ].split(' ')
    # Get model forecast and truth files for
    # each option in VERIF_CASE_STEP_type_list
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +VERIF_CASE_STEP_type)
        # Set valid hours
        if VERIF_CASE_STEP_type in ['pres_levs', 'means']: 
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type == 'precip':
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        elif VERIF_CASE_STEP_type == 'snow':
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        # Set cycle hours
        VERIF_CASE_STEP_type_cycle_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_cycle_list'
        ].split(' ')
        # Set forecast hours
        VERIF_CASE_STEP_type_fhr_min = (
            os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_min']
        )
        VERIF_CASE_STEP_type_fhr_max = (
            os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_max']
        )
        VERIF_CASE_STEP_type_fhr_inc = (
            os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_inc']
        )
        VERIF_CASE_STEP_type_fhr_list = list(
            range(int(VERIF_CASE_STEP_type_fhr_min),
                  int(VERIF_CASE_STEP_type_fhr_max)
                  +int(VERIF_CASE_STEP_type_fhr_inc),
                  int(VERIF_CASE_STEP_type_fhr_inc))
        )
        # Get time information
        VERIF_CASE_STEP_type_time_info_dict = gda_util.get_time_info(
            start_date, end_date, 'VALID', VERIF_CASE_STEP_type_cycle_list,
            VERIF_CASE_STEP_type_valid_hr_list, VERIF_CASE_STEP_type_fhr_list
        )
        # Get forecast files for each model
        VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
        VERIF_CASE_STEP_type_valid_time_list = []
        for time in VERIF_CASE_STEP_type_time_info_dict:
            if time['valid_time'] not in VERIF_CASE_STEP_type_valid_time_list:
                VERIF_CASE_STEP_type_valid_time_list.append(time['valid_time'])
            for model_idx in range(len(model_list)):
                model = model_list[model_idx]
                VERIF_CASE_STEP_model_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, model
                )
                if not os.path.exists(VERIF_CASE_STEP_model_dir):
                    os.makedirs(VERIF_CASE_STEP_model_dir)
                if VERIF_CASE_STEP_type == 'precip':
                    model_file_format = (
                        VERIF_CASE_STEP_precip_file_format_list[model_idx]
                    )
                    model_accum = (
                        VERIF_CASE_STEP_precip_file_accum_list[model_idx]
                    )
                    model_fcst_dest_file_format = os.path.join(
                        VERIF_CASE_STEP_model_dir,
                        model+'.precip.{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                    )
                else:
                    model_file_format = model_file_format_list[model_idx]
                    model_fcst_dest_file_format = os.path.join(
                        VERIF_CASE_STEP_model_dir,
                        model+'.'+'{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                    )
                gda_util.get_model_file(
                    time['valid_time'], time['init_time'],
                    time['forecast_hour'], model_file_format,
                    model_fcst_dest_file_format
                )
                if VERIF_CASE_STEP_type == 'pres_levs':
                    # Get previous day for Geopotential
                    # Height Anomaly verification
                    gda_util.get_model_file(
                        time['valid_time'] - datetime.timedelta(days=1),
                        time['init_time'] - datetime.timedelta(days=1),
                        time['forecast_hour'], model_file_format,
                        model_fcst_dest_file_format
                    )
                elif VERIF_CASE_STEP_type == 'precip':
                    # Get for 24 hour accumulations
                    fhrs_24hr_accum_list = []
                    if model_accum == 'continuous':
                        nfiles_24hr_accum = 2
                        fhrs_24hr_accum_list.append(
                            time['forecast_hour']
                        )
                        if int(time['forecast_hour']) - 24 > 0:
                            fhrs_24hr_accum_list.append(
                                str(int(time['forecast_hour']) - 24)
                            )
                    elif int(model_accum) == 24:
                        nfiles_24hr_accum = 1
                        fhrs_24hr_accum_list.append(
                            time['forecast_hour']
                        )
                    elif int(model_accum) < 24:
                        nfiles_24hr_accum = int(24/int(model_accum))
                        nf = 1
                        while nf <= nfiles_24hr_accum:
                            fhr_nf = (int(time['forecast_hour'])
                                      -(nf-1)*int(model_accum))
                            if fhr_nf > 0:
                                fhrs_24hr_accum_list.append(
                                    str(fhr_nf)
                                )
                            nf+=1
                    elif int(model_accum) > 24:
                        print("WARNING: the model precip file "
                              "accumulation for "+model+" ("
                              +model_file_format+") is greater than "
                              +"the verifying accumulation of 24 hours,"
                              +"please remove")
                        sys.exit(1)
                    if len(fhrs_24hr_accum_list) == nfiles_24hr_accum:
                        for fhr in fhrs_24hr_accum_list:
                            gda_util.get_model_file(
                                time['valid_time'], time['init_time'],
                                fhr, model_file_format,
                                model_fcst_dest_file_format 
                            )
                elif VERIF_CASE_STEP_type == 'snow':
                    # Get for 24 hour accumulations
                    if int(time['forecast_hour']) - 24 >= 0:
                        gda_util.get_model_file(
                            time['valid_time'], time['init_time'],
                            str(int(time['forecast_hour']) - 24),
                            model_file_format, model_fcst_dest_file_format
                        )
        # Get truth files
        for VERIF_CASE_STEP_type_valid_time \
                in VERIF_CASE_STEP_type_valid_time_list:
            if VERIF_CASE_STEP_type == 'pres_levs':
                # Model Analysis
                for model_idx in range(len(model_list)):
                    model = model_list[model_idx]
                    model_truth_file_format = (
                        VERIF_CASE_STEP_pres_levs_truth_format_list[model_idx]
                    )
                    VERIF_CASE_STEP_model_dir = os.path.join(
                        VERIF_CASE_STEP_data_dir, model
                    )
                    pres_levs_dest_file_format = os.path.join(
                        VERIF_CASE_STEP_model_dir,
                        model+'.'+'{valid?fmt=%Y%m%d%H}.truth'
                    )
                    if not os.path.exists(VERIF_CASE_STEP_model_dir):
                        os.makedirs(VERIF_CASE_STEP_model_dir)
                    gda_util.get_model_file(
                        VERIF_CASE_STEP_type_valid_time,
                        VERIF_CASE_STEP_type_valid_time,
                        'anl', model_truth_file_format,
                        pres_levs_dest_file_format
                    )
                    # Get previous day for Geopotential
                    # Height Anomaly verification
                    gda_util.get_model_file(
                        (VERIF_CASE_STEP_type_valid_time
                         - datetime.timedelta(days=1)),
                        (VERIF_CASE_STEP_type_valid_time
                         - datetime.timedelta(days=1)),
                        'anl', model_truth_file_format,
                        pres_levs_dest_file_format
                    )
            elif VERIF_CASE_STEP_type == 'precip':
                # CCPA
                ccpa_source_file_format = os.path.join(
                    COMROOT_PROD, 'ccpa', ccpa_ver, 'ccpa.{valid?fmt=%Y%m%d}',
                    '{valid?fmt=%H}',
                    'ccpa.t{valid?fmt=%H}z.06h.hrap.conus.gb2'
                )
                VERIF_CASE_STEP_ccpa_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ccpa'
                )
                ccpa_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_ccpa_dir, 'ccpa.6H.{valid?fmt=%Y%m%d%H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_ccpa_dir):
                    os.makedirs(VERIF_CASE_STEP_ccpa_dir)
                accum_valid_start = (VERIF_CASE_STEP_type_valid_time -
                                     datetime.timedelta(days=1))
                accum_valid_end = VERIF_CASE_STEP_type_valid_time
                accum_valid = accum_valid_end
                while accum_valid > accum_valid_start:
                    gda_util.get_truth_file(
                        accum_valid, ccpa_source_file_format,
                        ccpa_dest_file_format
                    )
                    accum_valid = (accum_valid -
                                   datetime.timedelta(hours=6))
            elif VERIF_CASE_STEP_type == 'snow':
                # NOHRSC
                nohrsc_source_file_format = os.path.join(
                    DCOMROOT_PROD, '{valid?fmt=%Y%m%d}', 'wgrbbul',
                    'nohrsc_snowfall',
                    'sfav2_CONUS_24h_{valid?fmt=%Y%m%d%H}_grid184.grb2'
                )
                VERIF_CASE_STEP_nohrsc_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'nohrsc'
                )
                nohrsc_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_nohrsc_dir,
                    'nohrsc.24H.{valid?fmt=%Y%m%d%H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_nohrsc_dir):
                    os.makedirs(VERIF_CASE_STEP_nohrsc_dir)
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time, nohrsc_source_file_format,
                    nohrsc_dest_file_format
                )
            elif VERIF_CASE_STEP_type == 'sst':
                # GHRSST
                VERIF_CASE_STEP_ghrsst_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ghrsst'
                )
                if not os.path.exists(VERIF_CASE_STEP_ghrsst_dir):
                    os.makedirs(VERIF_CASE_STEP_ghrsst_dir)
            elif VERIF_CASE_STEP_type == 'sea_ice':
                # OSI_SAF
                VERIF_CASE_STEP_osi_saf_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'osi_saf'
                )
                if not os.path.exists(VERIF_CASE_STEP_osi_saf_dir):
                    os.makedirs(VERIF_CASE_STEP_osi_saf_dir)
                # SMOS
                VERIF_CASE_STEP_smos_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'smos'
                )
                if not os.path.exists(VERIF_CASE_STEP_smos_dir):
                    os.makedirs(VERIF_CASE_STEP_smos_dir)
                # NASA Icebridge
                VERIF_CASE_STEP_nasa_icebridge_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'nasa_icebridge'
                )
                if not os.path.exists(VERIF_CASE_STEP_nasa_icebridge_dir):
                    os.makedirs(VERIF_CASE_STEP_nasa_icebridge_dir)
                # YOPP
                VERIF_CASE_STEP_yopp_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'yopp'
                )
                if not os.path.exists(VERIF_CASE_STEP_yopp_dir):
                    os.makedirs(VERIF_CASE_STEP_yopp_dir)
                #OSTIA
                VERIF_CASE_STEP_ostia_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ostia'
                )
                if not os.path.exists(VERIF_CASE_STEP_ostia_dir):
                    os.makedirs(VERIF_CASE_STEP_ostia_dir)
                # GIOMAS
                VERIF_CASE_STEP_giomas_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'giomas'
                )
                if not os.path.exists(VERIF_CASE_STEP_giomas_dir):
                    os.makedirs(VERIF_CASE_STEP_giomas_dir)
            elif VERIF_CASE_STEP_type == 'ozone':
                # OMI
                VERIF_CASE_STEP_omi_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'omi'
                )
                if not os.path.exists(VERIF_CASE_STEP_omi_dir):
                    os.makedirs(VERIF_CASE_STEP_omi_dir)
                # TROPOMI
                VERIF_CASE_STEP_tropomi_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'tropomi'
                )
                if not os.path.exists(VERIF_CASE_STEP_tropomi_dir):
                    os.makedirs(VERIF_CASE_STEP_tropomi_dir)
                # OMPS
                VERIF_CASE_STEP_omps_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'omps'
                )
                if not os.path.exists(VERIF_CASE_STEP_omps_dir):
                    os.makedirs(VERIF_CASE_STEP_omps_dir)
            elif VERIF_CASE_STEP_type == 'flux':
                # ALEXI
                VERIF_CASE_STEP_alexi_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'alexi'
                )
                if not os.path.exists(VERIF_CASE_STEP_alexi_dir):
                    os.makedirs(VERIF_CASE_STEP_alexi_dir)
elif VERIF_CASE_STEP == 'grid2obs_stats':
    # Read in VERIF_CASE_STEP related environment variables
    # Get model forecast and truth files for each option in VERIF_CASE_STEP_type_list
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +VERIF_CASE_STEP_type)
        # Set valid hours
        if VERIF_CASE_STEP_type in ['pres_levs', 'sfc']:
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
            ].split(' ')
        # Set cycle hours
        VERIF_CASE_STEP_type_cycle_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_cycle_list'
        ].split(' ')
        # Set forecast hours
        VERIF_CASE_STEP_type_fhr_min = (
            os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_min']
        )
        VERIF_CASE_STEP_type_fhr_max = (
            os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_max']
        )
        VERIF_CASE_STEP_type_fhr_inc = (
            os.environ[VERIF_CASE_STEP_abbrev_type+'_fhr_inc']
        )
        VERIF_CASE_STEP_type_fhr_list = list(
            range(int(VERIF_CASE_STEP_type_fhr_min),
                  int(VERIF_CASE_STEP_type_fhr_max)
                  +int(VERIF_CASE_STEP_type_fhr_inc),
                  int(VERIF_CASE_STEP_type_fhr_inc))
        )
        # Get time information
        VERIF_CASE_STEP_type_time_info_dict = gda_util.get_time_info(
            start_date, end_date, 'VALID', VERIF_CASE_STEP_type_cycle_list,
            VERIF_CASE_STEP_type_valid_hr_list, VERIF_CASE_STEP_type_fhr_list
        )
        # Get forecast files for each model
        VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
        VERIF_CASE_STEP_type_valid_time_list = []
        for time in VERIF_CASE_STEP_type_time_info_dict:
            if time['valid_time'] not in VERIF_CASE_STEP_type_valid_time_list:
                VERIF_CASE_STEP_type_valid_time_list.append(time['valid_time'])
            for model_idx in range(len(model_list)):
                model = model_list[model_idx]
                model_file_format = model_file_format_list[model_idx]
                VERIF_CASE_STEP_model_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, model
                )
                model_fcst_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_model_dir,
                    model+'.'+'{init?fmt=%Y%m%d%H}.f{lead?fmt=%3H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_model_dir):
                    os.makedirs(VERIF_CASE_STEP_model_dir)
                gda_util.get_model_file(
                    time['valid_time'], time['init_time'],
                    time['forecast_hour'], model_file_format,
                    model_fcst_dest_file_format
                )
                if VERIF_CASE_STEP_type == 'sfc':
                    # Get previous day for 2 meter
                    # Temperature Anomaly verification
                    gda_util.get_model_file(
                        time['valid_time'] - datetime.timedelta(days=1),
                        time['init_time'] - datetime.timedelta(days=1),
                        time['forecast_hour'], model_file_format,
                        model_fcst_dest_file_format
                    )
        # Get truth files
        for VERIF_CASE_STEP_type_valid_time \
                in VERIF_CASE_STEP_type_valid_time_list:
            if VERIF_CASE_STEP_type in ['pres_levs', 'sfc']:
                # GDAS prepbufr
                if VERIF_CASE_STEP_type_valid_time.strftime('%H') \
                        in ['00', '06', '12', '18']:
                    gdas_source_file_format = os.path.join(
                        COMROOT_PROD, 'obsproc', obsproc_ver,
                        'gdas.{valid?fmt=%Y%m%d}', '{valid?fmt=%H}', 'atmos',
                        'gdas.t{valid?fmt=%H}z.prepbufr'
                    )
                    VERIF_CASE_STEP_gdas_dir = os.path.join(
                        VERIF_CASE_STEP_data_dir, 'gdas'
                    )
                    gdas_dest_file_format = os.path.join(
                        VERIF_CASE_STEP_gdas_dir,
                        'prepbufr.gdas.{valid?fmt=%Y%m%d%H}'
                    )
                    if not os.path.exists(VERIF_CASE_STEP_gdas_dir):
                        os.makedirs(VERIF_CASE_STEP_gdas_dir)
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time,
                        gdas_source_file_format,
                        gdas_dest_file_format
                    )
            if VERIF_CASE_STEP_type == 'sfc':
                # NAM prepbufr
                VERIF_CASE_STEP_nam_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'nam'
                )
                nam_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_nam_dir,
                    'prepbufr.nam.{valid?fmt=%Y%m%d%H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_nam_dir):
                    os.makedirs(VERIF_CASE_STEP_nam_dir)
                if VERIF_CASE_STEP_type_valid_time.strftime('%H') \
                        in ['00', '06', '12', '18']:
                    nam_source_file_format = os.path.join(
                        COMROOT_PROD, 'obsproc', obsproc_ver,
                        'nam.{valid?fmt=%Y%m%d}',
                        'nam.t{valid?fmt=%H}z.prepbufr.tm00'
                    )
                elif VERIF_CASE_STEP_type_valid_time.strftime('%H') \
                        in ['03', '09', '15', '21']:
                    nam_source_file_format = os.path.join(
                        COMROOT_PROD, 'obsproc', obsproc_ver,
                        'nam.'
                        +(VERIF_CASE_STEP_type_valid_time
                          +datetime.timedelta(hours=3)).strftime('%Y%m%d'),
                        'nam.t'
                        +(VERIF_CASE_STEP_type_valid_time
                          +datetime.timedelta(hours=3)).strftime('%H')
                        +'z.prepbufr.tm03'
                    )
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time,
                    nam_source_file_format, nam_dest_file_format
                )
                # Get previous day for 2 meter
                # Temperature Anomaly verification
                if VERIF_CASE_STEP_type_valid_time.strftime('%H') \
                        in ['00', '06', '12', '18']:
                    nam_source_file_format = os.path.join(
                        COMROOT_PROD, 'obsproc', obsproc_ver,
                        'nam.{valid?fmt=%Y%m%d}',
                        'nam.t{valid?fmt=%H}z.prepbufr.tm00'
                    )
                elif VERIF_CASE_STEP_type_valid_time.strftime('%H') \
                        in ['03', '09', '15', '21']:
                    nam_source_file_format = os.path.join(
                        COMROOT_PROD, 'obsproc', obsproc_ver,
                        'nam.'
                        +(VERIF_CASE_STEP_type_valid_time
                          -datetime.timedelta(hours=21)).strftime('%Y%m%d'),
                        'nam.t'
                        +(VERIF_CASE_STEP_type_valid_time
                          -datetime.timedelta(hours=21)).strftime('%H')
                        +'z.prepbufr.tm03'
                    ) 
                gda_util.get_truth_file(
                    (VERIF_CASE_STEP_type_valid_time 
                    - datetime.timedelta(days=1)),
                    nam_source_file_format, nam_dest_file_format
                )
                # RAP prepbufr
                rap_source_file_format = os.path.join(
                    COMROOT_PROD, 'obsproc', obsproc_ver,
                    'rap_p.{valid?fmt=%Y%m%d}',
                    'rap_p.t{valid?fmt=%H}z.prepbufr.tm00'
                )
                VERIF_CASE_STEP_rap_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'rap'
                )
                rap_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_rap_dir,
                    'prepbufr.rap.{valid?fmt=%Y%m%d%H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_rap_dir):
                    os.makedirs(VERIF_CASE_STEP_rap_dir)
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time,
                    rap_source_file_format, rap_dest_file_format
                )
                # Get previous day for 2 meter
                # Temperature Anomaly verification
                gda_util.get_truth_file(
                    (VERIF_CASE_STEP_type_valid_time
                     - datetime.timedelta(days=1)),
                    rap_source_file_format, rap_dest_file_format
                )
            elif VERIF_CASE_STEP_type == 'sea_ice':
                # IABP
                VERIF_CASE_STEP_iabp_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'iabp'
                )
                if not os.path.exists(VERIF_CASE_STEP_iabp_dir):
                    os.makedirs(VERIF_CASE_STEP_iabp_dir)

print("END: "+os.path.basename(__file__))
