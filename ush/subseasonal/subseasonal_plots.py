#!/usr/bin/env python3
'''
Name: subseasonal_plots.py
Contact(s): Shannon Shields
Abstract: This script is run by subseasonal_plots_grid2grid_create_job_
          scripts.py and subseasonal_plots_grid2obs_create_job_scripts.py
          in ush/subseasonal.
          This script is the main driver for the plotting scripts.
'''

import os
import sys
import logging
import datetime
import glob
import subprocess
import itertools
import shutil
import subseasonal_util as sub_util
from subseasonal_plots_specs import PlotSpecs

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
FIXevs = os.environ['FIXevs']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
plot_verbosity = os.environ['plot_verbosity']
event_equalization = os.environ['event_equalization']
job_name = os.environ['job_name']
line_type = os.environ['line_type']
grid = os.environ['grid']
job_var = os.environ['job_var']
vx_mask = os.environ['vx_mask']
interp_method = os.environ['interp_method']
interp_points_list = os.environ['interp_points_list'].split(', ')
fcst_var_name = os.environ['fcst_var_name']
fcst_var_level_list = os.environ['fcst_var_level_list'].split(', ')
fcst_var_thresh_list = os.environ['fcst_var_thresh_list'].split(', ')
obs_var_name = os.environ['obs_var_name']
obs_var_level_list = os.environ['obs_var_level_list'].split(', ')
obs_var_thresh_list = os.environ['obs_var_thresh_list'].split(', ')
model_list = os.environ['model_list'].split(', ')
model_plot_name_list = os.environ['model_plot_name_list'].split(', ')
obs_list = os.environ['obs_list'].split(', ')
VERIF_TYPE = os.environ['VERIF_TYPE']
date_type = os.environ['date_type']
valid_hr_start = os.environ['valid_hr_start']
valid_hr_end = os.environ['valid_hr_end']
valid_hr_inc = os.environ['valid_hr_inc']
init_hr_start = os.environ['init_hr_start']
init_hr_end = os.environ['init_hr_end']
init_hr_inc = os.environ['init_hr_inc']
fhr_start = os.environ['fhr_start']
fhr_end = os.environ['fhr_end']
fhr_inc = os.environ['fhr_inc']
job_id = os.environ['job_id']
job_DATA_dir = os.environ['job_DATA_dir']
if JOB_GROUP == 'make_plots':
    job_DATA_images_dir = os.environ['job_DATA_images_dir']
    job_work_images_dir = os.environ['job_work_images_dir']
    stat = os.environ['stat']
    plot = os.environ['plot']
else:
    job_work_dir = os.environ['job_work_dir']

# Set variables
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
now = datetime.datetime.now()

# Set up directory paths
logo_dir = os.path.join(FIXevs, 'logos')
VERIF_CASE_STEP_dir = os.path.join(DATA, VERIF_CASE_STEP)
stat_base_dir = os.path.join(VERIF_CASE_STEP_dir, 'data')
if JOB_GROUP == 'tar_images':
    VERIF_TYPE_tar_dir = os.path.join(job_work_dir, RUN+'.'+end_date,
                                      'tar_files', VERIF_TYPE)
if JOB_GROUP == 'make_plots':
    logging_dir = os.path.join(job_work_images_dir, 'logs')
elif JOB_GROUP == 'tar_images':
    logging_dir = os.path.join(VERIF_TYPE_tar_dir, 'logs')
else:
    logging_dir = os.path.join(job_work_dir, 'logs')
if not os.path.exists(logging_dir):
    os.makedirs(logging_dir)

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
    'init_hr_start': init_hr_start,
    'init_hr_end': init_hr_end,
    'init_hr_inc': init_hr_inc,
}
valid_hrs = list(range(int(valid_hr_start),
                       int(valid_hr_end)+int(valid_hr_inc),
                       int(valid_hr_inc)))
init_hrs = list(range(int(init_hr_start),
                      int(init_hr_end)+int(init_hr_inc),
                      int(init_hr_inc)))
