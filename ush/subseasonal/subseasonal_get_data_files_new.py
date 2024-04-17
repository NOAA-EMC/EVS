#!/usr/bin/env python3
'''
Name: subseasonal_get_data_files.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/stats/subseasonal.
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
        # Set valid hours
        if VERIF_CASE_STEP_type == 'seaice':
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
        elif VERIF_CASE_STEP_type == 'sst':
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
        elif VERIF_CASE_STEP_type == 'pres_lvls':
            (GFS_valid_hr_start, GFS_valid_hr_end,
             GFS_valid_hr_inc) = sub_util.get_obs_valid_hrs(
                 'GFS'
            )
            GFS_valid_hr_list = [
                str(x).zfill(2) for x in range(
                    GFS_valid_hr_start,
                    GFS_valid_hr_end+GFS_valid_hr_inc,
                    GFS_valid_hr_inc
                )
            ]
            VERIF_CASE_STEP_type_valid_hr_list = GFS_valid_hr_list
        else:
            VERIF_CASE_STEP_type_valid_hr_list = ['12']
        # Set initialization hours
        VERIF_CASE_STEP_type_init_hr_list = os.environ[
            VERIF_CASE_STEP_abbrev_type+'_inithour_list'
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
                if VERIF_CASE_STEP_type in ['pres_lvls', 'anom']:
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
                            if VERIF_CASE_STEP_type == 'pres_lvls':
                                model_file_format = os.path.join(
                                    model_file_form+'.pgbf.ens'+mb
                                    +'.t{init?fmt=%2H}z.f{lead?fmt=%3H}'
                                )
                                model_fcst_dest_file_format = os.path.join(
                                    VERIF_CASE_STEP_model_dir,
                                    model+'.pgbf.ens'+mb+'.{init?fmt=%Y%m%d%H}.'
                                    +'f{lead?fmt=%3H}'
                                )
                            else:
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
            if VERIF_CASE_STEP_type == 'pres_lvls':
                # GFS Analysis
                pres_lvls_truth_file_format = os.path.join(
                    COMIN+'.{valid?fmt=%Y%m%d}', 'gfs',
                    'gfs.{valid?fmt=%Y%m%d%H}.anl'
                )
                VERIF_CASE_STEP_gfs_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'gfs'
                )
                if not os.path.exists(VERIF_CASE_STEP_gfs_dir):
                    os.makedirs(VERIF_CASE_STEP_gfs_dir)
                pres_lvls_dest_file_format = os.path.join(
                    VERIF_CASE_STEP_gfs_dir,
                    'gfs.{valid?fmt=%Y%m%d%H}.anl'
                )
                # Weeks 3-4 obs span covers weekly and Days 6-10 so only
                # need to loop once to retrieve data
                nf = 0
                while nf <= 28:
                    sub_util.get_truth_file(
                        (VERIF_CASE_STEP_type_valid_time
                        -datetime.timedelta(hours=12*nf)),
                        pres_lvls_truth_file_format,
                        pres_lvls_dest_file_format
                    )
                    nf+=1
            elif VERIF_CASE_STEP_type == 'anom':
                # ECMWF Analysis
                anom_truth_file_format = os.path.join(
                    COMIN+'.{valid?fmt=%Y%m%d}', 'ecmwf',
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
                # Weeks 3-4 obs span covers weekly and Days 6-10 so only
                # need to loop once to retrieve data
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
                        COMIN+'.{valid?fmt=%Y%m%d}',
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
                        COMIN+'.{valid?fmt=%Y%m%d}',
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
            elif VERIF_CASE_STEP_type == 'sst':
                # GHRSST OSPO
                VERIF_CASE_STEP_ghrsst_ospo_dir = os.path.join(
                    VERIF_CASE_STEP_data_dir, 'ghrsst_ospo'
                )
                if not os.path.exists(VERIF_CASE_STEP_ghrsst_ospo_dir):
                    os.makedirs(VERIF_CASE_STEP_ghrsst_ospo_dir)
                for time_length in ['daily', 'weekly', 'monthly']:
                    ghrsst_daily_arch_file_format = os.path.join(
                        COMIN+'.{valid?fmt=%Y%m%d}', 'ghrsst_ospo',
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
                        COMIN+'.{valid?fmt=%Y%m%d}',
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
        if VERIF_CASE_STEP_type == 'prepbufr':
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
            VERIF_CASE_STEP_abbrev_type+'_inithour_list'
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
                if VERIF_CASE_STEP_type == 'prepbufr':
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
            if VERIF_CASE_STEP_type == 'prepbufr':
                # NAM prepbufr
                nam_prod_file_format = os.path.join(
                    COMIN+'.{valid?fmt=%Y%m%d}', 'prepbufr_nam',
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
                # Weeks 3-4 obs span covers weekly and Days 6-10 so only
                # need to loop once to retrieve data
                nf = 0
                while nf <= 28:
                    sub_util.get_truth_file(
                        (VERIF_CASE_STEP_type_valid_time
                        -datetime.timedelta(hours=12*nf)),
                        nam_prod_file_format,
                        nam_dest_file_format
                    )
                    nf+=1

print("END: "+os.path.basename(__file__))
