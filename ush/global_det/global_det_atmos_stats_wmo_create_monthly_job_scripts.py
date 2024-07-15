#!/usr/bin/env python3
'''
Name: global_det_atmos_stats_wmo_create_monthly_job_scripts.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This creates multiple independent job scripts. These
          jobs scripts contain all the necessary environment variables
          and commands to needed to run them.
Run By: scripts/stats/global_det/exevs_global_det_atmos_wmo_stats.sh
'''

import sys
import os
import glob
import datetime
import netCDF4 as netcdf
import pandas as pd
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMIN = os.environ['COMIN']
COMINgfs = os.environ['COMINgfs']
COMINobsproc = os.environ['COMINobsproc']
SENDCOM = os.environ['SENDCOM']
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
VDATE = os.environ['VDATE']
VYYYYmm = os.environ['VYYYYmm']
MODELNAME = os.environ['MODELNAME']
JOB_GROUP = os.environ['JOB_GROUP']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
METPLUS_PATH = os.environ['METPLUS_PATH']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
FIXevs = os.environ['FIXevs']

VDATE_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')
VYYYYmm_dt = datetime.datetime.strptime(VYYYYmm, '%Y%m')

# Check only running for GFS
if MODELNAME != 'gfs':
    print(f"ERROR: {VERIF_CASE} stats are only run for gfs, exit")
    sys.exit(1)

# Set file formats
daily_stat_file_format = os.path.join(
    DATA, MODELNAME+'.{valid?fmt=%Y%m%d}',
    f"{NET}.{STEP}.{MODELNAME}.{RUN}.{VERIF_CASE}."
    +'v{valid?fmt=%Y%m%d}.stat'
)
stat_analysis_job_file_format = os.path.join(
    DATA, RUN+'.{valid?fmt=%Y%m%d}', MODELNAME, VERIF_CASE,
    MODELNAME+'.{wmo_verif?fmt=str}.{valid?fmt=%Y%m}_{valid?fmt=%H}Z.'
    +'f{lead?fmt=%H}.{stat_analysis_job?fmt=str}.{line_type?fmt=str}.stat'
)
wmo_rec2_report_file_format = os.path.join(
    DATA, MODELNAME+'.{valid?fmt=%Y%m%d}',
    '{valid?fmt=%Y%m}_kwbc_{temporal?fmt=str}.rec2'
)
wmo_svs_report_vhr_fhr_file_format = os.path.join(
    DATA, RUN+'.{valid?fmt=%Y%m%d}', MODELNAME, VERIF_CASE,
    '{valid?fmt=%Y%m}_kwbc_{param?fmt=str}_'
    +'valid{valid?fmt=%H}Z_fhr{lead?fmt=%3H}.svs'
)
wmo_svs_report_file_format = os.path.join(
    DATA, MODELNAME+'.{valid?fmt=%Y%m%d}',
    '{valid?fmt=%Y%m}_kwbc_{param?fmt=str}.svs'
)

# WMO Verifcations
wmo_verif_list = ['grid2grid_upperair', 'grid2obs_upperair', 'grid2obs_sfc']
wmo_init_hour_list = ['00', '12']
wmo_verif_settings_dict = {
    'grid2grid_upperair': {'valid_hour_list': ['00', '12'],
                           'fhr_list': [str(fhr) for fhr \
                                        in range(12,240+12,12)]},
    'grid2obs_upperair': {'valid_hour_list': ['00', '12'],
                          'fhr_list': [str(fhr) for fhr \
                                       in range(12,240+12,12)]},
    'grid2obs_sfc': {'valid_hour_list': ['00', '03', '06', '09',
                                         '12', '15', '18', '21'],
                     'fhr_list': [str(fhr) for fhr \
                                  in [*range(0,72,3), *range(72,240+6,6)]]},
}
# Set up job directory
njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, 'jobs', JOB_GROUP)
gda_util.make_dir(JOB_GROUP_jobs_dir)

