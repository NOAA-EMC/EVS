#!/usr/bin/env python3
'''
Name: global_det_atmos_plots.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This is the driver script for creating plots.
Run By: individual plotting job scripts generated through
        ush/global_det/global_det_atmos_plots_grid2obs_create_job_scripts.py
        and ush/global_det/global_det_atmos_plots_grid2grid_create_job_scripts.py
'''

import os
import sys
import logging
import datetime
import glob
import itertools
import shutil
import global_det_atmos_util as gda_util
from global_det_atmos_plots_specs import PlotSpecs

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
job_DATA_dir = os.environ['job_DATA_dir']
job_work_dir = os.environ['job_work_dir']
SENDCOM = os.environ['SENDCOM']
job_COMOUT_dir = os.environ['job_COMOUT_dir']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
FIXevs = os.environ['FIXevs']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
evs_run_mode = os.environ['evs_run_mode']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
date_type = os.environ['date_type']
NDAYS = os.environ['NDAYS']
plot_verbosity = os.environ['plot_verbosity']
VERIF_TYPE = os.environ['VERIF_TYPE']
job_id = os.environ['job_id']
if JOB_GROUP == 'condense_stats':
    line_type = os.environ['line_type']
    fcst_var_name = os.environ['fcst_var_name']
    obs_var_name = os.environ['obs_var_name']
    vx_mask = os.environ['vx_mask']
    model_list = os.environ['model_list'].split(', ')
    model_plot_name_list = os.environ['model_plot_name_list'].split(', ')
    obs_list = os.environ['obs_list'].split(', ')
    fcst_var_level = os.environ['fcst_var_level']
    obs_var_level = os.environ['obs_var_level']
elif JOB_GROUP == 'filter_stats':
    line_type = os.environ['line_type']
    fcst_var_name = os.environ['fcst_var_name']
    obs_var_name = os.environ['obs_var_name']
    vx_mask = os.environ['vx_mask']
    model_list = os.environ['model_list'].split(', ')
    model_plot_name_list = os.environ['model_plot_name_list'].split(', ')
    obs_list = os.environ['obs_list'].split(', ')
    valid_hr_start = os.environ['valid_hr_start']
    valid_hr_end = os.environ['valid_hr_end']
    valid_hr_inc = os.environ['valid_hr_inc']
    init_hr_start = os.environ['init_hr_start']
    init_hr_end = os.environ['init_hr_end']
    init_hr_inc = os.environ['init_hr_inc']
    fhr_list = os.environ['fhr_list']
    grid = os.environ['grid']
    event_equalization = os.environ['event_equalization']
    interp_method = os.environ['interp_method']
    interp_points = os.environ['interp_points']
    fcst_var_level = os.environ['fcst_var_level']
    fcst_var_thresh = os.environ['fcst_var_thresh']
    obs_var_level = os.environ['obs_var_level']
    obs_var_thresh = os.environ['obs_var_thresh']
elif JOB_GROUP == 'make_plots':
    line_type = os.environ['line_type']
    fcst_var_name = os.environ['fcst_var_name']
    obs_var_name = os.environ['obs_var_name']
    vx_mask = os.environ['vx_mask']
    model_list = os.environ['model_list'].split(', ')
    model_plot_name_list = os.environ['model_plot_name_list'].split(', ')
    obs_list = os.environ['obs_list'].split(', ')
    valid_hr_start = os.environ['valid_hr_start']
    valid_hr_end = os.environ['valid_hr_end']
    valid_hr_inc = os.environ['valid_hr_inc']
    init_hr_start = os.environ['init_hr_start']
    init_hr_end = os.environ['init_hr_end']
    init_hr_inc = os.environ['init_hr_inc']
    fhr_list = os.environ['fhr_list']
    grid = os.environ['grid']
    event_equalization = os.environ['event_equalization']
    interp_method = os.environ['interp_method']
    interp_points = os.environ['interp_points']
    fcst_var_level_list = os.environ['fcst_var_level_list'].split(', ')
    fcst_var_thresh_list = os.environ['fcst_var_thresh_list'].split(', ')
    obs_var_level_list = os.environ['obs_var_level_list'].split(', ')
    obs_var_thresh_list = os.environ['obs_var_thresh_list'].split(', ')
    stat = os.environ['stat']
    plot = os.environ['plot']
elif JOB_GROUP == 'tar_images':
    KEEPDATA = os.environ['KEEPDATA']

# Set variables
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
now = datetime.datetime.now()

# Set up directory paths
logo_dir = os.path.join(FIXevs, 'logos')
VERIF_CASE_STEP_dir = os.path.join(DATA, f"{VERIF_CASE}_{STEP}")
stat_base_dir = os.path.join(VERIF_CASE_STEP_dir, 'data')
logging_dir = os.path.join(job_work_dir, 'logs')
gda_util.make_dir(logging_dir)

