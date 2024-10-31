#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_production_tof240.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This is the driver script for creating plots.
          It is only used in production to generate plots to
          forecast hour 240.
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

if os.environ['JOB_GROUP'] != "make_plots":
    print(os.path.basename(__file__)+" for JOB_GROUP = "
          +"make_plots only")
    sys.exit(1)

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
plot_verbosity = os.environ['plot_verbosity']
line_type = os.environ['line_type']
fcst_var_name = os.environ['fcst_var_name']
obs_var_name = os.environ['obs_var_name']
vx_mask = os.environ['vx_mask']
model_list = os.environ['model_list'].split(', ')
model_plot_name_list = os.environ['model_plot_name_list'].split(', ')
obs_list = os.environ['obs_list'].split(', ')
VERIF_TYPE = os.environ['VERIF_TYPE']
date_type = os.environ['date_type']
job_id = os.environ['job_id']
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
    'init_hr_inc': init_hr_inc
}
valid_hrs = list(range(int(valid_hr_start),
                       int(valid_hr_end)+int(valid_hr_inc),
                       int(valid_hr_inc)))
init_hrs = list(range(int(init_hr_start),
                      int(init_hr_end)+int(init_hr_inc),
                      int(init_hr_inc)))
fhrs = []
for fhr in fhr_list.split(', '):
    if int(fhr) <= 240:
        fhrs.append(int(fhr))

# Set up plot information dictionary
original_plot_info_dict = {
    'line_type': line_type,
    'vx_mask': vx_mask,
    'grid': grid,
    'interp_method': interp_method,
    'interp_points': interp_points,
    'event_equalization': event_equalization,
    'stat': stat
}
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
   logger.error("Forecast and observation variable information not the "
                +"same length")
   sys.exit(1)

# Set up MET information dictionary
original_met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}

if JOB_GROUP == 'make_plots':
    if len(model_list) > 10:
        logger.error("Too many models requested ("+str(len(model_list))
                     +", ["+', '.join(model_list)+"]), maximum is 10")
        sys.exit(1)
    plot_specs = PlotSpecs(logger, plot)
    model_info_dict = original_model_info_dict.copy()
    date_info_dict = original_date_info_dict.copy()
    plot_info_dict = original_plot_info_dict.copy()
    met_info_dict = original_met_info_dict.copy()
    if plot == 'lead_average':
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
                    gda_util.copy_file(job_work_image_name, job_COMOUT_image_name)
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
                                   +"lead_by_date plots")
                    make_lbd = False
                else:
                    make_lbd = True
            else:
                make_lbd = False
            if make_lbd:
                plot_lbd = gdap_lbd.LeadByDate(logger, job_input_dir+'/..',
                                               job_work_dir, model_info_dict,
                                               date_info_dict, plot_info_dict,
                                               met_info_dict, logo_dir)
                plot_lbd.make_lead_by_date()
                if SENDCOM == 'YES' and os.path.exists(job_work_image_name):
                    logger.info(f"Copying {job_work_image_name} to "
                                +f"{job_COMOUT_image_name}")
                    gda_util.copy_file(job_work_image_name, job_COMOUT_image_name)
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
                                       +"lead_by_level plots")
                        make_lbl = False
                    else:
                        make_lbl = True
                else:
                    make_lbl = False
                del plot_info_dict['fcst_var_level']
                del plot_info_dict['obs_var_level']
                if make_lbl:
                    plot_lbl = gdap_lbl.LeadByLevel(logger,
                                                    job_input_dir+'/..',
                                                    job_work_dir,
                                                    model_info_dict,
                                                    date_info_dict,
                                                    plot_info_dict,
                                                    met_info_dict, logo_dir)
                    plot_lbl.make_lead_by_level()
                    if SENDCOM == 'YES' \
                            and os.path.exists(job_work_image_name):
                        logger.info(f"Copying {job_work_image_name} to "
                                    +f"{job_COMOUT_image_name}")
                        gda_util.copy_file(job_work_image_name,
                                           job_COMOUT_image_name)
    else:
        logger.error(plot+" not recongized")
        sys.exit(1)

print("END: "+os.path.basename(__file__))
