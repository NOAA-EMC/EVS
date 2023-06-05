#!/usr/bin/env python3
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
NET = os.environ['NET']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
DATA = os.environ['DATA']
COMIN = os.environ['COMIN']
model_list = os.environ['model_list'].split(' ')
model_evs_data_dir_list = os.environ['model_evs_data_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
USER = os.environ['USER']
evs_run_mode = os.environ['evs_run_mode']
COMINnohrsc = os.environ['COMINnohrsc']
if STEP == 'stats':
    COMINccpa = os.environ['COMINccpa']
    COMINobsproc = os.environ['COMINobsproc']
    COMINosi_saf = os.environ['COMINosi_saf']
    COMINghrsst_ospo = os.environ['COMINghrsst_ospo']
    COMINget_d = os.environ['COMINget_d']
if evs_run_mode != 'production':
    QUEUESERV = os.environ['QUEUESERV']
    ACCOUNT = os.environ['ACCOUNT']
    machine = os.environ['machine']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP

# Set archive paths
if evs_run_mode != 'production':
    archive_obs_data_dir = os.environ['archive_obs_data_dir']
else:
    archive_obs_data_dir = '/dev/null'

# Make sure in right working directory
cwd = os.getcwd()
if cwd != DATA:
    os.chdir(DATA)

if VERIF_CASE_STEP == 'grid2grid_stats':
    # Get model forecast and truth files for
    # each option in VERIF_CASE_STEP_type_list
    # Read in VERIF_CASE_STEP related environment variables
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        print("----> Getting files for "+VERIF_CASE_STEP+" "
              +VERIF_CASE_STEP_type)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +VERIF_CASE_STEP_type)
        # Read in VERIF_CASE_STEP_type related environment variables
        if VERIF_CASE_STEP_type == 'pres_levs':
            VERIF_CASE_STEP_pres_levs_truth_format_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_pres_levs_truth_format_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type in ['precip_accum24hr',
                                      'precip_accum3hr']:
            VERIF_CASE_STEP_precip_accum_file_format_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_'+VERIF_CASE_STEP_type
                +'_file_format_list'
            ].split(' ')
            VERIF_CASE_STEP_precip_accum_file_accum_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_'+VERIF_CASE_STEP_type
                +'_file_accum_list'
            ].split(' ')
        # Set valid hours
        if VERIF_CASE_STEP_type == 'flux':
            (GET_D_valid_hr_start, GET_D_valid_hr_end,
             GET_D_valid_hr_inc) = gda_util.get_obs_valid_hrs(
                 'GET_D'
            )
            GET_D_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    GET_D_valid_hr_start,
                    GET_D_valid_hr_end+GET_D_valid_hr_inc,
                    GET_D_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = GET_D_valid_hr_list
        elif VERIF_CASE_STEP_type in ['pres_levs', 'means']: 
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type == 'precip_accum24hr':
            (CCPA24hr_valid_hr_start, CCPA24hr_valid_hr_end,
             CCPA24hr_valid_hr_inc) = gda_util.get_obs_valid_hrs(
                 '24hrCCPA'
            )
            CCPA24hr_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    CCPA24hr_valid_hr_start,
                    CCPA24hr_valid_hr_end+CCPA24hr_valid_hr_inc,
                    CCPA24hr_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = CCPA24hr_valid_hr_list
        elif VERIF_CASE_STEP_type == 'precip_accum3hr':
            (CCPA3hr_valid_hr_start, CCPA3hr_valid_hr_end,
             CCPA3hr_valid_hr_inc) = gda_util.get_obs_valid_hrs(
                 '3hrCCPA'
            )
            CCPA3hr_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    CCPA3hr_valid_hr_start,
                    CCPA3hr_valid_hr_end+CCPA3hr_valid_hr_inc,
                    CCPA3hr_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = CCPA3hr_valid_hr_list
        elif VERIF_CASE_STEP_type == 'snow':
            (NOHRSC24hr_valid_hr_start, NOHRSC24hr_valid_hr_end,
             NOHRSC24hr_valid_hr_inc) = gda_util.get_obs_valid_hrs(
                 '24hrNOHRSC'
            )
            NOHRSC24hr_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    NOHRSC24hr_valid_hr_start,
                    NOHRSC24hr_valid_hr_end+NOHRSC24hr_valid_hr_inc,
                    NOHRSC24hr_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = NOHRSC24hr_valid_hr_list
        elif VERIF_CASE_STEP_type == 'sea_ice':
            (OSI_SAF_valid_hr_start, OSI_SAF_valid_hr_end,
             OSI_SAF_valid_hr_inc) = gda_util.get_obs_valid_hrs(
                 'OSI-SAF'
            )
            OSI_SAF_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    OSI_SAF_valid_hr_start,
                    OSI_SAF_valid_hr_end+OSI_SAF_valid_hr_inc,
                    OSI_SAF_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = OSI_SAF_valid_hr_list
        elif VERIF_CASE_STEP_type == 'sst':
            (GHRSST_OSPO_valid_hr_start, GHRSST_OSPO_valid_hr_end,
             GHRSST_OSPO_valid_hr_inc) = gda_util.get_obs_valid_hrs(
                 'GHRSST-OSPO'
            )
            GHRSST_OSPO_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    GHRSST_OSPO_valid_hr_start,
                    GHRSST_OSPO_valid_hr_end+GHRSST_OSPO_valid_hr_inc,
                    GHRSST_OSPO_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = GHRSST_OSPO_valid_hr_list
        else:
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        # Set initialization hours
        VERIF_CASE_STEP_type_init_hr_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_init_hr_list'
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
            start_date, end_date, 'VALID', VERIF_CASE_STEP_type_init_hr_list,
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
                if VERIF_CASE_STEP_type in ['precip_accum24hr',
                                            'precip_accum3hr']:
                    model_file_format = (
                        VERIF_CASE_STEP_precip_accum_file_format_list\
                        [model_idx]
                    )
                    model_accum = (
                        VERIF_CASE_STEP_precip_accum_file_accum_list\
                        [model_idx]
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
                    model_fcst_dest_file_format,
                )
                if VERIF_CASE_STEP_type == 'flux':
                    # Get files for flux daily averages, same init
                    nf = 1
                    while nf <= 4:
                        minus_hr = nf * 6
                        fhr = int(time['forecast_hour'])-minus_hr
                        if fhr >= 0:
                            gda_util.get_model_file(
                                time['valid_time'] \
                                - datetime.timedelta(hours=minus_hr),
                                time['init_time'],
                                str(fhr),
                                model_file_format,
                                model_fcst_dest_file_format,
                            )
                        nf+=1
                elif VERIF_CASE_STEP_type in ['precip_accum24hr',
                                              'precip_accum3hr']:
                    if VERIF_CASE_STEP_type == 'precip_accum24hr':
                        accum = 24
                    elif VERIF_CASE_STEP_type == 'precip_accum3hr':
                        accum = 3
                    # Get for accumulations
                    fhrs_accum_list = []
                    if model_accum == 'continuous':
                        nfiles_accum = 2
                        fhrs_accum_list.append(
                            time['forecast_hour']
                        )
                        if int(time['forecast_hour']) - accum > 0:
                            fhrs_accum_list.append(
                                str(int(time['forecast_hour']) - accum)
                            )
                    elif int(model_accum) == accum:
                        nfiles_accum = 1
                        fhrs_accum_list.append(
                            time['forecast_hour']
                        )
                    elif int(model_accum) < accum:
                        nfiles_accum = int(accum/int(model_accum))
                        nf = 1
                        while nf <= nfiles_accum:
                            fhr_nf = (int(time['forecast_hour'])
                                      -(nf-1)*int(model_accum))
                            if fhr_nf > 0:
                                fhrs_accum_list.append(
                                    str(fhr_nf)
                                )
                            nf+=1
                    elif int(model_accum) > accum:
                        print("WARNING: the model precip file "
                              "accumulation for "+model+" ("
                              +model_file_format+") is greater than "
                              +"the verifying accumulation of "+str(accum)
                              +" hours, please remove")
                        sys.exit(1)
                    if len(fhrs_accum_list) == nfiles_accum:
                        for fhr in fhrs_accum_list:
                            fhr_diff = (int(time['forecast_hour'])
                                        -int(fhr))
                            gda_util.get_model_file(
                                (time['valid_time']
                                 - datetime.timedelta(hours=fhr_diff)),
                                time['init_time'],
                                fhr, model_file_format,
                                model_fcst_dest_file_format,
                            )
                elif VERIF_CASE_STEP_type == 'pres_levs':
                    # Get files for anomaly daily averages, same init
                    # get for 00Z and 12Z only
                    if time['init_time'].strftime('%H') in ['00', '12'] \
                            and int(time['forecast_hour']) % 24 == 0:
                        fhr = int(time['forecast_hour'])-12
                        if fhr >= 0:
                            gda_util.get_model_file(
                                time['valid_time'] \
                                - datetime.timedelta(hours=12),
                                time['init_time'],
                                str(fhr),
                                model_file_format,
                                model_fcst_dest_file_format,
                            )
                elif VERIF_CASE_STEP_type == 'sea_ice':
                    # OSI-SAF spans PDYm1 00Z to PDY 00Z
                    nf = 0
                    while nf <= 4:
                        if int(time['forecast_hour'])-(6*nf) >= 0:
                            gda_util.get_model_file(
                                (time['valid_time']
                                 -datetime.timedelta(hours=6*nf)),
                                time['init_time'],
                                str(int(time['forecast_hour'])-(6*nf)),
                                model_file_format, model_fcst_dest_file_format,
                            )
                        nf+=1
                elif VERIF_CASE_STEP_type == 'snow':
                    # Get for 24 hour accumulations
                    if int(time['forecast_hour']) - 24 >= 0:
                        gda_util.get_model_file(
                            time['valid_time'], time['init_time'],
                            str(int(time['forecast_hour']) - 24),
                            model_file_format, model_fcst_dest_file_format,
                        )
                elif VERIF_CASE_STEP_type == 'sst':
                    # GHRSST OSPO spans PDYm1 00Z to PDY 00Z
                    nf = 0
                    while nf <= 4:
                        if int(time['forecast_hour'])-(6*nf) >= 0:
                            gda_util.get_model_file(
                                (time['valid_time']
                                 -datetime.timedelta(hours=6*nf)),
                                time['init_time'],
                                str(int(time['forecast_hour'])-(6*nf)),
                                model_file_format, model_fcst_dest_file_format,
                            )
                        nf+=1
        # Get truth files
        for VERIF_CASE_STEP_type_valid_time \
                in VERIF_CASE_STEP_type_valid_time_list:
            if VERIF_CASE_STEP_type == 'flux':
                # GET-D
                get_d_prod_file_format = os.path.join(
                    COMINget_d, 'prep',
                    COMPONENT, RUN+'.{valid?fmt=%Y%m%d}',
                    'get_d', 'get_d.'
                    +'{valid_shift?fmt=%Y%m%d%H?shift='
                    +'-24}to'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                get_d_arch_file_format = os.path.join(
                    archive_obs_data_dir, 'get_d',
                    'GETDL3_DAL_CONUS_{valid?fmt=%Y%j}_1.0.nc'
                )
                VERIF_CASE_STEP_get_d_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'get_d'
                )
                get_d_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_get_d_dir,
                    'get_d.{valid_shift?fmt=%Y%m%d%H?shift='
                    +'-24}to{valid?fmt=%Y%m%d%H}.nc'
                )
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time, 'GET-D',
                    get_d_prod_file_format, get_d_arch_file_format,
                    evs_run_mode, get_d_dest_file_format
                )
            elif VERIF_CASE_STEP_type in ['precip_accum24hr',
                                          'precip_accum3hr']:
                # CCPA
                if VERIF_CASE_STEP_type == 'precip_accum24hr':
                    ccpa_accum_intvl = 6
                    accum = 24
                elif VERIF_CASE_STEP_type == 'precip_accum3hr':
                    ccpa_accum_intvl = 3
                    accum = 3
                VERIF_CASE_STEP_ccpa_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ccpa'
                )
                ccpa_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_ccpa_dir, 'ccpa.'+str(ccpa_accum_intvl)
                    +'H.{valid?fmt=%Y%m%d%H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_ccpa_dir):
                    os.makedirs(VERIF_CASE_STEP_ccpa_dir)
                accum_valid_start = (VERIF_CASE_STEP_type_valid_time -
                                     datetime.timedelta(hours=accum))
                accum_valid_end = VERIF_CASE_STEP_type_valid_time
                accum_valid = accum_valid_end
                while accum_valid > accum_valid_start:
                    if VERIF_CASE_STEP_type == 'precip_accum3hr' \
                            and int(accum_valid.strftime('%H'))%6 != 0:
                        ccpa_prod_file_format = os.path.join(
                            COMINccpa, 'ccpa.{valid_shift?fmt=%Y%m%d?shift=3}',
                           '{valid_shift?fmt=%H?shift=3}',
                           'ccpa.t{valid?fmt=%H}z.'
                           +str(ccpa_accum_intvl).zfill(2)+'h.hrap.conus.gb2'
                        )
                    else:
                        ccpa_prod_file_format = os.path.join(
                            COMINccpa, 'ccpa.{valid?fmt=%Y%m%d}',
                           '{valid?fmt=%H}', 'ccpa.t{valid?fmt=%H}z.'
                           +str(ccpa_accum_intvl).zfill(2)+'h.hrap.conus.gb2'
                        )
                    ccpa_arch_file_format = os.path.join(
                        archive_obs_data_dir, 'ccpa_accum'
                        +str(ccpa_accum_intvl)+'hr',
                        'ccpa.hrap.{valid?fmt=%Y%m%d%H}.'
                        +str(ccpa_accum_intvl)+'h'
                    )
                    gda_util.get_truth_file(
                        accum_valid, 'CCPA Accum '
                        +str(ccpa_accum_intvl).zfill(2)+'hr',
                        ccpa_prod_file_format, ccpa_arch_file_format,
                        evs_run_mode, ccpa_dest_file_format
                    )
                    accum_valid = (accum_valid -
                                   datetime.timedelta(hours=ccpa_accum_intvl))
            elif VERIF_CASE_STEP_type == 'pres_levs':
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
                        pres_levs_dest_file_format,
                    )
            elif VERIF_CASE_STEP_type == 'sea_ice':
                # OSI_SAF
                VERIF_CASE_STEP_osi_saf_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'osi_saf'
                )
                if not os.path.exists(VERIF_CASE_STEP_osi_saf_dir):
                    os.makedirs(VERIF_CASE_STEP_osi_saf_dir)
                for hem in ['nh', 'sh']:
                    osi_saf_hem_prod_file_format = os.path.join(
                        COMINosi_saf, 'prep',
                        COMPONENT, RUN+'.{valid?fmt=%Y%m%d}',
                        'osi_saf', 'osi_saf.multi.'+hem+'.'
                        +'{valid_shift?fmt=%Y%m%d%H?shift=-24}to'
                        +'{valid?fmt=%Y%m%d%H}.nc'
                    )
                    osi_saf_hem_arch_file_format = os.path.join(
                        archive_obs_data_dir, 'osi_saf',
                        'osi_saf.multi.'+hem+'.'
                        +'{valid_shift?fmt=%Y%m%d%H?shift=-24}to'
                        +'{valid?fmt=%Y%m%d%H}.nc'
                    )
                    osi_saf_hem_dest_file_format = os.path.join(
                        VERIF_CASE_STEP_osi_saf_dir,
                        'osi_saf.multi.'+hem+'.'
                        +'{valid_shift?fmt=%Y%m%d%H?shift=-24}to'
                        +'{valid?fmt=%Y%m%d%H}.nc'
                    )
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time,
                        f"OSI-SAF {hem.upper()}",
                        osi_saf_hem_prod_file_format,
                        osi_saf_hem_arch_file_format, evs_run_mode,
                        osi_saf_hem_dest_file_format
                    )
            elif VERIF_CASE_STEP_type == 'snow':
                # NOHRSC
                nohrsc_prod_file_format = os.path.join(
                    COMINnohrsc, '{valid?fmt=%Y%m%d}', 'wgrbbul',
                    'nohrsc_snowfall',
                    'sfav2_CONUS_24h_{valid?fmt=%Y%m%d%H}_grid184.grb2'
                )
                nohrsc_arch_file_format = os.path.join(
                    archive_obs_data_dir, 'nohrsc_accum24hr',
                    'nohrsc.{valid?fmt=%Y%m%d%H}.24h'
                )
                VERIF_CASE_STEP_nohrsc_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'nohrsc'
                )
                nohrsc_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_nohrsc_dir,
                    'nohrsc.24H.{valid?fmt=%Y%m%d%H}'
                )
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time, 'NOHRSC Accum 24hr',
                    nohrsc_prod_file_format, nohrsc_arch_file_format,
                    evs_run_mode, nohrsc_dest_file_format
                )
            elif VERIF_CASE_STEP_type == 'sst':
                # GHRSST OSPO
                ghrsst_ospo_prod_file_format = os.path.join(
                    COMINghrsst_ospo, 'prep',
                    COMPONENT, RUN+'.{valid?fmt=%Y%m%d}', 'ghrsst_ospo',
                    'ghrsst_ospo.{valid_shift?fmt=%Y%m%d%H?shift=-24}to'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                ghrsst_ospo_arch_file_format = os.path.join(
                    archive_obs_data_dir, 'ghrsst_ospo',
                    'ghrsst_ospo.{valid_shift?fmt=%Y%m%d%H?shift=-24}to'
                    +'{valid?fmt=%Y%m%d%H}.nc'
                )
                VERIF_CASE_STEP_ghrsst_ospo_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ghrsst_ospo'
                )
                if not os.path.exists(VERIF_CASE_STEP_ghrsst_ospo_dir):
                    os.makedirs(VERIF_CASE_STEP_ghrsst_ospo_dir)
                ghrsst_ospo_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_ghrsst_ospo_dir,
                    'ghrsst_ospo.{valid_shift?fmt=%Y%m%d%H?shift=-24}to'
                     +'{valid?fmt=%Y%m%d%H}.nc'
                )
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time, 'GHRSST OSPO',
                    ghrsst_ospo_prod_file_format, ghrsst_ospo_arch_file_format,
                    evs_run_mode, ghrsst_ospo_dest_file_format
                )