# Set up logging
job_logging_file = os.path.join(logging_dir, 'evs_'+COMPONENT+'_'+RUN+'_'
                                +VERIF_CASE+'_'+STEP+'_'+VERIF_TYPE+'_'
                                +JOB_GROUP+'_'+job_id+'_runon'
                                +now.strftime('%Y%m%d%H%M%S')+'.log')
logger = logging.getLogger(job_logging_file)
logger.setLevel(plot_verbosity)
formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
    + '%(message)s',
    '%m/%d %H:%M:%S'
)
file_handler = logging.FileHandler(job_logging_file, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger_info = f"Log file: {job_logging_file}"
print(logger_info)
logger.info(logger_info)

# Set up model information dictionary
original_model_info_dict = {}
if JOB_GROUP != 'tar_images':
    for model_idx in range(len(model_list)):
        model_num = model_idx + 1
        original_model_info_dict['model'+str(model_num)] = {
            'name': model_list[model_idx],
            'plot_name': model_plot_name_list[model_idx],
            'obs_name': obs_list[model_idx]
        }

# Set up date information dictionary
original_date_info_dict = {
    'date_type': date_type,
    'start_date': start_date,
    'end_date': end_date,
    'ndays': NDAYS
}
if JOB_GROUP in ['filter_stats', 'make_plots']:
    original_date_info_dict['init_hr_start'] = init_hr_start
    original_date_info_dict['init_hr_end'] = init_hr_end
    original_date_info_dict['init_hr_inc'] = init_hr_inc
    valid_hrs = list(range(int(valid_hr_start),
                           int(valid_hr_end)+int(valid_hr_inc),
                           int(valid_hr_inc)))
    init_hrs = list(range(int(init_hr_start),
                          int(init_hr_end)+int(init_hr_inc),
                          int(init_hr_inc)))
    fhrs = [int(i) for i in fhr_list.split(', ')]

# Set up plot information dictionary
if JOB_GROUP != 'tar_images':
    original_plot_info_dict = {
        'line_type': line_type,
        'vx_mask': vx_mask,
    }
else:
    original_plot_info_dict = {}
if JOB_GROUP in ['filter_stats', 'make_plots']:
    original_plot_info_dict['grid'] = grid
    original_plot_info_dict['interp_method'] = interp_method
    original_plot_info_dict['interp_points'] = interp_points
    original_plot_info_dict['event_equalization'] = event_equalization
    if JOB_GROUP == 'filter_stats':
        original_plot_info_dict['fcst_var_name'] = fcst_var_name
        original_plot_info_dict['fcst_var_level'] = fcst_var_level
        original_plot_info_dict['fcst_var_thresh'] = fcst_var_thresh
        original_plot_info_dict['obs_var_name'] = obs_var_name
        original_plot_info_dict['obs_var_level'] = obs_var_level
        original_plot_info_dict['obs_var_thresh'] = obs_var_thresh
    elif JOB_GROUP == 'make_plots':
        original_plot_info_dict['stat'] = stat
        fcst_var_prod = list(
            itertools.product([fcst_var_name], fcst_var_level_list,
                              fcst_var_thresh_list)
        )
        obs_var_prod = list(
            itertools.product([obs_var_name], obs_var_level_list,
                              obs_var_thresh_list)
        )
        if len(fcst_var_prod) == len(obs_var_prod):
            var_info = []
            for v in range(len(fcst_var_prod)):
                var_info.append((fcst_var_prod[v], obs_var_prod[v]))
        else:
            logger.error("Forecast and observation variable information not "
                         +"the same length")
            sys.exit(1)


# Set up MET information dictionary
original_met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}

# Condense .stat files
if JOB_GROUP == 'condense_stats':
    for model_idx in range(len(model_list)):
        model = model_list[model_idx]
        obs_name = obs_list[model_idx]
        job_work_condensed_model_stat_file = os.path.join(
            job_work_dir, f"condensed_stats_{model.lower()}_{line_type.lower()}_"
            +f"{fcst_var_name.lower()}_"
            +f"{fcst_var_level.lower().replace('.','p').replace('-', '_')}_"
            +f"{vx_mask.lower()}.stat"
        )
        job_COMOUT_condensed_model_stat_file = (
            job_work_condensed_model_stat_file.replace(job_work_dir,
                                                       job_COMOUT_dir)
        )
        job_DATA_condensed_model_stat_file = (
            job_work_condensed_model_stat_file.replace(job_work_dir,
                                                       job_DATA_dir)
        )
        if SENDCOM == 'YES':
            check_job_condensed_model_stat_file = (
                job_COMOUT_condensed_model_stat_file
            )
        else:
            check_job_condensed_model_stat_file = (
                job_DATA_condensed_model_stat_file
            )
        if not os.path.exists(check_job_condensed_model_stat_file):
            gda_util.condense_model_stat_files(
                logger, stat_base_dir, job_work_dir, model, obs_name, vx_mask,
                fcst_var_name, fcst_var_level, obs_var_name, obs_var_level,
                line_type
            )
            if SENDCOM == 'YES' \
                    and os.path.exists(job_work_condensed_model_stat_file):
                logger.info(f"Copying {job_work_condensed_model_stat_file} to "
                            +f"{job_COMOUT_condensed_model_stat_file}")
                gda_util.copy_file(job_work_condensed_model_stat_file,
                                   job_COMOUT_condensed_model_stat_file)
