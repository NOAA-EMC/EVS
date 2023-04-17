'''
Name: subseasonal_get_data_files.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/.
          This gets the necessary data files to run
          the use case.
'''

import os
import datetime
import subseasonal_util as sub_util

print("BEGIN: "+os.path.basename(__file__))

# Read in common environment variables
RUN = os.environ['RUN']
NET = os.environ['NET']
COMPONENT = os.environ['COMPONENT']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
VERIF_CASE_STEP = os.environ['VERIF_CASE_STEP']
DATA = os.environ['DATA']
COMIN = os.environ['COMIN']
model_list = os.environ['model_list'].split(' ')
model_stats_dir_list = os.environ['model_stats_dir_list'].split(' ')
model_file_format_list = os.environ['model_file_format_list'].split(' ')
members = os.environ['members']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
USER = os.environ['USER']
#evs_run_mode = os.environ['evs_run_mode']
if STEP == 'stats':
    COMINobs = os.environ['COMINobs']
    #COMINccpa = os.environ['COMINccpa']
    #COMINobsproc = os.environ['COMINobsproc']
    #COMINosi_saf = os.environ['COMINosi_saf']
    #COMINghrsst_ospo = os.environ['COMINghrsst_ospo']
#if evs_run_mode != 'production':
    #QUEUESERV = os.environ['QUEUESERV']
    #ACCOUNT = os.environ['ACCOUNT']
    #machine = os.environ['machine']