elif VERIF_CASE_STEP == 'grid2obs_stats':
    # Read in VERIF_CASE_STEP related environment variables
    # Get model forecast and truth files for each option in VERIF_CASE_STEP_type_list
    for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
        print("----> Getting files for "+VERIF_CASE_STEP+" "
              +VERIF_CASE_STEP_type)
        VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                       +VERIF_CASE_STEP_type)
        # Read in VERIF_CASE_STEP_type related environment variables
        # Set valid hours
        if VERIF_CASE_STEP_type in ['pres_levs', 'sfc', 'ptype']:
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
            ].split(' ')
        # Set initialization hours
        VERIF_CASE_STEP_type_init_hr_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_init_hr_list'
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
            start_date, end_date, 'VALID', VERIF_CASE_STEP_type_init_hr_list,
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
                    model_fcst_dest_file_format,
                )
                if VERIF_CASE_STEP_type == 'sfc':
                    # Get files for anomaly daily averages, same init
                    if int(time['forecast_hour']) % 24 == 0:
                        nf = 1
                        while nf <= 3:
                            minus_hr = nf * 6
                            fhr = int(time['forecast_hour'])-minus_hr
                            if fhr >= 0:
                                gda_util.get_model_file(
                                    time['valid_time'] \
                                    - datetime.timedelta(hours=minus_hr),
                                    time['init_time'],
                                    str(fhr),
                                    model_file_format,
                                    model_fcst_dest_file_format,
                                )
                                gda_util.get_model_file(
                                    time['valid_time'],
                                    time['init_time'] \
                                    - datetime.timedelta(hours=minus_hr),
                                    str(fhr),
                                    model_file_format,
                                    model_fcst_dest_file_format,
                                )
                            nf+=1
        # Get truth files
        for VERIF_CASE_STEP_type_valid_time \
                in VERIF_CASE_STEP_type_valid_time_list:
            if VERIF_CASE_STEP_type in ['pres_levs', 'sfc']:
                # GDAS prepbufr
                if VERIF_CASE_STEP_type_valid_time.strftime('%H') \
                        in ['00', '06', '12', '18']:
                    gdas_prod_file_format = os.path.join(
                        COMINobsproc, 'gdas.{valid?fmt=%Y%m%d}',
                        '{valid?fmt=%H}', 'atmos',
                        'gdas.t{valid?fmt=%H}z.prepbufr'
                    )
                    gdas_arch_file_format = os.path.join(
                        archive_obs_data_dir, 'prepbufr', 'gdas',
                        'prepbufr.gdas.{valid?fmt=%Y%m%d%H}'
                    )
                    VERIF_CASE_STEP_gdas_dir = os.path.join(
                        VERIF_CASE_STEP_data_dir, 'prepbufr_gdas'
                    )
                    gdas_dest_file_format = os.path.join(
                        VERIF_CASE_STEP_gdas_dir,
                        'prepbufr.gdas.{valid?fmt=%Y%m%d%H}'
                    )
                    if not os.path.exists(VERIF_CASE_STEP_gdas_dir):
                        os.makedirs(VERIF_CASE_STEP_gdas_dir)
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time, 'Prepbufr GDAS',
                        gdas_prod_file_format, gdas_arch_file_format,
                        evs_run_mode, gdas_dest_file_format
                    )
            if VERIF_CASE_STEP_type in ['sfc', 'ptype']:
                # NAM prepbufr
                offset_hr = str(
                    int(VERIF_CASE_STEP_type_valid_time.strftime('%H'))%6
                ).zfill(2)
                offset_valid_time_dt = (
                    VERIF_CASE_STEP_type_valid_time
                    + datetime.timedelta(hours=int(offset_hr))
                )
                nam_prod_file_format = os.path.join(
                    COMINobsproc, 'nam.{valid?fmt=%Y%m%d}',
                    'nam.t{valid?fmt=%H}z.prepbufr.tm'+offset_hr
                )
                nam_prod_file = gda_util.format_filler(
                    nam_prod_file_format, offset_valid_time_dt,
                    offset_valid_time_dt, ['anl'], {}
                )
                nam_arch_file_format = os.path.join(
                    archive_obs_data_dir, 'prepbufr',
                    'nam', 'nam.{valid?fmt=%Y%m%d}',
                    'nam.t{valid?fmt=%H}z.prepbufr.tm'+offset_hr
                )
                nam_arch_file = gda_util.format_filler(
                    nam_arch_file_format, offset_valid_time_dt,
                    offset_valid_time_dt, ['anl'], {}
                )
                VERIF_CASE_STEP_nam_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'prepbufr_nam'
                )
                nam_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_nam_dir,
                    'prepbufr.nam.{valid?fmt=%Y%m%d%H}'
                )
                nam_dest_file = gda_util.format_filler(
                    nam_dest_file_format, VERIF_CASE_STEP_type_valid_time,
                    VERIF_CASE_STEP_type_valid_time, ['anl'], {}
                )
                if not os.path.exists(VERIF_CASE_STEP_nam_dir):
                    os.makedirs(VERIF_CASE_STEP_nam_dir)
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time, 'Prepbufr NAM',
                    nam_prod_file, nam_arch_file, evs_run_mode,
                    nam_dest_file
                )
                # RAP prepbufr
                rap_prod_file_format = os.path.join(
                    COMINobsproc, 'rap.{valid?fmt=%Y%m%d}',
                    'rap.t{valid?fmt=%H}z.prepbufr.tm00'
                )
                rap_arch_file_format = os.path.join(
                    archive_obs_data_dir, 'prepbufr',
                    'rap', 'rap.{valid?fmt=%Y%m%d}',
                    'rap.t{valid?fmt=%H}z.prepbufr.tm00'
                )
                VERIF_CASE_STEP_rap_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'prepbufr_rap'
                )
                rap_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_rap_dir,
                    'prepbufr.rap.{valid?fmt=%Y%m%d%H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_rap_dir):
                    os.makedirs(VERIF_CASE_STEP_rap_dir)
                gda_util.get_truth_file(
                    VERIF_CASE_STEP_type_valid_time, 'Prepbufr RAP',
                    rap_prod_file_format, rap_arch_file_format,
                    evs_run_mode, rap_dest_file_format
                )