elif JOB_GROUP == 'filter_stats':
    model_info_dict = original_model_info_dict.copy()
    date_info_dict = original_date_info_dict.copy()
    plot_info_dict = original_plot_info_dict.copy()
    met_info_dict = original_met_info_dict.copy()
    for filter_info in list(itertools.product(valid_hrs, fhrs)):
        date_info_dict['valid_hr_start'] = str(filter_info[0])
        date_info_dict['valid_hr_end'] = str(filter_info[0])
        date_info_dict['valid_hr_inc'] = '24'
        date_info_dict['forecast_hour'] = str(filter_info[1])
        init_hr = gda_util.get_init_hour(
            int(date_info_dict['valid_hr_start']),
            int(date_info_dict['forecast_hour'])
        )
        if init_hr in init_hrs:
            valid_dates, init_dates = gda_util.get_plot_dates(
                logger, date_info_dict['date_type'],
                date_info_dict['start_date'],
                date_info_dict['end_date'],
                date_info_dict['valid_hr_start'],
                date_info_dict['valid_hr_end'],
                date_info_dict['valid_hr_inc'],
                date_info_dict['init_hr_start'],
                date_info_dict['init_hr_end'],
                date_info_dict['init_hr_inc'],
                date_info_dict['forecast_hour']
            )
            format_valid_dates = [valid_dates[d].strftime('%Y%m%d_%H%M%S') \
                                  for d in range(len(valid_dates))]
            if len(valid_dates) == 0:
                plot_dates = np.arange(
                    datetime.datetime.strptime(
                        date_info_dict['start_date']
                        +date_info_dict['valid_hr_start'],
                        '%Y%m%d%H'
                    ),
                    datetime.datetime.strptime(
                        date_info_dict['end_date']
                        +date_info_dict['valid_hr_end'],
                        '%Y%m%d%H'
                    )
                    +datetime.timedelta(
                        hours=int(date_info_dict['valid_hr_inc'])
                    ),
                    datetime.timedelta(
                        hours=int(date_info_dict['valid_hr_inc'])
                    )
                ).astype(datetime.datetime)
            else:
                plot_dates = valid_dates
            for model_num in list(model_info_dict.keys()):
                model_dict = model_info_dict[model_num]
                job_work_filter_stats_model_file = os.path.join(
                    job_work_dir,
                    ('fcst'+model_dict['name']+'_'
                     +plot_info_dict['fcst_var_name']
                     +plot_info_dict['fcst_var_level']
                     +plot_info_dict['fcst_var_thresh']+'_'
                     +'obs'+model_dict['obs_name']+'_'
                     +plot_info_dict['obs_var_name']
                     +plot_info_dict['obs_var_level']
                     +plot_info_dict['obs_var_thresh']+'_'
                     +'linetype'+plot_info_dict['line_type']+'_'
                     +'grid'+plot_info_dict['grid']+'_'
                     +'vxmask'+plot_info_dict['vx_mask']+'_'
                     +'interp'+plot_info_dict['interp_method']
                     +plot_info_dict['interp_points']+'_'
                     +date_info_dict['date_type'].lower()
                     +valid_dates[0].strftime('%Y%m%d%H%M%S')+'to'
                     +valid_dates[-1].strftime('%Y%m%d%H%M%S')+'_'
                     +'fhr'+str(date_info_dict['forecast_hour']).zfill(3))\
                    .lower().replace('.','p').replace('-', '_')\
                    .replace('&&', 'and').replace('||', 'or')\
                    .replace('0,*,*', '').replace('*,*', '')\
                    +'.stat'
                )
                job_COMOUT_filter_stats_model_file = (
                    job_work_filter_stats_model_file.replace(job_work_dir,
                                                             job_COMOUT_dir)
                )
                job_DATA_filter_stats_model_file = (
                    job_work_filter_stats_model_file.replace(job_work_dir,
                                                             job_DATA_dir)
                )
                if SENDCOM == 'YES':
                    check_job_filter_stats_model_file = (
                        job_COMOUT_filter_stats_model_file
                    )
                    job_input_dir = job_COMOUT_dir
                else:
                    check_job_filter_stats_model_file = (
                        job_DATA_filter_stats_model_file
                    )
                    job_input_dir = job_DATA_dir
                if not os.path.exists(check_job_filter_stats_model_file):
                    all_model_df = gda_util.build_df(
                        JOB_GROUP, logger, job_input_dir, job_work_dir,
                        model_info_dict, met_info_dict,
                        plot_info_dict['fcst_var_name'],
                        plot_info_dict['fcst_var_level'],
                        plot_info_dict['fcst_var_thresh'],
                        plot_info_dict['obs_var_name'],
                        plot_info_dict['obs_var_level'],
                        plot_info_dict['obs_var_thresh'],
                        plot_info_dict['line_type'],
                        plot_info_dict['grid'],
                        plot_info_dict['vx_mask'],
                        plot_info_dict['interp_method'],
                        plot_info_dict['interp_points'],
                        date_info_dict['date_type'],
                        valid_dates, format_valid_dates,
                        str(date_info_dict['forecast_hour'])
                    )
                    if SENDCOM == 'YES' \
                            and \
                            os.path.exists(job_work_filter_stats_model_file):
                        logger.info("Copying "
                                    +f"{job_work_filter_stats_model_file} to "
                                    +f"{job_COMOUT_filter_stats_model_file}")
                        gda_util.copy_file(job_work_filter_stats_model_file,
                                           job_COMOUT_filter_stats_model_file)