# Set archive paths
#if evs_run_mode != 'production':
    #archive_obs_data_dir = os.environ['archive_obs_data_dir']

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
        if VERIF_CASE_STEP_type == 'pres':
            VERIF_CASE_STEP_pres_truth_format_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_pres_truth_file_format_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type == 'anom':
            VERIF_CASE_STEP_anom_truth_format_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_anom_truth_file_format_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type == 'OLR':
            VERIF_CASE_STEP_OLR_truth_format_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_OLR_truth_file_format_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type == 'precip':
            VERIF_CASE_STEP_precip_truth_format_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_precip_truth_file_format_list'
            ].split(' ')
            VERIF_CASE_STEP_precip_file_format_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_precip_file_format_list'
            ].split(' ')
            VERIF_CASE_STEP_precip_file_accum_list = os.environ[
                VERIF_CASE_STEP_abbrev+'_precip_file_accum_list'
            ].split(' ')
        # Set valid hours
        if VERIF_CASE_STEP_type in ['pres', 'OLR']: 
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_vhr_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type == 'precip':
            (CCPA24hr_valid_hr_start, CCPA24hr_valid_hr_end,
             CCPA24hr_valid_hr_inc) = sub_util.get_obs_valid_hrs(
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
        elif VERIF_CASE_STEP_type == 'seaice':
            (OSI_SAF_valid_hr_start, OSI_SAF_valid_hr_end,
             OSI_SAF_valid_hr_inc) = sub_util.get_obs_valid_hrs(
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
        elif VERIF_CASE_STEP_type in ['sst', 'ENSO']:
            (GHRSST_OSPO_valid_hr_start, GHRSST_OSPO_valid_hr_end,
             GHRSST_OSPO_valid_hr_inc) = sub_util.get_obs_valid_hrs(
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
        elif VERIF_CASE_STEP_type == 'anom':
            (ECMWF_valid_hr_start, ECMWF_valid_hr_end,
             ECMWF_valid_hr_inc) = sub_util.get_obs_valid_hrs(
                 'ECMWF'
            )
            ECMWF_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    ECMWF_valid_hr_start,
                    ECMWF_valid_hr_end+ECMWF_valid_hr_inc,
                    ECMWF_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = ECMWF_valid_hr_list
        else:
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        # Set initialization hours
        VERIF_CASE_STEP_type_init_hr_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_fcyc_list'
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
        VERIF_CASE_STEP_type_time_info_dict = sub_util.get_time_info(
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
                model_file_form = model_file_format_list[model_idx]
                VERIF_CASE_STEP_model_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, model
                )
                if not os.path.exists(VERIF_CASE_STEP_model_dir):
                    os.makedirs(VERIF_CASE_STEP_model_dir)
                if VERIF_CASE_STEP_type == 'precip':
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
                elif VERIF_CASE_STEP_type == 'pres':
                    mbr = 1
                    total = int(members)
                    while mbr <= total:
                        mb = str(mbr).zfill(2)
                        if model == 'gefs':
                            model_file_format = os.path.join(
                                model_file_form+'.ens'+mb
                                +'.t{init?fmt=%2H}z.pgrb2.0p50.'
                                +'f{lead?fmt=%3H}'
                            )
                            model_fcst_dest_file_format = os.path.join(
                                VERIF_CASE_STEP_model_dir,
                                model+'.ens'+mb+'.{init?fmt=%Y%m%d%H}.'
                                +'f{lead?fmt=%3H}'
                            )
                        elif model == 'cfs':
                            model_file_format = os.path.join(
                                model_file_form+'.pgbf.ens'+mb
                                +'.t{init?fmt=%2H}z.f{lead?fmt=%3H}'
                            )
                            model_fcst_dest_file_format = os.path.join(
                                VERIF_CASE_STEP_model_dir,
                                model+'.pgbf.ens'+mb+'.{init?fmt=%Y%m%d%H}.'
                                +'f{lead?fmt=%3H}'
                            )
                        #if time['init_time'].strftime('%H') in ['00'] \
                                #and int(time['forecast_hour']) % 24 == 0:
                        if int(time['forecast_hour']) == 168:
                            nf = 0
                            while nf <= 12:
                                sub_util.get_model_file(
                                    time['valid_time'] \
                                    - datetime.timedelta(hours=12*nf),
                                    time['init_time'],
                                    str(int(time['forecast_hour'])-(12*nf)),
                                    model_file_format,
                                    model_fcst_dest_file_format
                                )
                                #sub_util.get_model_file(
                                    #time['valid_time'] \
                                    #- datetime.timedelta(hours=12),
                                    #time['init_time'],
                                    #str(fhr),
                                    #model_file_format,
                                    #model_fcst_dest_file_format
                                #)
                                nf+=1
                        del model_file_format
                        mbr = mbr+1
                elif VERIF_CASE_STEP_type == 'anom':
                    mbr = 1
                    total = int(members)
                    while mbr <= total:
                        mb = str(mbr).zfill(2)
                        if model == 'gefs':
                            model_file_format = os.path.join(
                                model_file_form+'.ens'+mb
                                +'.t{init?fmt=%2H}z.pgrb2.0p50.'
                                +'f{lead?fmt=%3H}'
                            )
                        elif model == 'cfs':
                            model_file_format = os.path.join(
                                model_file_form+'.ens'+mb
                                +'.t{init?fmt=%2H}z.f{lead?fmt=%3H}'
                            )
                        model_fcst_dest_file_format = os.path.join(
                            VERIF_CASE_STEP_model_dir,
                            model+'.ens'+mb+'.{init?fmt=%Y%m%d%H}.'
                            +'f{lead?fmt=%3H}'
                        )
                        for time_length in ['weekly', 'days6_10', 'weeks3_4']:
                            if time_length == 'weekly':
                                if (time['forecast_hour']) in ['168',
                                                               '336',
                                                               '504',
                                                               '672',
                                                               '840']:
                                    nf = 0
                                    while nf <= 14:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format,
                                            model_fcst_dest_file_format
                                        )
                                        nf+=1
                            if time_length == 'days6_10':
                                if int(time['forecast_hour']) == 240:
                                    nf = 0
                                    while nf <= 10:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format,
                                            model_fcst_dest_file_format
                                        )
                                        nf+=1
                            if time_length == 'weeks3_4':
                                if int(time['forecast_hour']) == 672:
                                    nf = 0
                                    while nf <= 28:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format,
                                            model_fcst_dest_file_format
                                        )
                                        nf+=1
                        del model_file_format
                        mbr = mbr+1
                elif VERIF_CASE_STEP_type in ['sst', 'seaice']:
                    mbr = 1
                    total = int(members)
                    while mbr <= total:
                        mb = str(mbr).zfill(2)
                        if model == 'gefs':
                            model_file_format = os.path.join(
                                model_file_form+'.ens'+mb
                                +'.t{init?fmt=%2H}z.pgrb2.0p50.'
                                +'f{lead?fmt=%3H}'
                            )
                        elif model == 'cfs':
                            model_file_format = os.path.join(
                                model_file_form+'.ens'+mb
                                +'.t{init?fmt=%2H}z.f{lead?fmt=%3H}'
                            )
                        for time_length in ['daily', 'weekly', 'monthly']:
                            if time_length == 'daily':
                                model_fcst_dest_file_format = os.path.join(
                                    VERIF_CASE_STEP_model_dir,
                                    model+'.ens'+mb+'.{init?fmt=%Y%m%d%H}.'
                                    +'f{lead?fmt=%3H}'
                                )
                                nf = 0
                                while nf <= 2:
                                    if int(time['forecast_hour'])-(12*nf) >= 0:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format,
                                            model_fcst_dest_file_format
                                        )
                                    nf+=1
                            if time_length == 'weekly':
                                model_fcst_dest_file_format = os.path.join(
                                    VERIF_CASE_STEP_model_dir,
                                    model+'.ens'+mb+'.{init?fmt=%Y%m%d%H}.'
                                    +'f{lead?fmt=%3H}'
                                )
                                if (time['forecast_hour']) in ['168',
                                                               '336', 
                                                               '504', 
                                                               '672', 
                                                               '840']:
                                    nf = 0
                                    while nf <= 14:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format, 
                                            model_fcst_dest_file_format
                                        )
                                        nf+=1
                            if time_length == 'monthly':
                                model_fcst_dest_file_format = os.path.join(
                                    VERIF_CASE_STEP_model_dir,
                                    model+'.ens'+mb+'.{init?fmt=%Y%m%d%H}.'
                                    +'f{lead?fmt=%3H}'
                                )
                                if int(time['forecast_hour']) == 720:
                                    nf = 0
                                    while nf <= 60:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format,
                                            model_fcst_dest_file_format
                                        )
                                        nf+=1
                        del model_file_format
                        mbr = mbr+1
        # Get truth/obs files
        for VERIF_CASE_STEP_type_valid_time \
                in VERIF_CASE_STEP_type_valid_time_list:
            if VERIF_CASE_STEP_type == 'precip':
                # CCPA
                ccpa_prod_file_format = os.path.join(
                    COMINccpa, 'ccpa.{valid?fmt=%Y%m%d}',
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
                    ccpa_dest_file = gda_util.format_filler(
                        ccpa_dest_file_format, accum_valid, accum_valid,
                        ['anl'], {}
                    )
                    gda_util.get_truth_file(
                        accum_valid, ccpa_prod_file_format,
                        ccpa_dest_file_format
                    )
                    if not os.path.exists(ccpa_dest_file) \
                            and evs_run_mode != 'production':
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
            elif VERIF_CASE_STEP_type == 'pres':
                # GFS Analysis
                pres_truth_file_format = os.path.join(
                    COMINobs+'.{valid?fmt=%Y%m%d}', 'gfs',
                    'gfs.{valid?fmt=%Y%m%d%H}.anl'
                )
                VERIF_CASE_STEP_gfs_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'gfs'
                )
                pres_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_gfs_dir,
                    'gfs.{valid?fmt=%Y%m%d%H}.anl'
                )
                if not os.path.exists(VERIF_CASE_STEP_gfs_dir):
                    os.makedirs(VERIF_CASE_STEP_gfs_dir)
                nf = 0
                while nf <= 14:
                    sub_util.get_model_file(
                        (VERIF_CASE_STEP_type_valid_time
                        -datetime.timedelta(hours=12*nf)),
                        (VERIF_CASE_STEP_type_valid_time
                        -datetime.timedelta(hours=12*nf)),
                        'anl', pres_truth_file_format,
                        pres_dest_file_format
                    )
                    nf+=1
            elif VERIF_CASE_STEP_type == 'anom':
                # ECMWF Analysis
                anom_truth_file_format = os.path.join(
                    COMINobs+'.{valid?fmt=%Y%m%d}', 'ecmwf',
                    'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                )
                VERIF_CASE_STEP_ecmwf_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ecmwf'
                )
                if not os.path.exists(VERIF_CASE_STEP_ecmwf_dir):
                    os.makedirs(VERIF_CASE_STEP_ecmwf_dir)
                anom_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_ecmwf_dir,
                    'ecmwf.{valid?fmt=%Y%m%d%H}.anl'
                )
                for time_length in ['weekly', 'days6_10', 'weeks3_4']:
                    if time_length == 'weekly':
                        nf = 0
                        while nf <= 14:
                            sub_util.get_truth_file(
                                (VERIF_CASE_STEP_type_valid_time
                                -datetime.timedelta(hours=12*nf)),
                                anom_truth_file_format,
                                anom_dest_file_format
                            )
                            nf+=1
                    if time_length == 'days6_10':
                        nf = 0
                        while nf <= 10:
                            sub_util.get_truth_file(
                                (VERIF_CASE_STEP_type_valid_time
                                -datetime.timedelta(hours=12*nf)),
                                anom_truth_file_format,
                                anom_dest_file_format
                            )
                            nf+=1
                    if time_length == 'weeks3_4':
                        nf = 0
                        while nf <= 28:
                            sub_util.get_truth_file(
                                (VERIF_CASE_STEP_type_valid_time
                                -datetime.timedelta(hours=12*nf)),
                                anom_truth_file_format,
                                anom_dest_file_format
                            )
                            nf+=1
            elif VERIF_CASE_STEP_type == 'seaice':
                # OSI_SAF
                VERIF_CASE_STEP_osi_saf_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'osi_saf'
                )
                if not os.path.exists(VERIF_CASE_STEP_osi_saf_dir):
                    os.makedirs(VERIF_CASE_STEP_osi_saf_dir)
                for time_length in ['weekly', 'monthly']:
                    osi_saf_daily_arch_file_format = os.path.join(
                        COMINobs+'.{valid?fmt=%Y%m%d}',
                        'osi_saf', 'osi_saf.multi.'
                        +'{valid_shift?fmt=%Y%m%d%H?shift='
                        +'-24}to'
                        +'{valid?fmt=%Y%m%d%H}_G003.nc'
                    )
                    osi_saf_daily_arch_file = sub_util.format_filler(
                        osi_saf_daily_arch_file_format,
                        VERIF_CASE_STEP_type_valid_time,
                        VERIF_CASE_STEP_type_valid_time,
                        'anl', {}
                    )
                    osi_saf_daily_prep_file_format = os.path.join(
                        COMINobs+'.{valid?fmt=%Y%m%d}',
                        'osi_saf',
                        osi_saf_daily_arch_file_format.rpartition('/')[2]
                    )
                    if time_length == 'weekly':
                        VDATEm7_dt = (VERIF_CASE_STEP_type_valid_time
                                     + datetime.timedelta(hours=-168))
                        osi_saf_weekly_dest_file_format = os.path.join(
                            VERIF_CASE_STEP_osi_saf_dir,
                            'osi_saf.multi.'
                            +'{valid_shift?fmt=%Y%m%d%H?shift='
                            +'-168}to'
                            +'{valid?fmt=%Y%m%d%H}_G003.nc'
                        )
                        osi_saf_weekly_dest_file = sub_util.format_filler(
                            osi_saf_weekly_dest_file_format,
                            VERIF_CASE_STEP_type_valid_time,
                            VERIF_CASE_STEP_type_valid_time,
                            'anl', {}
                        )
                        print("----> Trying to create "
                              +osi_saf_weekly_dest_file)
                        osi_saf_weekly_file_list = [osi_saf_daily_arch_file]
                        VDATEm_dt = (VERIF_CASE_STEP_type_valid_time
                                    - datetime.timedelta(hours=24))
                        while VDATEm_dt > VDATEm7_dt:
                            VDATEm_arch_file = sub_util.format_filler(
                                osi_saf_daily_prep_file_format,
                                VDATEm_dt, VDATEm_dt,
                                'anl', {}
                            )
                            osi_saf_weekly_file_list.append(VDATEm_arch_file)
                            VDATEm_dt = VDATEm_dt - datetime.timedelta(hours=24)
                        sub_util.weekly_osi_saf_file(
                            osi_saf_weekly_file_list,
                            osi_saf_weekly_dest_file,
                            (VDATEm7_dt,VERIF_CASE_STEP_type_valid_time)
                        )
                    elif time_length == 'monthly':
                        VDATEm30_dt = (VERIF_CASE_STEP_type_valid_time 
                                      + datetime.timedelta(hours=-720))
                        osi_saf_monthly_dest_file_format = os.path.join(
                            VERIF_CASE_STEP_osi_saf_dir,
                            'osi_saf.multi.'
                            +'{valid_shift?fmt=%Y%m%d%H?shift='
                            +'-720}to'
                            +'{valid?fmt=%Y%m%d%H}_G003.nc'
                        )
                        osi_saf_monthly_dest_file = sub_util.format_filler(
                            osi_saf_monthly_dest_file_format,
                            VERIF_CASE_STEP_type_valid_time,
                            VERIF_CASE_STEP_type_valid_time,
                            'anl', {}
                        )
                        print("----> Trying to create "
                              +osi_saf_monthly_dest_file)
                        osi_saf_monthly_file_list = [osi_saf_daily_arch_file]
                        VDATEm_dt = (VERIF_CASE_STEP_type_valid_time
                                    - datetime.timedelta(hours=24))
                        while VDATEm_dt > VDATEm30_dt:
                            VDATEm_arch_file = sub_util.format_filler(
                                osi_saf_daily_prep_file_format,
                                VDATEm_dt, VDATEm_dt,
                                'anl', {}
                            )
                            osi_saf_monthly_file_list.append(VDATEm_arch_file)
                            VDATEm_dt = VDATEm_dt - datetime.timedelta(hours=24)
                        sub_util.monthly_osi_saf_file(
                            osi_saf_monthly_file_list,
                            osi_saf_monthly_dest_file,
                            (VDATEm30_dt,VERIF_CASE_STEP_type_valid_time)
                        )
                    #if not os.path.exists(osi_saf_dest_file) \
                            #and evs_run_mode != 'production':
                        #gda_util.get_truth_file(
                            #VERIF_CASE_STEP_type_valid_time,
                            #osi_saf_arch_file_format, osi_saf_dest_file_format
                        #)
            elif VERIF_CASE_STEP_type in ['sst', 'ENSO']:
                # GHRSST OSPO
                VERIF_CASE_STEP_ghrsst_ospo_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ghrsst_ospo'
                )
                if not os.path.exists(VERIF_CASE_STEP_ghrsst_ospo_dir):
                    os.makedirs(VERIF_CASE_STEP_ghrsst_ospo_dir)
                for time_length in ['daily', 'weekly', 'monthly']:
                    ghrsst_daily_arch_file_format = os.path.join(
                        COMINobs+'.{valid?fmt=%Y%m%d}', 'ghrsst_ospo',
                        'ghrsst_ospo.{valid_shift?fmt=%Y%m%d%H?shift='
                        +'-24}to'
                        +'{valid?fmt=%Y%m%d%H}.nc'
                    )
                    ghrsst_daily_arch_file = sub_util.format_filler(
                        ghrsst_daily_arch_file_format,
                        VERIF_CASE_STEP_type_valid_time,
                        VERIF_CASE_STEP_type_valid_time,
                        'anl', {}
                    )
                    ghrsst_daily_dest_file_format = os.path.join(
                        VERIF_CASE_STEP_ghrsst_ospo_dir,
                        'ghrsst_ospo.{valid_shift?fmt=%Y%m%d%H?shift='
                        +'-24}to'
                        +'{valid?fmt=%Y%m%d%H}.nc'
                    )
                    ghrsst_daily_prep_file_format = os.path.join(
                        COMINobs+'.{valid?fmt=%Y%m%d}',
                        'ghrsst_ospo',
                        ghrsst_daily_arch_file_format.rpartition('/')[2]
                    )
                    if time_length == 'daily':
                        ghrsst_daily_dest_file = sub_util.format_filler(
                            ghrsst_daily_dest_file_format,
                            VERIF_CASE_STEP_type_valid_time,
                            VERIF_CASE_STEP_type_valid_time,
                            ['anl'], {}
                        )
                        sub_util.get_truth_file(
                            VERIF_CASE_STEP_type_valid_time,
                            ghrsst_daily_arch_file_format,
                            ghrsst_daily_dest_file_format
                        )
                    elif time_length == 'weekly':
                        VDATEm7_dt = (VERIF_CASE_STEP_type_valid_time
                                     + datetime.timedelta(hours=-168))
                        ghrsst_weekly_dest_file_format = os.path.join(
                            VERIF_CASE_STEP_ghrsst_ospo_dir,
                            'ghrsst_ospo.{valid_shift?fmt=%Y%m%d%H?shift='
                            +'-168}to'
                            +'{valid?fmt=%Y%m%d%H}.nc'
                        )
                        ghrsst_weekly_dest_file = sub_util.format_filler(
                            ghrsst_weekly_dest_file_format,
                            VERIF_CASE_STEP_type_valid_time,
                            VERIF_CASE_STEP_type_valid_time,
                            'anl', {}
                        )
                        print("----> Trying to create "
                              +ghrsst_weekly_dest_file)
                        ghrsst_weekly_file_list = [ghrsst_daily_arch_file]
                        VDATEm_dt = (VERIF_CASE_STEP_type_valid_time
                                    - datetime.timedelta(hours=24))
                        while VDATEm_dt > VDATEm7_dt:
                            VDATEm_arch_file = sub_util.format_filler(
                                ghrsst_daily_prep_file_format,
                                VDATEm_dt, VDATEm_dt,
                                'anl', {}
                            )
                            ghrsst_weekly_file_list.append(VDATEm_arch_file)
                            VDATEm_dt = VDATEm_dt - datetime.timedelta(hours=24)
                        sub_util.weekly_ghrsst_ospo_file(
                            ghrsst_weekly_file_list,
                            ghrsst_weekly_dest_file,
                            (VDATEm7_dt,VERIF_CASE_STEP_type_valid_time)
                        )
                    elif time_length == 'monthly':
                        VDATEm30_dt = (VERIF_CASE_STEP_type_valid_time
                                      + datetime.timedelta(hours=-720))
                        ghrsst_monthly_dest_file_format = os.path.join(
                            VERIF_CASE_STEP_ghrsst_ospo_dir,
                            'ghrsst_ospo.{valid_shift?fmt=%Y%m%d%H?shift='
                            +'-720}to'
                            +'{valid?fmt=%Y%m%d%H}.nc'
                        )
                        ghrsst_monthly_dest_file = sub_util.format_filler(
                            ghrsst_monthly_dest_file_format,
                            VERIF_CASE_STEP_type_valid_time,
                            VERIF_CASE_STEP_type_valid_time,
                            'anl', {}
                        )
                        print("----> Trying to create "
                              +ghrsst_monthly_dest_file)
                        ghrsst_monthly_file_list = [ghrsst_daily_arch_file]
                        VDATEm_dt = (VERIF_CASE_STEP_type_valid_time
                                    - datetime.timedelta(hours=24))
                        while VDATEm_dt > VDATEm30_dt:
                            VDATEm_arch_file = sub_util.format_filler(
                                ghrsst_daily_prep_file_format,
                                VDATEm_dt, VDATEm_dt,
                                'anl', {}
                            )
                            ghrsst_monthly_file_list.append(VDATEm_arch_file)
                            VDATEm_dt = VDATEm_dt - datetime.timedelta(hours=24)
                        sub_util.monthly_ghrsst_ospo_file(
                            ghrsst_monthly_file_list,
                            ghrsst_monthly_dest_file,
                            (VDATEm30_dt,VERIF_CASE_STEP_type_valid_time)
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
        if VERIF_CASE_STEP_type in ['pres_levs', 'sfc']:
            VERIF_CASE_STEP_type_valid_hr_list = os.environ[
                VERIF_CASE_STEP_abbrev_type+'_valid_hr_list'
            ].split(' ')
        elif VERIF_CASE_STEP_type == 'PrepBufr':
            (BUFR_valid_hr_start, BUFR_valid_hr_end,
             BUFR_valid_hr_inc) = sub_util.get_obs_valid_hrs(
                 'BUFR'
            )
            BUFR_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    BUFR_valid_hr_start,
                    BUFR_valid_hr_end+BUFR_valid_hr_inc,
                    BUFR_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = BUFR_valid_hr_list
        # Set initialization hours
        VERIF_CASE_STEP_type_init_hr_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_fcyc_list'
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
        VERIF_CASE_STEP_type_time_info_dict = sub_util.get_time_info(
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
                model_file_form = model_file_format_list[model_idx]
                VERIF_CASE_STEP_model_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, model
                )
                if not os.path.exists(VERIF_CASE_STEP_model_dir):
                    os.makedirs(VERIF_CASE_STEP_model_dir)
                if VERIF_CASE_STEP_type == 'PrepBufr':
                    mbr = 1
                    total = int(members)
                    while mbr <= total:
                        mb = str(mbr).zfill(2)
                        if model == 'gefs':
                            model_file_format = os.path.join(
                                model_file_form+'.ens'+mb
                                +'.t{init?fmt=%2H}z.pgrb2.0p50.'
                                +'f{lead?fmt=%3H}'
                            )
                        elif model == 'cfs':
                            model_file_format = os.path.join(
                                model_file_form+'.ens'+mb
                                +'.t{init?fmt=%2H}z.f{lead?fmt=%3H}'
                            )
                        model_fcst_dest_file_format = os.path.join(
                            VERIF_CASE_STEP_model_dir,
                            model+'.ens'+mb+'.{init?fmt=%Y%m%d%H}.'
                            +'f{lead?fmt=%3H}'
                        )
                        for time_length in ['weekly', 'days6_10', 'weeks3_4']:
                            if time_length == 'weekly':
                                if (time['forecast_hour']) in ['168',
                                                               '336',
                                                               '504',
                                                               '672',
                                                               '840']:
                                    nf = 0
                                    while nf <= 14:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format,
                                            model_fcst_dest_file_format
                                        )
                                        nf+=1
                            if time_length == 'days6_10':
                                if int(time['forecast_hour']) == 240:
                                    nf = 0
                                    while nf <= 10:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format,
                                            model_fcst_dest_file_format
                                        )
                                        nf+=1
                            if time_length == 'weeks3_4':
                                if int(time['forecast_hour']) == 672:
                                    nf = 0
                                    while nf <= 28:
                                        sub_util.get_model_file(
                                            (time['valid_time']
                                             -datetime.timedelta(hours=12*nf)),
                                            time['init_time'],
                                            str(int(time['forecast_hour'])-(12*nf)),
                                            model_file_format,
                                            model_fcst_dest_file_format
                                        )
                                        nf+=1
                        del model_file_format
                        mbr = mbr+1
        # Get truth/obs files
        for VERIF_CASE_STEP_type_valid_time \
                in VERIF_CASE_STEP_type_valid_time_list:
            if VERIF_CASE_STEP_type == 'PrepBufr':
                # NAM prepbufr
                nam_prod_file_format = os.path.join(
                    COMINobs+'.{valid?fmt=%Y%m%d}', 'prepbufr_nam',
                    'prepbufr.nam.{valid?fmt=%Y%m%d%H}'
                )
                VERIF_CASE_STEP_nam_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'prepbufr_nam'
                )
                if not os.path.exists(VERIF_CASE_STEP_nam_dir):
                    os.makedirs(VERIF_CASE_STEP_nam_dir)
                nam_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_nam_dir,
                    'prepbufr.nam.{valid?fmt=%Y%m%d%H}'
                )
                for time_length in ['weekly', 'days6_10', 'weeks3_4']:
                    if time_length == 'weekly':
                        nf = 0
                        while nf <= 14:
                            sub_util.get_truth_file(
                                (VERIF_CASE_STEP_type_valid_time
                                -datetime.timedelta(hours=12*nf)),
                                nam_prod_file_format,
                                nam_dest_file_format
                            )
                            nf+=1
                    if time_length == 'days6_10':
                        nf = 0
                        while nf <= 10:
                            sub_util.get_truth_file(
                                (VERIF_CASE_STEP_type_valid_time
                                -datetime.timedelta(hours=12*nf)),
                                nam_prod_file_format,
                                nam_dest_file_format
                            )
                            nf+=1
                    if time_length == 'weeks3_4':
                        nf = 0
                        while nf <= 28:
                            sub_util.get_truth_file(
                                (VERIF_CASE_STEP_type_valid_time
                                -datetime.timedelta(hours=12*nf)),
                                nam_prod_file_format,
                                nam_dest_file_format
                            )
                            nf+=1
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
                        model+'_'+RUN+'_'+VERIF_CASE+'_'
                        'v'+date_dt.strftime('%Y%m%d')+'.stat'
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
            COMINccpa, 'pcp_combine_precip.24hrCCPA.valid'
            +end_date_dt.strftime('%Y%m%d')+CCPA24hr_valid_hr_list[0]+'.nc'
        )
        dest_ccpa_pcp_combine_file = os.path.join(
            VERIF_CASE_STEP_data_dir, 'ccpa',
            'ccpa_precip.24hrAccum.valid'
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
                    COMINmodel, 'pcp_combine_precip.24hrAccum.init'
                    +init_dt.strftime('%Y%m%d%H')+'.f'+str(fhr).zfill(3)+'.nc'
                )
                dest_model_fhr_pcp_combine_file = os.path.join(
                    VERIF_CASE_STEP_data_dir, model,
                    model+'_precip.24hrAccum.init'
                    +init_dt.strftime('%Y%m%d%H')+'.f'+str(fhr).zfill(3)+'.nc'
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

print("END: "+os.path.basename(__file__))