# Create job scripts
if JOB_GROUP == 'summarize_stats':
    job_env_dict = gda_util.initalize_job_env_dict('all', JOB_GROUP,
                                                   VERIF_CASE, 'all')
    job_env_dict['year_month'] = VYYYYmm
    job_env_dict['valid_date'] = VDATE
    # Get daily stat files in VYYYYmm
    VYYYYmm_daily_stats_dir = os.path.join(DATA, f"{VYYYYmm}_daily_stats")
    VYYYYmm_station_info_dir = os.path.join(DATA, f"{VYYYYmm}_station_info")
    date_dt = VDATE_dt
    while date_dt >= VYYYYmm_dt:
        input_date_stat_file = gda_util.format_filler(
            daily_stat_file_format, date_dt, date_dt,
            'anl', {}
        ).replace(DATA, os.path.join(COMIN, 'stats', COMPONENT))
        tmp_date_stat_file = os.path.join(
            VYYYYmm_daily_stats_dir, input_date_stat_file.rpartition('/')[2]
        )
        if gda_util.check_file_exists_size(input_date_stat_file):
            print(f"Linking {input_date_stat_file} to {tmp_date_stat_file}")
            os.symlink(input_date_stat_file, tmp_date_stat_file)
        input_date_station_info_file = (
            input_date_stat_file.replace('.wmo.', '.wmo.station_info.')
        )
        tmp_date_station_info_file = os.path.join(
            VYYYYmm_station_info_dir,
            input_date_station_info_file.rpartition('/')[2]
        )
        if gda_util.check_file_exists_size(input_date_station_info_file):
            print(f"Linking {input_date_station_info_file} to "
                  +f"{tmp_date_station_info_file}")
            os.symlink(input_date_station_info_file,
                       tmp_date_station_info_file)
        date_dt = date_dt - datetime.timedelta(days=1)
    ndaily_stat_files = len(os.listdir(VYYYYmm_daily_stats_dir))
    job_env_dict['daily_stats_dir'] = VYYYYmm_daily_stats_dir
    # Filter surface station information
    print('Gathering station information from '
           +os.path.join(DATA, f"{VDATE_dt:%Y%m}_station_info", '*'))
    tmp_station_info_file_list = glob.glob(
        os.path.join(DATA, f"{VDATE_dt:%Y%m}_station_info", '*')
    )
    most_recent_station_info_file = os.path.join(
        DATA, f"{VDATE_dt:%Y%m}_station_info",
        f"evs.stats.gfs.atmos.wmo.station_info.v{VDATE_dt:%Y%m}.stat"
    )
    station_info = []
    column_name_list = gda_util.get_met_line_type_cols('hold', MET_ROOT,
                                                        met_ver, 'MPR')
    for station_info_file in tmp_station_info_file_list:
        station_info_file_df = pd.read_csv(
            station_info_file, sep=" ", skiprows=1, skipinitialspace=True,
            keep_default_na=False, dtype='str', header=None,
            names=column_name_list
        )
        station_info.append(station_info_file_df)
    station_info_df = pd.concat(station_info, axis=0, ignore_index=True)
    if len(station_info_df) == 0:
        have_station_info = False
        print("NOTE: Could not read in station information from file "
              +os.path.join(DATA, f"{VDATE_dt:%Y%m}_station_info", '*'))
    else:
        have_station_info = True
    del station_info_file_df
    most_recent_station_info_list = []
    for obs_sid_lead, obs_sid_lead_df \
            in station_info_df.groupby(by=['OBS_SID', 'FCST_LEAD']):
        sid_lead_valid_hr_list = []
        for fcst_valid_beg in obs_sid_lead_df['FCST_VALID_BEG'].unique():
            if fcst_valid_beg.split('_')[1] not in sid_lead_valid_hr_list:
                sid_lead_valid_hr_list.append(fcst_valid_beg.split('_')[1])
        for vhr in sid_lead_valid_hr_list:
            x = obs_sid_lead_df[
                obs_sid_lead_df['FCST_VALID_BEG'].str.contains(vhr)
            ]
            most_recent_station_info_list.append(
                x[x['FCST_VALID_BEG'] == x['FCST_VALID_BEG'].max()]
           )
    most_recent_station_info_df = pd.concat(
        most_recent_station_info_list, axis=0, ignore_index=True
    )
    most_recent_station_info_df.to_csv(
        most_recent_station_info_file, index=None, sep=' ', mode='w'
    )
    # Make job scripts
    VYYYYmm_monthly_stats_dir = os.path.join(DATA, f"{VYYYYmm}_monthly_stats")
    job_env_dict['monthly_stats_dir'] = VYYYYmm_monthly_stats_dir
    for wmo_verif in wmo_verif_list:
        job_env_dict['wmo_verif'] = wmo_verif
        if wmo_verif == 'grid2grid_upperair':
            job_env_dict['obtype'] = f"{MODELNAME}_anl"
            stat_analysis_job_dict = {
                'summary': ['VCNT:RMSVE,SPEED_ERR',
                            'CNT:ME,RMSE,ANOM_CORR,MAE,'
                            +'RMSFA,RMSOA,FSTDEV,OSTDEV',
                            'GRAD:S1']
            }
        elif wmo_verif == 'grid2obs_upperair':
            job_env_dict['obtype'] = 'ADPUPA'
            stat_analysis_job_dict = {
                'summary': ['VCNT:RMSVE,SPEED_ERR',
                            'CNT:ME,RMSE,MAE']
            }
        elif wmo_verif == 'grid2obs_sfc':
            job_env_dict['obtype'] = 'ADPSFC'
            stat_analysis_job_dict = {
                'summary': ['VCNT:RMSVE,SPEED_ERR,SPEED_ABSERR,'
                            +'DIR_ME,DIR_MAE,DIR_RMSE',
                            'CNT:ME,RMSE,MAE'],
                'aggregate': ['MCTC']
            }
        for vhr in wmo_verif_settings_dict[wmo_verif]['valid_hour_list']:
            job_env_dict['valid_hour'] = vhr
            valid_time_dt = datetime.datetime.strptime(VDATE+vhr,
                                                       '%Y%m%d%H')
            for fhr in wmo_verif_settings_dict[wmo_verif]['fhr_list']:
                job_env_dict['fhr'] = fhr
                init_time_dt = (valid_time_dt
                                - datetime.timedelta(hours=int(fhr)))
                if f"{init_time_dt:%H}" not in wmo_init_hour_list:
                     print(f"Skipping forecast hour {fhr} with init "
                           +f"{init_time_dt:%H} as init hour not in "
                           +"WMO required init hours "
                           +f"{wmo_init_hour_list}")
                     continue
                for stat_analysis_job in list(stat_analysis_job_dict.keys()):
                    wmo_verif_metplus_conf = (
                        f"StatAnalysis_fcstGFS_{stat_analysis_job}.conf"
                    )
                    for line_type_info \
                            in stat_analysis_job_dict[stat_analysis_job]:
                        if stat_analysis_job == 'summary':
                            line_type = line_type_info.split(':')[0]
                            line_type_stat_list = (
                                line_type_info.split(':')[1].split(',')
                            )
                            line_type_columns = ''
                            for stat in line_type_stat_list:
                                line_type_columns = (line_type_columns
                                                     +f"{line_type}:{stat}")
                                if stat != line_type_stat_list[-1]:
                                    line_type_columns = line_type_columns+','
                        elif stat_analysis_job == 'aggregate':
                            line_type = line_type_info
                        job_env_dict['line_type'] = line_type
                        tmp_stat_analysis_job_file = gda_util.format_filler(
                            stat_analysis_job_file_format, valid_time_dt,
                            valid_time_dt, fhr,
                            {'wmo_verif': wmo_verif,
                             'stat_analysis_job': stat_analysis_job,
                             'line_type': line_type}
                        )
                        job_env_dict['tmp_stat_analysis_job_file'] = (
                            tmp_stat_analysis_job_file
                        )
                        job_env_dict['tmp_stat_analysis_job_dump_row_file'] = (
                            tmp_stat_analysis_job_file.replace(
                                f".{line_type}.stat",
                                f".{line_type}.dump_row.stat"
                            )
                        )
                        job_env_dict['tmp_stat_analysis_job_grep_file'] = (
                            tmp_stat_analysis_job_file.replace(
                                f".{line_type}.stat",
                                f".{line_type}.grep.stat"
                            )
                        )
                        output_stat_analysis_job_file = os.path.join(
                            COMOUT , f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
                            tmp_stat_analysis_job_file.rpartition('/')[2]
                        )
                        job_env_dict['output_stat_analysis_job_file'] = (
                            output_stat_analysis_job_file
                        )
                        job_env_dict['output_stat_analysis_job_dump_row_file'] = (
                            output_stat_analysis_job_file.replace(
                                f".{line_type}.stat",
                                f".{line_type}.dump_row.stat"
                            )
                        )
                        job_env_dict['output_stat_analysis_job_grep_file'] = (
                            output_stat_analysis_job_file.replace(
                                f".{line_type}.stat",
                                f".{line_type}.grep.stat"
                            )
                        )
                        have_stat = os.path.exists(
                            output_stat_analysis_job_file
                        )
                        njobs+=1
                        job_file = os.path.join(JOB_GROUP_jobs_dir,
                                                'job'+str(njobs))
                        print(f"Creating job script: {job_file}")
                        job = open(job_file, 'w')
                        job.write('#!/bin/bash\n')
                        job.write('set -x\n')
                        job.write('\n')
                        for name, value in job_env_dict.items():
                            job.write(f'export {name}="{value}"\n')
                        if stat_analysis_job == 'summary':
                            job.write('export summary_columns="'
                                      +f'{line_type_columns}"\n')
                        job.write('\n')
                        if have_stat:
                            job.write(
                                'if [ -f '
                                +'$output_stat_analysis_job_grep_file ]; '
                                +'then cp -v '
                                +'$output_stat_analysis_job_grep_file '
                                +'$tmp_stat_analysis_job_grep_file; fi\n'
                            )
                            job.write('export err=$?; err_chk\n')
                            job.write(
                                'if [ -f $output_stat_analysis_job_file ]; '
                                +'then cp -v '
                                +'$output_stat_analysis_job_file '
                                +'$tmp_stat_analysis_job_file; fi\n'
                            )
                            job.write('export err=$?; err_chk\n')
                            job.write(
                                'if [ -f '
                                +'$output_stat_analysis_job_dump_row_file ]; '
                                +'then cp -v '
                                +'$output_stat_analysis_job_dump_row_file '
                                +'$tmp_stat_analysis_job_dump_row_file; fi\n'
                            )
                            job.write('export err=$?; err_chk')
                        else:
                            if ndaily_stat_files > 0:
                                job.write(
                                    'grep -h '
                                    +f'"{wmo_verif}.*{fhr.zfill(2)}0000 '
                                    +f'.*{VYYYYmm}.*_{vhr}0000 .* '
                                    +f'{line_type} " '
                                    +f"{VYYYYmm_daily_stats_dir}/"
                                    +f"evs.stats.gfs.atmos.wmo.v{VYYYYmm}"
                                    +'*.stat >& '
                                    +'$tmp_stat_analysis_job_grep_file\n'
                                )
                                job.write('export err=$?; err_chk\n')
                                job.write(
                                    'if [ -f '
                                    +'$tmp_stat_analysis_job_grep_file '
                                    +']; then '
                                    +gda_util.metplus_command(
                                         wmo_verif_metplus_conf
                                    )
                                    +'; fi\n'
                                )
                                job.write('export err=$?; err_chk\n')
                                if SENDCOM == 'YES':
                                    job.write(
                                        'if [ -f '
                                        +'$tmp_stat_analysis_job_grep_file'
                                        +' ]; then cp -v '
                                        +'$tmp_stat_analysis_job_'
                                        +'grep_file '
                                        +'$output_stat_analysis_job_'
                                        +'grep_file; fi\n'
                                    )
                                    job.write('export err=$?; err_chk\n')
                                    job.write(
                                        'if [ -f $tmp_stat_analysis_job_file ]'
                                        +'; then cp -v '
                                        +'$tmp_stat_analysis_job_file '
                                        +'$output_stat_analysis_job_file; fi\n'
                                    )
                                    job.write('export err=$?; err_chk\n')
                                    job.write(
                                        'if [ -f '
                                        +'$tmp_stat_analysis_job_dump_row_file'
                                        +' ]; then cp -v '
                                        +'$tmp_stat_analysis_job_'
                                        +'dump_row_file '
                                        +'$output_stat_analysis_job_'
                                        +'dump_row_file; fi\n'
                                    )
                                    job.write('export err=$?; err_chk')
                        job.close()