elif JOB_GROUP == 'make_plots':
    if len(model_list) > 10:
        logger.error("Too many models requested ("+str(len(model_list))
                     +", ["+', '.join(model_list)+"]), maximum is 10")
        sys.exit(1)
    plot_specs = PlotSpecs(logger, plot)
    model_info_dict = original_model_info_dict.copy()
    date_info_dict = original_date_info_dict.copy()
    plot_info_dict = original_plot_info_dict.copy()
    met_info_dict = original_met_info_dict.copy()
    if plot == 'time_series':
        import global_det_atmos_plots_time_series as gdap_ts
        for ts_info in \
                list(itertools.product(valid_hrs, fhrs, var_info)):
            date_info_dict['valid_hr_start'] = str(ts_info[0])
            date_info_dict['valid_hr_end'] = str(ts_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(ts_info[1])
            plot_info_dict['fcst_var_name'] = ts_info[2][0][0]
            plot_info_dict['fcst_var_level'] = ts_info[2][0][1]
            plot_info_dict['fcst_var_thresh'] = ts_info[2][0][2]
            plot_info_dict['obs_var_name'] = ts_info[2][1][0]
            plot_info_dict['obs_var_level'] = ts_info[2][1][1]
            plot_info_dict['obs_var_thresh'] = ts_info[2][1][2]
            init_hr = gda_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            job_work_image_name = plot_specs.get_savefig_name(
                job_work_dir, plot_info_dict, date_info_dict
            )
            job_COMOUT_image_name = job_work_image_name.replace(
                job_work_dir, job_COMOUT_dir
            )
            job_DATA_image_name = job_work_image_name.replace(
                job_work_dir, job_DATA_dir
            )
            if SENDCOM == 'YES':
                check_job_image_name = job_COMOUT_image_name
                job_input_dir = job_COMOUT_dir
            else:
                check_job_image_name = job_DATA_image_name
                job_input_dir = job_DATA_dir
            if init_hr in init_hrs \
                    and not os.path.exists(check_job_image_name):
                make_ts = True
            else:
                make_ts = False
            if plot_info_dict['stat'] == 'FBAR_OBAR' \
                    and str(date_info_dict['forecast_hour']) not in \
                    ['24', '72', '120']:
                make_ts = False
            if os.path.exists(check_job_image_name):
                make_ts = False
            else:
                make_ts = True
            if make_ts:
                plot_ts = gdap_ts.TimeSeries(logger, job_input_dir+'/..',
                                             job_work_dir, model_info_dict,
                                             date_info_dict, plot_info_dict,
                                             met_info_dict, logo_dir)
                plot_ts.make_time_series()
                if SENDCOM == 'YES' and os.path.exists(job_work_image_name):
                    logger.info(f"Copying {job_work_image_name} to "
                                +f"{job_COMOUT_image_name}")
                    gda_util.copy_file(job_work_image_name,
                                       job_COMOUT_image_name)
    elif plot == 'lead_average':
        import global_det_atmos_plots_lead_average as gdap_la
        for la_info in list(itertools.product(valid_hrs, var_info)):
            date_info_dict['valid_hr_start'] = str(la_info[0])
            date_info_dict['valid_hr_end'] = str(la_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = la_info[1][0][0]
            plot_info_dict['fcst_var_level'] = la_info[1][0][1]
            plot_info_dict['fcst_var_thresh'] = la_info[1][0][2]
            plot_info_dict['obs_var_name'] = la_info[1][1][0]
            plot_info_dict['obs_var_level'] = la_info[1][1][1]
            plot_info_dict['obs_var_thresh'] = la_info[1][1][2]
            job_work_image_name = plot_specs.get_savefig_name(
                job_work_dir, plot_info_dict, date_info_dict
            )
            job_COMOUT_image_name = job_work_image_name.replace(
                job_work_dir, job_COMOUT_dir
            )
            job_DATA_image_name = job_work_image_name.replace(
                job_work_dir, job_DATA_dir
            )
            if SENDCOM == 'YES':
                check_job_image_name = job_COMOUT_image_name
                job_input_dir = job_COMOUT_dir
            else:
                check_job_image_name = job_DATA_image_name
                job_input_dir = job_DATA_dir
            if not os.path.exists(check_job_image_name) \
                    and plot_info_dict['stat'] != 'FBAR_OBAR':
                if len(date_info_dict['forecast_hours']) <= 1:
                    logger.warning("No span of forecast hours to plot, "
                                   +"given 1 forecast hour, skipping "
                                   +"lead_average plots")
                    make_la = False
                else:
                    make_la = True
            else:
                make_la = False
            if make_la:
                plot_la = gdap_la.LeadAverage(logger, job_input_dir+'/..',
                                              job_work_dir, model_info_dict,
                                              date_info_dict, plot_info_dict,
                                              met_info_dict, logo_dir)
                plot_la.make_lead_average()
                if SENDCOM == 'YES' and os.path.exists(job_work_image_name):
                    logger.info(f"Copying {job_work_image_name} to "
                                +f"{job_COMOUT_image_name}")
                    gda_util.copy_file(job_work_image_name,
                                       job_COMOUT_image_name)
    elif plot == 'valid_hour_average':
        import global_det_atmos_plots_valid_hour_average as gdap_vha
        for vha_info in list(itertools.product(var_info)):
            date_info_dict['valid_hr_start'] = valid_hr_start
            date_info_dict['valid_hr_end'] = valid_hr_end
            date_info_dict['valid_hr_inc'] = valid_hr_inc
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = vha_info[0][0][0]
            plot_info_dict['fcst_var_level'] = vha_info[0][0][1]
            plot_info_dict['fcst_var_thresh'] = vha_info[0][0][2]
            plot_info_dict['obs_var_name'] = vha_info[0][1][0]
            plot_info_dict['obs_var_level'] = vha_info[0][1][1]
            plot_info_dict['obs_var_thresh'] = vha_info[0][1][2]
            DATAjob_image_name = plot_specs.get_savefig_name(
                DATAjob, plot_info_dict, date_info_dict
            )
            COMOUTjob_image_name = (
                DATAjob_image_name.replace(DATAjob, COMOUTjob)
            )
            if not os.path.exists(DATAjob_image_name) \
                    and plot_info_dict['stat'] != 'FBAR_OBAR':
                if date_info_dict['valid_hr_start'] \
                        == date_info_dict['valid_hr_end']:
                    logger.warning("No span of valid hours to plot, "
                                   +"valid start hour is the same as "
                                   +"valid end hour, skipping "
                                   +"valid_hour_average plots")
                    make_vha = False
                else:
                    make_vha = True
            else:
                make_vha = False
            if os.path.exists(COMOUTjob_image_name):
                logger.info(f"Copying {COMOUTjob_image_name} to "
                            +f"{DATAjob_image_name}")
                gda_util.copy_file(COMOUTjob_image_name, DATAjob_image_name)
                make_vha = False
            if make_vha:
                plot_vha = gdap_vha.ValidHourAverage(logger, DATAjob+'/..',
                                                     DATAjob, model_info_dict,
                                                     date_info_dict,
                                                     plot_info_dict,
                                                     met_info_dict, logo_dir)
                plot_vha.make_valid_hour_average()
                if SENDCOM == 'YES' and os.path.exists(DATAjob_image_name):
                    logger.info(f"Copying {DATAjob_image_name} to "
                                +f"{COMOUTjob_image_name}")
                    gda_util.copy_file(DATAjob_image_name, COMOUTjob_image_name)
    elif plot == 'threshold_average':
        import global_det_atmos_plots_threshold_average as gdap_ta
        for ta_info in list(itertools.product(valid_hrs, fhrs)):
            date_info_dict['valid_hr_start'] = str(ta_info[0])
            date_info_dict['valid_hr_end'] = str(ta_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(ta_info[1])
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['fcst_var_threshs'] = fcst_var_thresh_list
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['obs_var_threshs'] = obs_var_thresh_list
            init_hr = gda_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            for l in range(len(fcst_var_level_list)):
                plot_info_dict['fcst_var_level'] = fcst_var_level_list[l]
                plot_info_dict['obs_var_level'] = obs_var_level_list[l]
                DATAjob_image_name = plot_specs.get_savefig_name(
                    DATAjob, plot_info_dict, date_info_dict
                )
                COMOUTjob_image_name = (
                    DATAjob_image_name.replace(DATAjob, COMOUTjob)
                )
                if init_hr in init_hrs \
                        and not os.path.exists(DATAjob_image_name) \
                        and plot_info_dict['stat'] != 'FBAR_OBAR':
                    if len(plot_info_dict['fcst_var_threshs']) <= 1:
                        logger.warning("No span of thresholds to plot, "
                                       +"given 1 threshold, skipping "
                                       +"threshold_average plots")
                        make_ta = False
                    else:
                        make_ta = True
                else:
                     make_ta = False
                if os.path.exists(COMOUTjob_image_name):
                    logger.info(f"Copying {COMOUTjob_image_name} to "
                                +f"{DATAjob_image_name}")
                    gda_util.copy_file(COMOUTjob_image_name, DATAjob_image_name)
                    make_ta = False
                if make_ta:
                    plot_ta = gdap_ta.ThresholdAverage(logger, DATAjob+'/..',
                                                       DATAjob,
                                                       model_info_dict,
                                                       date_info_dict,
                                                       plot_info_dict,
                                                       met_info_dict,
                                                       logo_dir)
                    plot_ta.make_threshold_average()
                    if SENDCOM == 'YES' \
                            and os.path.exists(DATAjob_image_name):
                        logger.info(f"Copying {DATAjob_image_name} to "
                                    +f"{COMOUTjob_image_name}")
                        gda_util.copy_file(DATAjob_image_name,
                                           COMOUTjob_image_name)
    elif plot == 'lead_by_date':
        import global_det_atmos_plots_lead_by_date as gdap_lbd
        for lbd_info in list(itertools.product(valid_hrs, var_info)):
            date_info_dict['valid_hr_start'] = str(lbd_info[0])
            date_info_dict['valid_hr_end'] = str(lbd_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = lbd_info[1][0][0]
            plot_info_dict['fcst_var_level'] = lbd_info[1][0][1]
            plot_info_dict['fcst_var_thresh'] = lbd_info[1][0][2]
            plot_info_dict['obs_var_name'] = lbd_info[1][1][0]
            plot_info_dict['obs_var_level'] = lbd_info[1][1][1]
            plot_info_dict['obs_var_thresh'] = lbd_info[1][1][2]
            DATAjob_image_name = plot_specs.get_savefig_name(
                DATAjob, plot_info_dict, date_info_dict
            )
            COMOUTjob_image_name = (
                DATAjob_image_name.replace(DATAjob, COMOUTjob)
            )
            if not os.path.exists(DATAjob_image_name) \
                    and plot_info_dict['stat'] != 'FBAR_OBAR':
                if len(date_info_dict['forecast_hours']) <= 1:
                    logger.warning("No span of forecast hours to plot, "
                                   +"given 1 forecast hour, skipping "
                                   +"lead_by_date plots")
                    make_lbd = False
                else:
                    make_lbd = True
            else:
                make_lbd = False
            if os.path.exists(COMOUTjob_image_name):
                logger.info(f"Copying {COMOUTjob_image_name} to "
                            +f"{DATAjob_image_name}")
                gda_util.copy_file(COMOUTjob_image_name, DATAjob_image_name)
                make_lbd = False
            if make_lbd:
                plot_lbd = gdap_lbd.LeadByDate(logger, DATAjob+'/..', DATAjob,
                                               model_info_dict, date_info_dict,
                                               plot_info_dict, met_info_dict,
                                               logo_dir)
                plot_lbd.make_lead_by_date()
                if SENDCOM == 'YES' and os.path.exists(DATAjob_image_name):
                    logger.info(f"Copying {DATAjob_image_name} to "
                                +f"{COMOUTjob_image_name}")
                    gda_util.copy_file(DATAjob_image_name, COMOUTjob_image_name)
    elif plot == 'stat_by_level':
        import global_det_atmos_plots_stat_by_level as gdap_sbl
        vert_profiles = [os.environ['vert_profile']]
        for sbl_info in \
                list(itertools.product(valid_hrs, fhrs, vert_profiles)):
            date_info_dict['valid_hr_start'] = str(sbl_info[0])
            date_info_dict['valid_hr_end'] = str(sbl_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(sbl_info[1])
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['vert_profile'] = sbl_info[2]
            plot_info_dict['fcst_var_level'] = sbl_info[2]
            plot_info_dict['obs_var_level'] = sbl_info[2]
            init_hr = gda_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            for t in range(len(fcst_var_thresh_list)):
                plot_info_dict['fcst_var_thresh'] = fcst_var_thresh_list[t]
                plot_info_dict['obs_var_thresh'] = obs_var_thresh_list[t]
                DATAjob_image_name = plot_specs.get_savefig_name(
                    DATAjob, plot_info_dict, date_info_dict
                )
                COMOUTjob_image_name = (
                    DATAjob_image_name.replace(DATAjob, COMOUTjob)
                )
                if init_hr in init_hrs \
                        and not os.path.exists(DATAjob_image_name) \
                        and plot_info_dict['stat'] != 'FBAR_OBAR':
                            make_sbl = True
                else:
                    make_sbl = False
                del plot_info_dict['fcst_var_level']
                del plot_info_dict['obs_var_level']
                if os.path.exists(COMOUTjob_image_name):
                    logger.info(f"Copying {COMOUTjob_image_name} to "
                                +f"{DATAjob_image_name}")
                    gda_util.copy_file(COMOUTjob_image_name, DATAjob_image_name)
                    make_sbl = False
                if make_sbl:
                    plot_sbl = gdap_sbl.StatByLevel(logger, DATAjob+'/..',
                                                    DATAjob, model_info_dict,
                                                    date_info_dict,
                                                    plot_info_dict,
                                                    met_info_dict, logo_dir)
                    plot_sbl.make_stat_by_level()
                    if SENDCOM == 'YES' \
                            and os.path.exists(DATAjob_image_name):
                        logger.info(f"Copying {DATAjob_image_name} to "
                                    +f"{COMOUTjob_image_name}")
                        gda_util.copy_file(DATAjob_image_name,
                                           COMOUTjob_image_name)
    elif plot == 'lead_by_level':
        import global_det_atmos_plots_lead_by_level as gdap_lbl
        if evs_run_mode == 'production':
            fhrs_lbl = []
            for fhr in fhrs:
                if fhr % 24 == 0:
                    fhrs_lbl.append(fhr)
        else:
            fhrs_lbl = fhrs
        vert_profiles = [os.environ['vert_profile']]
        for lbl_info in list(itertools.product(valid_hrs, vert_profiles)):
            date_info_dict['valid_hr_start'] = str(lbl_info[0])
            date_info_dict['valid_hr_end'] = str(lbl_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hours'] = fhrs_lbl
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['vert_profile'] = lbl_info[1]
            plot_info_dict['fcst_var_level'] = lbl_info[1]
            plot_info_dict['obs_var_level'] = lbl_info[1]
            for t in range(len(fcst_var_thresh_list)):
                plot_info_dict['fcst_var_thresh'] = fcst_var_thresh_list[t]
                plot_info_dict['obs_var_thresh'] = obs_var_thresh_list[t]
                DATAjob_image_name = plot_specs.get_savefig_name(
                    DATAjob, plot_info_dict, date_info_dict
                )
                COMOUTjob_image_name = (
                    DATAjob_image_name.replace(DATAjob, COMOUTjob)
                )
                if not os.path.exists(DATAjob_image_name) \
                        and plot_info_dict['stat'] != 'FBAR_OBAR':
                    if len(date_info_dict['forecast_hours']) <= 1:
                        logger.warning("No span of forecast hours to plot, "
                                       +"given 1 forecast hour, skipping "
                                       +"lead_by_level plots")
                        make_lbl = False
                    else:
                        make_lbl = True
                else:
                    make_lbl = False
                del plot_info_dict['fcst_var_level']
                del plot_info_dict['obs_var_level']
                if os.path.exists(COMOUTjob_image_name):
                    logger.info(f"Copying {COMOUTjob_image_name} to "
                                +f"{DATAjob_image_name}")
                    gda_util.copy_file(COMOUTjob_image_name, DATAjob_image_name)
                    make_lbl = False
                if make_lbl:
                    plot_lbl = gdap_lbl.LeadByLevel(logger, DATAjob+'/..',
                                                    DATAjob, model_info_dict,
                                                    date_info_dict,
                                                    plot_info_dict,
                                                    met_info_dict, logo_dir)
                    plot_lbl.make_lead_by_level()
                    if SENDCOM == 'YES' \
                            and os.path.exists(DATAjob_image_name):
                        logger.info(f"Copying {DATAjob_image_name} to "
                                    +f"{COMOUTjob_image_name}")
                        gda_util.copy_file(DATAjob_image_name,
                                           COMOUTjob_image_name)
    elif plot == 'nohrsc_spatial_map':
        import global_det_atmos_plots_nohrsc_spatial_map as gdap_nsm
        nohrsc_data_dir = os.path.join(VERIF_CASE_STEP_dir, 'data', 'nohrsc')
        date_info_dict['valid_hr_start'] = str(valid_hrs[0])
        date_info_dict['valid_hr_end'] = str(valid_hrs[0])
        date_info_dict['valid_hr_inc'] = '24'
        plot_info_dict['obs_var_name'] = obs_var_name
        plot_info_dict['obs_var_level'] = obs_var_level_list[0]
        if SENDCOM == 'YES':
            job_final_output_dir = job_COMOUT_dir
        else:
            job_final_output_dir = job_DATA_dir
        plot_nsm = gdap_nsm.NOHRSCSpatialMap(logger, nohrsc_data_dir,
                                             job_work_dir,
                                             job_final_output_dir,
                                             date_info_dict, plot_info_dict,
                                             logo_dir)
        plot_nsm.make_nohrsc_spatial_map()
    elif plot == 'precip_spatial_map':
        model_info_dict['obs'] = {'name': 'ccpa',
                                  'plot_name': 'ccpa',
                                  'obs_name': '24hrCCPA'}
        pcp_combine_base_dir = os.path.join(VERIF_CASE_STEP_dir, 'data')
        import global_det_atmos_plots_precip_spatial_map as gdap_psm
        for psm_info in \
                list(itertools.product(valid_hrs, fhrs)):
            date_info_dict['valid_hr_start'] = str(psm_info[0])
            date_info_dict['valid_hr_end'] = str(psm_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(psm_info[1])
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['fcst_var_level'] = fcst_var_level_list[0]
            plot_info_dict['fcst_var_thresh'] = 'NA'
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['obs_var_level'] = obs_var_level_list[0]
            plot_info_dict['obs_var_thresh'] = 'NA'
            plot_info_dict['interp_points'] = 'NA'
            if SENDCOM == 'YES':
                job_final_output_dir = job_COMOUT_dir
            else:
                job_final_output_dir = job_DATA_dir
            plot_psm = gdap_psm.PrecipSpatialMap(logger, pcp_combine_base_dir,
                                                 job_work_dir,
                                                 job_final_output_dir,
                                                 model_info_dict,
                                                 date_info_dict,
                                                 plot_info_dict,
                                                 met_info_dict, logo_dir)
            plot_psm.make_precip_spatial_map()
    elif plot == 'performance_diagram':
        import global_det_atmos_plots_performance_diagram as gdap_pd
        for pd_info in list(itertools.product(valid_hrs, fhrs)):
            date_info_dict['valid_hr_start'] = str(pd_info[0])
            date_info_dict['valid_hr_end'] = str(pd_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(pd_info[1])
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['fcst_var_threshs'] = fcst_var_thresh_list
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['obs_var_threshs'] = obs_var_thresh_list
            init_hr = gda_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            for l in range(len(fcst_var_level_list)):
                plot_info_dict['fcst_var_level'] = fcst_var_level_list[l]
                plot_info_dict['obs_var_level'] = obs_var_level_list[l]
                job_work_image_name = plot_specs.get_savefig_name(
                    job_work_dir, plot_info_dict, date_info_dict
                )
                job_COMOUT_image_name = job_work_image_name.replace(
                    job_work_dir, job_COMOUT_dir
                )
                job_DATA_image_name = job_work_image_name.replace(
                    job_work_dir, job_DATA_dir
                )
                if SENDCOM == 'YES':
                    check_job_image_name = job_COMOUT_image_name
                    job_input_dir = job_COMOUT_dir
                else:
                    check_job_image_name = job_DATA_image_name
                    job_input_dir = job_DATA_dir
                if init_hr in init_hrs \
                        and not os.path.exists(check_job_image_name) \
                        and plot_info_dict['stat'] == 'PERFDIAG':
                    make_pd = True
                else:
                    make_pd = False
                if make_pd:
                    plot_pd = gdap_pd.PerformanceDiagram(logger,
                                                         job_input_dir+'/..',
                                                         job_work_dir,
                                                         model_info_dict,
                                                         date_info_dict,
                                                         plot_info_dict,
                                                         met_info_dict,
                                                         logo_dir)
                    plot_pd.make_performance_diagram()
                    if SENDCOM == 'YES' \
                            and os.path.exists(job_work_image_name):
                        logger.info(f"Copying {job_work_image_name} to "
                                    +f"{job_COMOUT_image_name}")
                        gda_util.copy_file(job_work_image_name,
                                           job_COMOUT_image_name)
    else:
        logger.error(plot+" not recongized")
        sys.exit(1)
elif JOB_GROUP == 'tar_images':
    cwd = os.getcwd()
    job_work_tar_file = os.path.join(
        job_work_dir,
        (f"{VERIF_CASE}_{VERIF_TYPE}_"
         +job_DATA_dir\
          .replace(os.path.join(DATA, f"{VERIF_CASE}_{STEP}",
                                'plot_output', f"{RUN}.{end_date}",
                                f"{VERIF_CASE}_{VERIF_TYPE}",
                                f"last{NDAYS}days/"), '')\
          .replace('/', '_')+'.tar')
    )
    job_COMOUT_tar_file = job_work_tar_file.replace(
        job_work_dir, job_COMOUT_dir
    )
    job_DATA_tar_file = os.path.join(
        DATA, f"{VERIF_CASE}_{STEP}", 'plot_output', 'tar_files',
        job_work_tar_file.rpartition('/')[2]
    )
    if SENDCOM == 'YES':
        check_job_tar_file = job_COMOUT_tar_file
        job_input_dir = job_COMOUT_dir
    else:
        check_job_tar_file = job_DATA_tar_file
        job_input_dir = job_DATA_dir
    if not os.path.exists(check_job_tar_file):
        if len(glob.glob(job_input_dir+'/*')) != 0:
            logger.debug(f"Making tar file {job_work_tar_file} "
                         +f"from {job_input_dir}")
            os.chdir(job_input_dir)
            gda_util.run_shell_command(['tar', '-cvf', job_work_tar_file, '*'])
            os.chdir(cwd)
        else:
            logger.debug(f"No images generated in {job_input_dir}, "
                         +"cannot make tar file")
    if SENDCOM == 'YES' \
            and os.path.exists(job_work_tar_file):
        logger.info(f"Copying {job_work_tar_file} to "
                    +f"{job_COMOUT_tar_file}")
        gda_util.copy_file(job_work_tar_file, job_COMOUT_tar_file)
    else:
        if KEEPDATA != 'YES':
            if os.path.exists(job_DATA_dir):
                logger.info(f"Removing {job_DATA_dir}")
                shutil.rmtree(job_DATA_dir)

print("END: "+os.path.basename(__file__))