fhrs = list(range(int(fhr_start), int(fhr_end)+int(fhr_inc), int(fhr_inc)))

# Set up plot information dictionary
original_plot_info_dict = {
    'line_type': line_type,
    'grid': grid,
    'vx_mask': vx_mask,
    'interp_method': interp_method,
    'event_equalization': event_equalization
}
if JOB_GROUP == 'make_plots':
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
    logger.error("FATAL ERROR, FORECAST AND OBSERVATION VARIABLE INFORMATION "
                 +"NOT THE SAME LENGTH")
    sys.exit(1)

# Set up MET information dictionary
original_met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}

# Condense .stat files
if JOB_GROUP == 'condense_stats':
    logger.info("Condensing model .stat files")
    for model_idx in range(len(model_list)):
        model = model_list[model_idx]
        obs_name = obs_list[model_idx]
        condensed_model_stat_file = os.path.join(job_work_dir, 'model'
                                                 +str(model_idx+1)+'_'+model
                                                 +'.stat')
        sub_util.condense_model_stat_files(logger, stat_base_dir,
                                           condensed_model_stat_file, model,
                                           obs_name, grid, vx_mask,
                                           fcst_var_name, obs_var_name, 
                                           line_type)
elif JOB_GROUP == 'filter_stats':
    logger.info("Filtering model .stat files")
    model_info_dict = original_model_info_dict.copy()
    date_info_dict = original_date_info_dict.copy()
    plot_info_dict = original_plot_info_dict.copy()
    met_info_dict = original_met_info_dict.copy()
    for filter_info in list(
            itertools.product(valid_hrs, fhrs, var_info,
                              interp_points_list)
    ):
        date_info_dict['valid_hr_start'] = str(filter_info[0])
        date_info_dict['valid_hr_end'] = str(filter_info[0])
        date_info_dict['valid_hr_inc'] = '24'
        date_info_dict['forecast_hour'] = str(filter_info[1])
        plot_info_dict['fcst_var_name'] = filter_info[2][0][0]
        plot_info_dict['fcst_var_level'] = filter_info[2][0][1]
        plot_info_dict['fcst_var_thresh'] = filter_info[2][0][2]
        plot_info_dict['obs_var_name'] = filter_info[2][1][0]
        plot_info_dict['obs_var_level'] = filter_info[2][1][1]
        plot_info_dict['obs_var_thresh'] = filter_info[2][1][2]
        plot_info_dict['interp_points'] = str(filter_info[3])
        init_hr = sub_util.get_init_hour(
            int(date_info_dict['valid_hr_start']),
            int(date_info_dict['forecast_hour'])
        )
        if init_hr in init_hrs:
            valid_dates, init_dates = sub_util.get_plot_dates(
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
            all_model_df = sub_util.build_df(
                logger, job_DATA_dir, job_work_dir,
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
# Make the plots
elif JOB_GROUP == 'make_plots':
    logger.info("Making plots")
    if len(model_list) > 10:
        logger.error("FATAL ERROR, "
                     +"TOO MANY MODELS LISTED ("+str(len(model_list))
                     +", ["+', '.join(model_list)+"]), maximum is 10")
        sys.exit(1)
    plot_specs = PlotSpecs(logger, plot)
    model_info_dict = original_model_info_dict.copy()
    date_info_dict = original_date_info_dict.copy()
    plot_info_dict = original_plot_info_dict.copy()
    met_info_dict = original_met_info_dict.copy()
    if plot == 'time_series':
        import subseasonal_plots_time_series as subp_ts
        for ts_info in \
                list(itertools.product(valid_hrs, fhrs, var_info,
                                       interp_points_list)):
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
            plot_info_dict['interp_points'] = str(ts_info[3])
            init_hr = sub_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            image_name = plot_specs.get_savefig_name(
                job_work_images_dir,
                plot_info_dict, date_info_dict
            )
            if init_hr in init_hrs:
                if not os.path.exists(image_name):
                    make_ts = True
                else:
                    make_ts = False
            else:
                make_ts = False
            if make_ts:
                plot_ts = subp_ts.TimeSeries(logger, job_DATA_dir,
                                             job_work_images_dir, 
                                             model_info_dict,
                                             date_info_dict, plot_info_dict,
                                             met_info_dict, logo_dir)
                plot_ts.make_time_series()
    elif plot == 'lead_average':
        import subseasonal_plots_lead_average as subp_la
        for la_info in \
                list(itertools.product(valid_hrs, var_info,
                                       interp_points_list)):
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
            plot_info_dict['interp_points'] = str(la_info[2])
            image_name = plot_specs.get_savefig_name(
                job_work_images_dir,
                plot_info_dict, date_info_dict
            )
            if not os.path.exists(image_name):
                if len(date_info_dict['forecast_hours']) <= 1:
                    logger.warning("No span of forecast hours to plot, "
                                   +"given 1 forecast hour, skipping "
                                   +"lead_average plots")
                    make_la = False
                else:
                    if plot_info_dict['stat'] == 'FBAR_OBAR':
                        make_la = False
                    else:
                        make_la = True
            else:
                make_la = False
            if make_la:
                plot_la = subp_la.LeadAverage(logger, job_DATA_dir,
                                              job_work_images_dir, 
                                              model_info_dict,
                                              date_info_dict, plot_info_dict,
                                              met_info_dict, logo_dir)
                plot_la.make_lead_average()
    elif plot == 'valid_hour_average':
        import subseasonal_plots_valid_hour_average as subp_vha
        for vha_info in \
                list(itertools.product(var_info, interp_points_list)):
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
            plot_info_dict['interp_points'] = str(vha_info[1])
            image_name = plot_specs.get_savefig_name(
                job_work_images_dir,
                plot_info_dict, date_info_dict
            )
            if not os.path.exists(image_name):
                if date_info_dict['valid_hr_start'] \
                        == date_info_dict['valid_hr_end']:
                    logger.warning("No span of valid hours to plot, "
                                   +"valid start hour is the same as "
                                   +"valid end hour, skipping "
                                   +"valid_hour_average plots")
                    make_vha = False
                else:
                    if plot_info_dict['stat'] == 'FBAR_OBAR':
                        make_vha = False
                    else:
                        make_vha = True
            else:
                make_vha = False
            if make_vha:
                plot_vha = subp_vha.ValidHourAverage(logger, job_DATA_dir,
                                                     job_work_images_dir,
                                                     model_info_dict,
                                                     date_info_dict,
                                                     plot_info_dict,
                                                     met_info_dict, logo_dir)
                plot_vha.make_valid_hour_average()
    elif plot == 'threshold_average':
        import subseasonal_plots_threshold_average as subp_ta
        for ta_info in \
                list(itertools.product(valid_hrs, fhrs, interp_points_list)):
            date_info_dict['valid_hr_start'] = str(ta_info[0])
            date_info_dict['valid_hr_end'] = str(ta_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(ta_info[1])
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['fcst_var_threshs'] = fcst_var_thresh_list
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['obs_var_threshs'] = obs_var_thresh_list
            plot_info_dict['interp_points'] = str(ta_info[2])
            init_hr = sub_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            for l in range(len(fcst_var_level_list)):
                plot_info_dict['fcst_var_level'] = fcst_var_level_list[l]
                plot_info_dict['obs_var_level'] = obs_var_level_list[l]
                image_name = plot_specs.get_savefig_name(
                    job_work_images_dir,
                    plot_info_dict, date_info_dict
                )
                if init_hr in init_hrs:
                    if not os.path.exists(image_name):
                        if len(plot_info_dict['fcst_var_threshs']) <= 1:
                            logger.warning("No span of thresholds to plot, "
                                           +"given 1 threshold, skipping "
                                           +"threshold_average plots")
                            make_ta = False
                        else:
                            if plot_info_dict['stat'] == 'FBAR_OBAR':
                                make_ta = False
                            else:
                                make_ta = True
                    else:
                        make_ta = False
                else:
                     make_ta = False
                if make_ta:
                    plot_ta = subp_ta.ThresholdAverage(logger, job_DATA_dir,
                                                       job_work_images_dir,
                                                       model_info_dict,
                                                       date_info_dict,
                                                       plot_info_dict,
                                                       met_info_dict,
                                                       logo_dir)
                    plot_ta.make_threshold_average()
    elif plot == 'lead_by_date':
        import subseasonal_plots_lead_by_date as subp_lbd
        for lbd_info in \
                list(itertools.product(valid_hrs, var_info,
                                       interp_points_list)):
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
            plot_info_dict['interp_points'] = str(lbd_info[2])
            image_name = plot_specs.get_savefig_name(
                job_work_images_dir,
                plot_info_dict, date_info_dict
            )
            if not os.path.exists(image_name):
                if len(date_info_dict['forecast_hours']) <= 1:
                    logger.warning("No span of forecast hours to plot, "
                                   +"given 1 forecast hour, skipping "
                                   +"lead_by_date plots")
                    make_lbd = False
                else:
                    if plot_info_dict['stat'] == 'FBAR_OBAR':
                        make_lbd = False
                    else:
                        make_lbd = True
            else:
                make_lbd = False
            if make_lbd:
                plot_lbd = subp_lbd.LeadByDate(logger, job_DATA_dir,
                                               job_work_images_dir, 
                                               model_info_dict,
                                               date_info_dict, plot_info_dict,
                                               met_info_dict, logo_dir)
                plot_lbd.make_lead_by_date()
    elif plot == 'stat_by_level':
        import subseasonal_plots_stat_by_level as subp_sbl
        vert_profiles = [os.environ['vert_profile']]
        for sbl_info in \
                list(itertools.product(valid_hrs, fhrs, interp_points_list,
                                       vert_profiles)):
            date_info_dict['valid_hr_start'] = str(sbl_info[0])
            date_info_dict['valid_hr_end'] = str(sbl_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(sbl_info[1])
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['interp_points'] = str(sbl_info[2])
            plot_info_dict['vert_profile'] = sbl_info[3]
            init_hr = sub_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            plot_info_dict['fcst_var_level'] = sbl_info[3]
            plot_info_dict['obs_var_level'] = sbl_info[3]
            for t in range(len(fcst_var_thresh_list)):
                plot_info_dict['fcst_var_thresh'] = fcst_var_thresh_list[t]
                plot_info_dict['obs_var_thresh'] = obs_var_thresh_list[t]
                image_name = plot_specs.get_savefig_name(
                    job_work_images_dir,
                    plot_info_dict, date_info_dict
                )
                if init_hr in init_hrs:
                    if not os.path.exists(image_name):
                        if plot_info_dict['stat'] == 'FBAR_OBAR':
                            make_sbl = False
                        else:
                            make_sbl = True
                    else:
                        make_sbl = False
                else:
                    make_sbl = False
                del plot_info_dict['fcst_var_level']
                del plot_info_dict['obs_var_level']
                if make_sbl:
                    plot_sbl = subp_sbl.StatByLevel(logger, job_DATA_dir,
                                                    job_work_images_dir,
                                                    model_info_dict,
                                                    date_info_dict,
                                                    plot_info_dict,
                                                    met_info_dict,
                                                    logo_dir)
                    plot_sbl.make_stat_by_level()
    elif plot == 'lead_by_level':
        import subseasonal_plots_lead_by_level as subp_lbl
        if int(fhr_inc) == 6:
            fhrs_lbl = list(
                range(int(fhr_start), int(fhr_end)+int(fhr_inc), 24)
            )
        else:
            fhrs_lbl = fhrs
        vert_profiles = [os.environ['vert_profile']]
        for lbl_info in \
                list(itertools.product(valid_hrs, interp_points_list,
                                       vert_profiles)):
            date_info_dict['valid_hr_start'] = str(lbl_info[0])
            date_info_dict['valid_hr_end'] = str(lbl_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hours'] = fhrs_lbl
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['interp_points'] = str(lbl_info[1])
            plot_info_dict['vert_profile'] = lbl_info[2]
            plot_info_dict['fcst_var_level'] = lbl_info[2]
            plot_info_dict['obs_var_level'] = lbl_info[2]
            for t in range(len(fcst_var_thresh_list)):
                plot_info_dict['fcst_var_thresh'] = fcst_var_thresh_list[t]
                plot_info_dict['obs_var_thresh'] = obs_var_thresh_list[t]
                image_name = plot_specs.get_savefig_name(
                    job_work_images_dir,
                    plot_info_dict, date_info_dict
                )
                if not os.path.exists(image_name):
                    if len(date_info_dict['forecast_hours']) <= 1:
                        logger.warning("No span of forecast hours to plot, "
                                       +"given 1 forecast hour, skipping "
                                       +"lead_by_level plots")
                    else:
                        if plot_info_dict['stat'] == 'FBAR_OBAR':
                            make_lbl = False
                        else:
                            make_lbl = True
                else:
                    make_lbl = False
                del plot_info_dict['fcst_var_level']
                del plot_info_dict['obs_var_level']
                if make_lbl:
                    plot_lbl = subp_lbl.LeadByLevel(logger, job_DATA_dir,
                                                    job_work_images_dir,
                                                    model_info_dict,
                                                    date_info_dict,
                                                    plot_info_dict,
                                                    met_info_dict, logo_dir)
                    plot_lbl.make_lead_by_level()
    elif plot == 'performance_diagram':
        import subseasonal_plots_performance_diagram as subp_pd
        for pd_info in \
                list(itertools.product(valid_hrs, fhrs, interp_points_list)):
            date_info_dict['valid_hr_start'] = str(pd_info[0])
            date_info_dict['valid_hr_end'] = str(pd_info[0])
            date_info_dict['valid_hr_inc'] = '24'
            date_info_dict['forecast_hour'] = str(pd_info[1])
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['fcst_var_threshs'] = fcst_var_thresh_list
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['obs_var_threshs'] = obs_var_thresh_list
            plot_info_dict['interp_points'] = str(pd_info[2])
            init_hr = sub_util.get_init_hour(
                int(date_info_dict['valid_hr_start']),
                int(date_info_dict['forecast_hour'])
            )
            for l in range(len(fcst_var_level_list)):
                plot_info_dict['fcst_var_level'] = fcst_var_level_list[l]
                plot_info_dict['obs_var_level'] = obs_var_level_list[l]
                image_name = plot_specs.get_savefig_name(
                    job_work_images_dir,
                    plot_info_dict, date_info_dict
                )
                if init_hr in init_hrs:
                    if not os.path.exists(image_name):
                        make_pd = True
                    else:
                        make_pd = False
                else:
                    make_pd = False
                if make_pd:
                    plot_pd = subp_pd.PerformanceDiagram(logger, job_DATA_dir,
                                                         job_work_images_dir,
                                                         model_info_dict,
                                                         date_info_dict,
                                                         plot_info_dict,
                                                         met_info_dict,
                                                         logo_dir)
                    plot_pd.make_performance_diagram()
    else:
        logger.warning(plot+" not recognized")

# Create tar file of plots and move to main image directory
elif JOB_GROUP == 'tar_images':
    logger.info("Tar'ing up images")
    job_input_image_dir = os.path.join(
        DATA, VERIF_CASE+'_'+STEP, 'plot_output',
        RUN+'.'+end_date, VERIF_TYPE,
        job_name.replace('/','_'), 'images'
    )
    cwd = os.getcwd()
    if len(glob.glob(job_input_image_dir+'/*')) != 0:
        os.chdir(job_input_image_dir)
        tar_file = os.path.join(VERIF_TYPE_tar_dir,
                                job_name.replace('/','_')+'.tar')
        if os.path.exists(tar_file):
            os.remove(tar_file)
        logger.debug(f"Making tar file {tar_file} from {job_input_image_dir}")
        sub_util.run_shell_command(
            ['tar', '-cvf', tar_file, '*']
        )
        os.chdir(cwd)
    else:
        logger.warning(f"No images generated in {job_input_image_dir}")


print("END: "+os.path.basename(__file__))