elif JOB_GROUP == 'write_reports':
    job_env_dict = gda_util.initalize_job_env_dict('all', JOB_GROUP,
                                                   VERIF_CASE, 'all')
    valid_time_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')
    job_env_dict['VDATE'] = VDATE
    # Write jobs for rec2
    for rec2_temporal in ['daily', 'monthly']:
        tmp_rec2_file = gda_util.format_filler(
            wmo_rec2_report_file_format, valid_time_dt, valid_time_dt,
            'anl', {'temporal': rec2_temporal}
        )
        output_rec2_file = os.path.join(
            COMOUT, f"{MODELNAME}.{VDATE}", tmp_rec2_file.rpartition('/')[2]
        )
        job_env_dict['tmp_report_file'] = tmp_rec2_file
        job_env_dict['output_report_file'] = output_rec2_file
        have_report = os.path.exists(output_rec2_file)
        # Make job script
        njobs+=1
        job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
        print(f"Creating job script: {job_file}")
        job = open(job_file, 'w')
        job.write('#!/bin/bash\n')
        job.write('set -x\n')
        job.write('\n')
        for name, value in job_env_dict.items():
            job.write(f'export {name}="{value}"\n')
        job.write('\n')
        if have_report:
            job.write('if [ -f $output_report_file ]; then '
                      +'cp -v $output_report_file $tmp_report_file; fi\n')
            job.write('export err=$?; err_chk')
        else:
            job.write(
                gda_util.python_command(
                    'global_det_atmos_stats_wmo_format_'
                    +f"rec2_domain_{rec2_temporal}.py",
                    []
                )+'\n'
            )
            job.write('export err=$?; err_chk\n')
            if SENDCOM == 'YES':
                job.write('if [ -f $tmp_report_file ]; then '
                          +'cp -v $tmp_report_file $output_report_file '
                          +'; fi\n')
                job.write('export err=$?; err_chk')
    # Write jobs for svs
    for param in ['t2m', 'ff10m', 'dd10m', 'tp24', 'td2m', 'rh2m',
                  'tcc', 'tp06']:
        if param == 'tp24':
            valid_hour_list = ['0', '12']
        else:
            valid_hour_list = ['0', '3', '6', '9', '12', '15', '18', '21']
        if param == 'tp24':
            fhr_list = [str(fhr) for fhr in range(24,240+24,24)]
        elif param == 'tp06':
            fhr_list = [str(fhr) for fhr in range(6,240+6,6)]
        else:
            fhr_list = [str(fhr) for fhr in \
                          [*range(0,72,3), *range(72,240+6,6)]]
        for vhr in valid_hour_list:
            for fhr in fhr_list:
                init_time_dt = (
                    (valid_time_dt + datetime.timedelta(hours=int(vhr)))
                    - datetime.timedelta(hours=int(fhr))
                )
                if f"{init_time_dt:%H}" not in wmo_init_hour_list:
                     print(f"Skipping forecast hour {fhr} with init "
                           +f"{init_time_dt:%H} as init hour not in "
                           +"WMO required init hours "
                           +f"{wmo_init_hour_list}")
                     continue
                tmp_report_file = gda_util.format_filler(
                    wmo_svs_report_vhr_fhr_file_format,
                    valid_time_dt+datetime.timedelta(hours=int(vhr)),
                    valid_time_dt+datetime.timedelta(hours=int(vhr)),
                    fhr, {'param': param}
                )
                output_report_file = os.path.join(
                    COMOUT, f"{RUN}.{VDATE}", MODELNAME, VERIF_CASE,
                    tmp_report_file.rpartition('/')[2]
                )
                job_env_dict['tmp_report_file'] = tmp_report_file
                job_env_dict['output_report_file'] = output_report_file
                have_report = os.path.exists(output_report_file)
                # Make job script
                njobs+=1
                job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
                print(f"Creating job script: {job_file}")
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                for name, value in job_env_dict.items():
                    job.write(f'export {name}="{value}"\n')
                job.write('\n')
                if have_report:
                    job.write('if [ -f $output_report_file ]; then '
                              +'cp -v $output_report_file $tmp_report_file; '
                              +'fi\n')
                    job.write('export err=$?; err_chk')
                else:
                    job.write(
                        gda_util.python_command(
                            'global_det_atmos_stats_wmo_format_'
                            +'svs_station_monthly.py',
                            [param, vhr, fhr]
                        )+'\n'
                    )
                    job.write('export err=$?; err_chk\n')
                    if SENDCOM == 'YES':
                        job.write('if [ -f $tmp_report_file ]; then '
                                  +'cp -v $tmp_report_file '
                                  +'$output_report_file; fi\n')
                        job.write('export err=$?; err_chk')