elif STEP == 'plots' :
    # Read in VERIF_CASE_STEP related environment variables
    # Get model stat files
    start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
    VERIF_CASE_STEP_data_dir = os.path.join(DATA, VERIF_CASE_STEP, 'data')
    date_type = 'VALID'
    for model_idx in range(len(model_list)):
        model = model_list[model_idx]
        model_evs_data_dir = model_evs_data_dir_list[model_idx]
        date_dt = start_date_dt
        while date_dt <= end_date_dt:
            if date_type == 'VALID':
                if evs_run_mode == 'production':
                    source_model_date_stat_file = os.path.join(
                        model_evs_data_dir+'.'+date_dt.strftime('%Y%m%d'),
                        'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.'
                        +'v'+date_dt.strftime('%Y%m%d')+'.stat'
                    )
                else:
                    source_model_date_stat_file = os.path.join(
                        model_evs_data_dir, 'evs_data',
                        COMPONENT, RUN, VERIF_CASE, model,
                        model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                    )
                dest_model_date_stat_file = os.path.join(
                    VERIF_CASE_STEP_data_dir, model,
                    model+'_v'+date_dt.strftime('%Y%m%d')+'.stat'
                )
            if not os.path.exists(dest_model_date_stat_file):
                if os.path.exists(source_model_date_stat_file):
                    print("Linking "+source_model_date_stat_file+" to "
                          +dest_model_date_stat_file)
                    os.symlink(source_model_date_stat_file,
                               dest_model_date_stat_file)
                else:
                    print("WARNING: "+source_model_date_stat_file+" "
                          +"DOES NOT EXIST")
            date_dt = date_dt + datetime.timedelta(days=1)
    # Get model pcp_combine files from COMIN
    if VERIF_CASE == 'grid2grid' and 'precip' in VERIF_CASE_STEP_type_list:
        (CCPA24hr_valid_hr_start, CCPA24hr_valid_hr_end,
         CCPA24hr_valid_hr_inc) = gda_util.get_obs_valid_hrs(
             '24hrCCPA'
        )
        CCPA24hr_valid_hr_list = [
            str(x).zfill(2) for x in range(
                CCPA24hr_valid_hr_start,
                CCPA24hr_valid_hr_end+CCPA24hr_valid_hr_inc,
                CCPA24hr_valid_hr_inc
            )
        ]
        VERIF_CASE_STEP_precip_fhr_min = (
            os.environ[VERIF_CASE_STEP_abbrev+'_precip_fhr_min']
        )
        VERIF_CASE_STEP_precip_fhr_max = (
            os.environ[VERIF_CASE_STEP_abbrev+'_precip_fhr_max']
        )
        VERIF_CASE_STEP_precip_fhr_inc = (
            os.environ[VERIF_CASE_STEP_abbrev+'_precip_fhr_inc']
        )
        VERIF_CASE_STEP_precip_fhr_list = list(
            range(int(VERIF_CASE_STEP_precip_fhr_min),
                  int(VERIF_CASE_STEP_precip_fhr_max)
                  +int(VERIF_CASE_STEP_precip_fhr_inc),
                  int(VERIF_CASE_STEP_precip_fhr_inc))
        )
        COMINccpa = os.path.join(
            COMIN, 'stats', COMPONENT,
            RUN+'.'+end_date_dt.strftime('%Y%m%d'),
            'ccpa', 'grid2grid'
        )
        source_ccpa_pcp_combine_file = os.path.join(
            COMINccpa, 'pcp_combine_precip_24hrCCPA_valid'
            +end_date_dt.strftime('%Y%m%d')+CCPA24hr_valid_hr_list[0]+'.nc'
        )
        dest_ccpa_pcp_combine_file = os.path.join(
            VERIF_CASE_STEP_data_dir, 'ccpa',
            'ccpa_precip_24hrAccum_valid'
            +end_date_dt.strftime('%Y%m%d')+CCPA24hr_valid_hr_list[0]+'.nc'
        )
        if not os.path.exists(dest_ccpa_pcp_combine_file):
            if os.path.exists(source_ccpa_pcp_combine_file):
                print("Linking "+source_ccpa_pcp_combine_file+" "
                      +"to "+dest_ccpa_pcp_combine_file)
                os.symlink(source_ccpa_pcp_combine_file,
                           dest_ccpa_pcp_combine_file)
            else:
                print("WARNING: "+source_ccpa_pcp_combine_file+" "
                       +"DOES NOT EXIST")
        for model_idx in range(len(model_list)):
            model = model_list[model_idx]
            COMINmodel = os.path.join(
                COMIN, 'stats', COMPONENT,
                RUN+'.'+end_date_dt.strftime('%Y%m%d'),
                model, 'grid2grid'
            )
            for fhr in VERIF_CASE_STEP_precip_fhr_list:
                init_dt = (
                    end_date_dt
                    + datetime.timedelta(hours=int(CCPA24hr_valid_hr_list[0]))
                )- datetime.timedelta(hours=fhr)
                source_model_fhr_pcp_combine_file = os.path.join(
                    COMINmodel, 'pcp_combine_precip_accum24hr_24hrAccum_init'
                    +init_dt.strftime('%Y%m%d%H')+'_fhr'+str(fhr).zfill(3)+'.nc'
                )
                dest_model_fhr_pcp_combine_file = os.path.join(
                    VERIF_CASE_STEP_data_dir, model,
                    model+'_precip_accum24hr_24hrAccum_init'
                    +init_dt.strftime('%Y%m%d%H')+'_fhr'+str(fhr).zfill(3)+'.nc'
                )
                if not os.path.exists(dest_model_fhr_pcp_combine_file):
                    if os.path.exists(source_model_fhr_pcp_combine_file):
                        print("Linking "+source_model_fhr_pcp_combine_file+" "
                              +"to "+dest_model_fhr_pcp_combine_file)
                        os.symlink(source_model_fhr_pcp_combine_file,
                                   dest_model_fhr_pcp_combine_file)
                    else:
                        print("WARNING: "+source_model_fhr_pcp_combine_file+" "
                              +"DOES NOT EXIST")
    # Get NOHRSC files from COMINnohrsc
    if VERIF_CASE == 'grid2grid' and 'snow' in VERIF_CASE_STEP_type_list:
        (NOHRSC24hr_valid_hr_start, NOHRSC24hr_valid_hr_end,
         NOHRSC24hr_valid_hr_inc) = gda_util.get_obs_valid_hrs(
            '24hrNOHRSC'
        )
        NOHRSC24hr_valid_hr_list = [
            str(x).zfill(2) for x in range(
                NOHRSC24hr_valid_hr_start,
                NOHRSC24hr_valid_hr_end+NOHRSC24hr_valid_hr_inc,
                NOHRSC24hr_valid_hr_inc
            )
        ]
        source_nohrsc_file = os.path.join(
            COMINnohrsc, end_date_dt.strftime('%Y%m%d'),
            'wgrbbul', 'nohrsc_snowfall',
            'sfav2_CONUS_24h_'+end_date_dt.strftime('%Y%m%d')
            +NOHRSC24hr_valid_hr_list[0]+'_grid184.grb2'
        )
        dest_nohrsc_file = os.path.join(
            VERIF_CASE_STEP_data_dir, 'nohrsc',
            'nohrsc_snow_24hrAccum_valid'
            +end_date_dt.strftime('%Y%m%d')
            +NOHRSC24hr_valid_hr_list[0]+'.grb2'
        )
        if not os.path.exists(dest_nohrsc_file):
            if os.path.exists(source_nohrsc_file):
                print("Linking "+source_nohrsc_file+" "
                      +"to "+dest_nohrsc_file)
                os.symlink(source_nohrsc_file,
                           dest_nohrsc_file)
            else:
                print("WARNING: "+source_nohrsc_file+" "
                       +"DOES NOT EXIST")

print("END: "+os.path.basename(__file__))
