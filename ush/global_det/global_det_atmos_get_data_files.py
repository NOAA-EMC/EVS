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
model_list = os.environ['model_list'].split(' ')
model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
USER = os.environ['USER']
evs_ver = os.environ['evs_ver']
ccpa_ver = os.environ['ccpa_ver']
obsproc_ver = os.environ['obsproc_ver']
evs_run_mode = os.environ['evs_run_mode']
if evs_run_mode != 'production':
    QUEUESERV = os.environ['QUEUESERV']
    ACCOUNT = os.environ['ACCOUNT']
    machine = os.environ['machine']

# Set production data paths
DCOMROOT_PROD = '/lfs/h1/ops/prod/dcom'
DCOMROOT_DEV = '/lfs/h1/ops/dev/dcom'
COMROOT_PROD = '/lfs/h1/ops/prod/com'

# Set archive paths
if evs_run_mode != 'production':
    archive_obs_data_dir = os.environ['archive_obs_data_dir']

# Make sure in right working directory
cwd = os.getcwd()
if cwd != DATA:
    os.chdir(DATA)

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
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
        elif VERIF_CASE_STEP_type == 'precip':
            VERIF_CASE_STEP_precip_file_format_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_precip_file_format_list'
            ].split(' ')
            VERIF_CASE_STEP_precip_file_accum_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_precip_file_accum_list'
            ].split(' ')
        # Set valid hours
        if VERIF_CASE_STEP_type in ['pres_levs', 'means']: 
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type == 'flux':
            VERIF_CASE_STEP_type_valid_hr_list = ['00']
        elif VERIF_CASE_STEP_type == 'precip':
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        elif VERIF_CASE_STEP_type == 'sea_ice':
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        elif VERIF_CASE_STEP_type == 'snow':
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        else:
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
                                model_fcst_dest_file_format
                            )
                        nf+=1
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
                            fhr_diff = (int(time['forecast_hour'])
                                        -int(fhr))
                            gda_util.get_model_file(
                                (time['valid_time']
                                 - datetime.timedelta(hours=fhr_diff)),
                                time['init_time'],
                                fhr, model_file_format,
                                model_fcst_dest_file_format 
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
            if VERIF_CASE_STEP_type == 'flux':
                # GET-D
                get_d_prod_file_format = os.path.join(
                    DCOMROOT_PROD, '{valid?fmt=%Y%m%d}', 'wgrbbul',
                    'get_d', 'GETDL3_DAL_CONUS_{valid?fmt=%Y%j}_1.0.nc'
                )
                get_d_prod_file = gda_util.format_filler(
                    get_d_prod_file_format, VERIF_CASE_STEP_type_valid_time,
                    VERIF_CASE_STEP_type_valid_time, ['anl'], {}
                )
                VERIF_CASE_STEP_get_d_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'get_d'
                )
                get_d_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_get_d_dir,
                    'get_d.24H.{valid?fmt=%Y%m%d%H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_get_d_dir):
                    os.makedirs(VERIF_CASE_STEP_get_d_dir)
                if os.path.exists(get_d_prod_file):
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time,
                        get_d_prod_file_format, get_d_dest_file_format
                    )
                else:
                    if evs_run_mode != 'production':
                        get_d_arch_file_format = os.path.join(
                            archive_obs_data_dir, 'get_d',
                            'GETDL3_DAL_CONUS_{valid?fmt=%Y%j}_1.0.nc'
                        )
                        gda_util.get_truth_file(
                            VERIF_CASE_STEP_type_valid_time,
                            get_d_arch_file_format, get_d_dest_file_format
                        )
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
            elif VERIF_CASE_STEP_type == 'precip':
                # CCPA
                ccpa_prod_file_format = os.path.join(
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
                    ccpa_prod_file = gda_util.format_filler(
                        ccpa_prod_file_format, accum_valid, accum_valid,
                        ['anl'], {}
                    )
                    if os.path.exists(ccpa_prod_file):
                        gda_util.get_truth_file(
                            accum_valid, ccpa_prod_file_format,
                            ccpa_dest_file_format
                        )
                    else:
                        if evs_run_mode != 'production':
                            ccpa_arch_file_format = os.path.join(
                                archive_obs_data_dir, 'ccpa_accum6hr',
                                'ccpa.hrap.{valid?fmt=%Y%m%d%H}.6h'
                            )
                            gda_util.get_truth_file(
                                accum_valid, ccpa_arch_file_format,
                                ccpa_dest_file_format
                            )
                    accum_valid = (accum_valid -
                                   datetime.timedelta(hours=6))
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
                        pres_levs_dest_file_format
                    )
                    # Get previous day for Geopotential
                    # Height Anomaly verification
                    if VERIF_CASE_STEP_type_valid_time.strftime('%H') \
                            in ['00', '12']:
                        gda_util.get_model_file(
                            (VERIF_CASE_STEP_type_valid_time
                             - datetime.timedelta(days=1)),
                            (VERIF_CASE_STEP_type_valid_time
                             - datetime.timedelta(days=1)),
                            'anl', model_truth_file_format,
                            pres_levs_dest_file_format
                        )
            elif VERIF_CASE_STEP_type == 'sea_ice':
                # OSI_SAF
                osi_saf_prod_file_format = os.path.join(
                    COMROOT_PROD, 'evs',  evs_ver, 'prep',
                    COMPONENT, RUN+'.{valid?fmt=%Y%m%d}',
                    'osi_saf', 'osi_saf.multi.{valid?fmt=%Y%m%d%H}_G004.nc'
                )
                osi_saf_prod_file = gda_util.format_filler(
                    osi_saf_prod_file_format, VERIF_CASE_STEP_type_valid_time,
                    VERIF_CASE_STEP_type_valid_time, ['anl'], {}
                )
                VERIF_CASE_STEP_osi_saf_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'osi_saf'
                )
                osi_saf_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_osi_saf_dir,
                    'osi_saf.multi.{valid?fmt=%Y%m%d%H}_G004.nc'
                )
                if not os.path.exists(VERIF_CASE_STEP_osi_saf_dir):
                    os.makedirs(VERIF_CASE_STEP_osi_saf_dir)
                if os.path.exists(osi_saf_prod_file):
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time,
                        osi_saf_prod_file_format,
                        osi_saf_dest_file_format
                    )
                else:
                    osi_saf_hem_prod_file_format = os.path.join(
                        DCOMROOT_DEV, '{valid?fmt=%Y%m%d}',
                        'seaice', 'osisaf', 'ice_conc_{hem?fmt=str}'
                        +'_polstere-100_multi_{valid?fmt=%Y%m%d%H}00.nc'
                    )
                    osi_saf_hem_prod_file = gda_util.format_filler(
                        osi_saf_hem_prod_file_format,
                        VERIF_CASE_STEP_type_valid_time,
                        VERIF_CASE_STEP_type_valid_time, ['anl'], {}
                    )
                    osi_saf_dest_file = gda_util.format_filler(
                        osi_saf_dest_file_format,
                        VERIF_CASE_STEP_type_valid_time,
                        VERIF_CASE_STEP_type_valid_time, ['anl'], {}
                    )
                    gda_util.prep_prod_osi_saf_file(
                        osi_saf_hem_prod_file,
                        osi_saf_dest_file
                    )
                    if not os.path.exists(osi_saf_dest_file) \
                            and evs_run_mode != 'production':
                        osi_saf_arch_file_format = os.path.join(
                            archive_obs_data_dir, 'osi_saf',
                            'osi_saf.multi.{valid?fmt=%Y%m%d%H}_G004.nc'
                        )
                        gda_util.get_truth_file(
                            VERIF_CASE_STEP_type_valid_time,
                            osi_saf_arch_file_format, osi_saf_dest_file_format
                        )
                # SMOS
                VERIF_CASE_STEP_smos_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'smos'
                )
                if not os.path.exists(VERIF_CASE_STEP_smos_dir):
                    os.makedirs(VERIF_CASE_STEP_smos_dir)
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
            elif VERIF_CASE_STEP_type == 'snow':
                # NOHRSC
                nohrsc_prod_file_format = os.path.join(
                    DCOMROOT_PROD, '{valid?fmt=%Y%m%d}', 'wgrbbul',
                    'nohrsc_snowfall',
                    'sfav2_CONUS_24h_{valid?fmt=%Y%m%d%H}_grid184.grb2'
                )
                nohrsc_prod_file = gda_util.format_filler(
                    nohrsc_prod_file_format, VERIF_CASE_STEP_type_valid_time,
                    VERIF_CASE_STEP_type_valid_time, ['anl'], {}
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
                if os.path.exists(nohrsc_prod_file):
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time,
                        nohrsc_prod_file_format, nohrsc_dest_file_format
                    )
                else:
                    if evs_run_mode != 'production':
                        nohrsc_arch_file_format = os.path.join(
                            archive_obs_data_dir, 'nohrsc_accum24hr',
                            'nohrsc.{valid?fmt=%Y%m%d%H}.24h'
                        )
                        gda_util.get_truth_file(
                            VERIF_CASE_STEP_type_valid_time,
                            nohrsc_arch_file_format, nohrsc_dest_file_format
                        )
            elif VERIF_CASE_STEP_type == 'sst':
                # GHRSST
                VERIF_CASE_STEP_ghrsst_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ghrsst'
                )
                if not os.path.exists(VERIF_CASE_STEP_ghrsst_dir):
                    os.makedirs(VERIF_CASE_STEP_ghrsst_dir)
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
                                    model_fcst_dest_file_format
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
                        COMROOT_PROD, 'obsproc', obsproc_ver,
                        'gdas.{valid?fmt=%Y%m%d}', '{valid?fmt=%H}', 'atmos',
                        'gdas.t{valid?fmt=%H}z.prepbufr'
                    )
                    gdas_prod_file = gda_util.format_filler(
                        gdas_prod_file_format, VERIF_CASE_STEP_type_valid_time,
                        VERIF_CASE_STEP_type_valid_time, ['anl'], {}
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
                    if os.path.exists(gdas_prod_file):
                        gda_util.get_truth_file(
                            VERIF_CASE_STEP_type_valid_time,
                            gdas_prod_file_format,
                            gdas_dest_file_format
                        )
                    else:
                        if evs_run_mode != 'production':
                            gdas_arch_file_format = os.path.join(
                                archive_obs_data_dir, 'prepbufr', 'gdas',
                                'prepbufr.gdas.{valid?fmt=%Y%m%d%H}'
                            )
                            gda_util.get_truth_file(
                                VERIF_CASE_STEP_type_valid_time,
                                gdas_arch_file_format,
                                gdas_dest_file_format
                            )
            if VERIF_CASE_STEP_type == 'sea_ice':
                # IABP
                VERIF_CASE_STEP_iabp_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'iabp'
                )
                if not os.path.exists(VERIF_CASE_STEP_iabp_dir):
                    os.makedirs(VERIF_CASE_STEP_iabp_dir)
            elif VERIF_CASE_STEP_type == 'sfc':
                # NAM prepbufr
                offset_hr = str(
                    int(VERIF_CASE_STEP_type_valid_time.strftime('%H'))%6
                ).zfill(2)
                offset_valid_time_dt = (
                    VERIF_CASE_STEP_type_valid_time
                    + datetime.timedelta(hours=int(offset_hr))
                )
                nam_prod_file_format = os.path.join(
                    COMROOT_PROD, 'obsproc', obsproc_ver,
                    'nam.{valid?fmt=%Y%m%d}',
                    'nam.t{valid?fmt=%H}z.prepbufr.tm'+offset_hr
                )
                nam_prod_file = gda_util.format_filler(
                    nam_prod_file_format, offset_valid_time_dt,
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
                if os.path.exists(nam_prod_file):
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time,
                        nam_prod_file, nam_dest_file
                    )
                else:
                    if evs_run_mode != 'production':
                        nam_arch_file_format = os.path.join(
                            archive_obs_data_dir, 'prepbufr',
                            'nam', 'nam.{valid?fmt=%Y%m%d}',
                            'nam.t{valid?fmt=%H}z.prepbufr.tm'+offset_hr
                        )
                        nam_arch_file = gda_util.format_filler(
                            nam_arch_file_format, offset_valid_time_dt,
                            offset_valid_time_dt, ['anl'], {}
                        )
                        gda_util.get_truth_file(
                            VERIF_CASE_STEP_type_valid_time,
                            nam_arch_file, nam_dest_file
                        )
                # Get previous day for 2 meter
                # Temperature Anomaly verification
                offset_valid_time_m1_dt = (
                    offset_valid_time_dt - datetime.timedelta(days=1)
                )
                VERIF_CASE_STEP_type_valid_time_m1 = (
                    VERIF_CASE_STEP_type_valid_time
                    - datetime.timedelta(days=1)
                )
                nam_prod_file = gda_util.format_filler(
                    nam_prod_file_format, offset_valid_time_m1_dt,
                    offset_valid_time_m1_dt, ['anl'], {}
                )
                nam_dest_file = gda_util.format_filler(
                    nam_dest_file_format, VERIF_CASE_STEP_type_valid_time_m1,
                    VERIF_CASE_STEP_type_valid_time_m1, ['anl'], {}
                )
                if os.path.exists(nam_prod_file):
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time,
                        nam_prod_file, nam_dest_file
                    )
                else:
                    if evs_run_mode != 'production':
                        nam_arch_file = gda_util.format_filler(
                            nam_arch_file_format, offset_valid_time_m1_dt,
                            offset_valid_time_m1_dt, ['anl'], {}
                        )
                        gda_util.get_truth_file(
                            VERIF_CASE_STEP_type_valid_time,
                            nam_arch_file, nam_dest_file
                        )
                # RAP_P prepbufr
                rap_p_prod_file_format = os.path.join(
                    COMROOT_PROD, 'obsproc', obsproc_ver,
                    'rap_p.{valid?fmt=%Y%m%d}',
                    'rap_p.t{valid?fmt=%H}z.prepbufr.tm00'
                )
                rap_p_prod_file = gda_util.format_filler(
                    rap_p_prod_file_format, VERIF_CASE_STEP_type_valid_time,
                    VERIF_CASE_STEP_type_valid_time, ['anl'], {}
                ) 
                VERIF_CASE_STEP_rap_p_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'prepbufr_rap_p'
                )
                rap_p_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_rap_p_dir,
                    'prepbufr.rap_p.{valid?fmt=%Y%m%d%H}'
                )
                if not os.path.exists(VERIF_CASE_STEP_rap_p_dir):
                    os.makedirs(VERIF_CASE_STEP_rap_p_dir)
                if os.path.exists(rap_p_prod_file):
                    gda_util.get_truth_file(
                        VERIF_CASE_STEP_type_valid_time,
                        rap_p_prod_file_format, rap_p_dest_file_format
                    )
                else:
                    if evs_run_mode != 'production':
                        rap_p_arch_file_format = os.path.join(
                            archive_obs_data_dir, 'prepbufr',
                            'rap_p', 'rap_p.{valid?fmt=%Y%m%d}',
                            'rap_p.t{valid?fmt=%H}z.prepbufr.tm00'
                        )
                        gda_util.get_truth_file(
                            VERIF_CASE_STEP_type_valid_time,
                            rap_p_arch_file_format, rap_p_dest_file_format
                        )
                # Get previous day for 2 meter
                # Temperature Anomaly verification
                rap_p_prod_file = gda_util.format_filler(
                    rap_p_prod_file_format,
                    VERIF_CASE_STEP_type_valid_time-datetime.timedelta(days=1),
                    VERIF_CASE_STEP_type_valid_time-datetime.timedelta(days=1),
                    ['anl'], {}
                )
                if os.path.exists(rap_p_prod_file):
                    gda_util.get_truth_file(
                        (VERIF_CASE_STEP_type_valid_time
                         - datetime.timedelta(days=1)),
                        rap_p_prod_file_format, rap_p_dest_file_format
                    )
                else:
                    if evs_run_mode != 'production':
                        gda_util.get_truth_file(
                            (VERIF_CASE_STEP_type_valid_time
                             - datetime.timedelta(days=1)),
                            rap_p_arch_file_format, rap_p_dest_file_format
                        )

print("END: "+os.path.basename(__file__))