elif JOB_GROUP == 'concatenate_reports':
    job_env_dict = gda_util.initalize_job_env_dict('all', JOB_GROUP,
                                                   VERIF_CASE, 'all')
    valid_time_dt = datetime.datetime.strptime(VDATE, '%Y%m%d')
    job_env_dict['VDATE'] = VDATE
    # Write jobs for svs
    for param in ['t2m', 'ff10m', 'dd10m', 'tp24', 'td2m', 'rh2m',
                  'tcc', 'tp06']:
        tmp_report_file = gda_util.format_filler(
            wmo_svs_report_file_format, valid_time_dt,
            valid_time_dt, 'anl', {'param': param}
        )
        output_report_file = os.path.join(
            COMOUT, f"{MODELNAME}.{valid_time_dt:%Y%m%d}",
            tmp_report_file.rpartition('/')[2]
        )
        job_env_dict['tmp_report_file'] = tmp_report_file
        job_env_dict['output_report_file'] = output_report_file
        have_report = os.path.exists(output_report_file)
        # Make job script
        njobs+=1
        job_file = os.path.join(JOB_GROUP_jobs_dir, 'job'+str(njobs))
        print(f"Creating job script: {job_file}")
        job = open(job_file, 'w')
        job.write('#!/bin/bash\n')
        job.write('set -x\n')
        job.write('\n')
        for name, value in job_env_dict.items():
            job.write(f'export {name}="{value}"\n')
        job.write('\n')
        if have_report:
            job.write('if [ -f $output_report_file ]; then '
                      +'cp -v $output_report_file $tmp_report_file; '
                      +'fi\n')
            job.write('export err=$?; err_chk')
        else:
            svs_param_vhr_fhr_wildcard = os.path.join(
                DATA, f"{RUN}.{valid_time_dt:%Y%m%d}", MODELNAME, VERIF_CASE,
                f"{valid_time_dt:%Y%m}_kwbc_{param}_valid*Z_fhr*.svs"
            )
            svs_param_vhr_fhr_files = glob.glob(
                svs_param_vhr_fhr_wildcard
            )
            if len(svs_param_vhr_fhr_files) > 0:
                job.write(
                    f"cat {' '.join(svs_param_vhr_fhr_files)} >& "
                    +'$tmp_report_file\n'
                )
                if SENDCOM == 'YES':
                    job.write('if [ -f $tmp_report_file ]; then '
                              +'cp -v $tmp_report_file '
                              +'$output_report_file; fi\n')
                    job.write('export err=$?; err_chk')
            else:
                job.write('echo "No files matching '
                          +svs_param_vhr_fhr_wildcard+'"')

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(DATA, 'jobs', JOB_GROUP, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("NOTE: No job files created in "
              +os.path.join(DATA, 'jobs', JOB_GROUP))
    poe_files = glob.glob(os.path.join(DATA, 'jobs', JOB_GROUP, 'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = f"job{str(njob)}"
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            if iproc >= int(nproc):
                iproc = 0
                node+=1
        poe_filename = os.path.join(DATA, 'jobs', JOB_GROUP,
                                    f"poe_jobs{str(node)}")
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
               f"{str(iproc-1)} "
               +os.path.join(DATA, 'jobs', JOB_GROUP, job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(DATA, 'jobs', JOB_GROUP, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(DATA, 'jobs', JOB_GROUP,
                                f"poe_jobs{str(node)}")
    poe_file = open(poe_filename, 'a')
    iproc+=1
    while iproc <= int(nproc):
       if machine in ['HERA', 'ORION', 'S4', 'JET']:
           poe_file.write(
               f"{str(iproc-1)} /bin/echo {str(iproc)}\n"
           )
       else:
           poe_file.write(
               f"/bin/echo {str(iproc)}\n"
           )
       iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
