'''
Name: global_det_atmos_plots.py
Contact(s): Mallory Row
Abstract: This script is main driver for the plotting scripts.
'''

import os
import sys
import logging
import datetime
import glob
import subprocess
import itertools
import shutil
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
FIXevs = os.environ['FIXevs']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
plot_verbosity = os.environ['plot_verbosity']
event_equalization = os.environ['event_equalization']
job_name = os.environ['job_name']
line_type = os.environ['line_type']
stat = os.environ['stat']
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
model_list = os.environ['model_list'].split(' ')
model_plot_name_list = os.environ['model_plot_name_list'].split(' ')
plots_list = os.environ['plots_list'].split(', ')
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
if VERIF_CASE == 'grid2grid' and VERIF_TYPE == 'pres_levs':
   truth_name_list = os.environ['truth_name_list'].split(' ') 
else:
   obs_name = os.environ['obs_name']

# Set variables
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
now = datetime.datetime.now()

# Set up directory paths
logo_dir = os.path.join(FIXevs, 'logos')
VERIF_CASE_STEP_dir = os.path.join(DATA, VERIF_CASE_STEP)
stat_base_dir = os.path.join(VERIF_CASE_STEP_dir, 'data')
plot_output_dir = os.path.join(VERIF_CASE_STEP_dir, 'plot_output')
logging_dir = os.path.join(plot_output_dir, RUN+'.'+end_date, 'logs')
VERIF_TYPE_image_dir = os.path.join(plot_output_dir, RUN+'.'+end_date,
                                    'images', VERIF_TYPE)
job_output_dir = os.path.join(plot_output_dir, RUN+'.'+end_date,
                              VERIF_TYPE,job_name.replace('/','_'))
if not os.path.exists(job_output_dir):
    os.makedirs(job_output_dir)

# Set up logging
job_logging_file = os.path.join(logging_dir, 'evs_'+COMPONENT+'_'+RUN+'_'
                                +VERIF_CASE+'_'+STEP+'_'+VERIF_TYPE+'_'
                                +job_name.replace('/','_')+'_runon'
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

if len(model_list) > 10:
    logger.error("TOO MANY MODELS LISTED ("+str(len(model_list))
                 +", ["+', '.join(model_list)+"]), maximum is 10")
    sys.exit(1)

# Condense .stat files
logger.info("Condensing model .stat files for job")
for model_idx in range(len(model_list)):
    model = model_list[model_idx]
    condensed_model_stat_file = os.path.join(job_output_dir, 'model'
                                             +str(model_idx+1)+'_'+model
                                             +'.stat')
    if VERIF_CASE == 'grid2grid' and VERIF_TYPE == 'pres_levs':
        obs_name = truth_name_list[model_idx]
    gda_util.condense_model_stat_files(logger, stat_base_dir,
                                       condensed_model_stat_file, model,
                                       obs_name, grid, vx_mask, fcst_var_name,
                                       obs_var_name, line_type)

# Set up model information dictionary
model_info_dict = {}
for model_idx in range(len(model_list)):
    model_num = model_idx + 1
    model_info_dict['model'+str(model_num)] = {
        'name': model_list[model_idx],
        'plot_name': model_plot_name_list[model_idx],
    }
    if VERIF_CASE == 'grid2grid' and VERIF_TYPE == 'pres_levs':
         model_info_dict['model'+str(model_num)]['obs_name'] = (
             truth_name_list[model_idx]
         )
    elif VERIF_CASE == 'grid2grid' and VERIF_TYPE == 'means':
         model_info_dict['model'+str(model_num)]['obs_name'] = (
             model_list[model_idx]
         )
    else:
        model_info_dict['model'+str(model_num)]['obs_name'] = obs_name

# Set up date information dictionary
date_info_dict = {
    'date_type': date_type,
    'start_date': start_date,
    'end_date': end_date,
    'valid_hr_start': valid_hr_start,
    'valid_hr_end': valid_hr_end,
    'valid_hr_inc': valid_hr_inc,
    'init_hr_start': init_hr_start,
    'init_hr_end': init_hr_end,
    'init_hr_inc': init_hr_inc,
}
fhrs = list(range(int(fhr_start), int(fhr_end)+int(fhr_inc), int(fhr_inc)))

# Set up plot information dictionary
plot_info_dict = {
    'line_type': line_type,
    'grid': grid,
    'stat': stat,
    'vx_mask': vx_mask,
    'interp_method': interp_method,
    'event_equalization': event_equalization
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
    logger.error("FORECAST AND OBSERVATION VARIABLE INFORMATION NOT THE "
                 +"SAME LENGTH")
    sys.exit(1)

# Set up MET information dictionary
met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}

# Make the plots
for plot in plots_list:
    if plot == 'time_series':
        import global_det_atmos_plots_time_series as gdap_ts
        for fhr_var_interppts_info in \
                list(itertools.product(fhrs, var_info, interp_points_list)):
            date_info_dict['forecast_hour'] = str(
                fhr_var_interppts_info[0]
            )
            plot_info_dict['fcst_var_name'] = (
                fhr_var_interppts_info[1][0][0]
            )
            plot_info_dict['fcst_var_level'] = (
                fhr_var_interppts_info[1][0][1]
            )
            plot_info_dict['fcst_var_thresh'] = (
                fhr_var_interppts_info[1][0][2]
            )
            plot_info_dict['obs_var_name'] = (
                fhr_var_interppts_info[1][1][0]
            )
            plot_info_dict['obs_var_level'] = (
                fhr_var_interppts_info[1][1][1]
            )
            plot_info_dict['obs_var_thresh'] = (
                fhr_var_interppts_info[1][1][2]
            )
            plot_info_dict['interp_points'] = str(
                fhr_var_interppts_info[2]
            )
            plot_ts = gdap_ts.TimeSeries(logger, job_output_dir, job_output_dir,
                                         model_info_dict, date_info_dict,
                                         plot_info_dict, met_info_dict, logo_dir)
            plot_ts.make_time_series()
    elif plot == 'lead_average':
        import global_det_atmos_plots_lead_average as gdap_la
        for var_interppts_info in \
                list(itertools.product(var_info, interp_points_list)):
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = (
                var_interppts_info[0][0][0]
            )
            plot_info_dict['fcst_var_level'] = (
                var_interppts_info[0][0][1]
            )
            plot_info_dict['fcst_var_thresh'] = (
                var_interppts_info[0][0][2]
            )
            plot_info_dict['obs_var_name'] = (
                var_interppts_info[0][1][0]
            )
            plot_info_dict['obs_var_level'] = (
                var_interppts_info[0][1][1]
            )
            plot_info_dict['obs_var_thresh'] = (
                var_interppts_info[0][1][2]
            )
            plot_info_dict['interp_points'] = str(
                var_interppts_info[1]
            )
            plot_la = gdap_la.LeadAverage(logger, job_output_dir, job_output_dir,
                                          model_info_dict, date_info_dict,
                                          plot_info_dict, met_info_dict, logo_dir)
            plot_la.make_lead_average()
    elif plot == 'valid_hour_average':
        import global_det_atmos_plots_valid_hour_average as gdap_vha
        for var_interppts_info in \
                list(itertools.product(var_info, interp_points_list)):
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = (
                var_interppts_info[0][0][0]
            )
            plot_info_dict['fcst_var_level'] = (
                var_interppts_info[0][0][1]
            )
            plot_info_dict['fcst_var_thresh'] = (
                var_interppts_info[0][0][2]
            )
            plot_info_dict['obs_var_name'] = (
                var_interppts_info[0][1][0]
            )
            plot_info_dict['obs_var_level'] = (
                var_interppts_info[0][1][1]
            )
            plot_info_dict['obs_var_thresh'] = (
                var_interppts_info[0][1][2]
            )
            plot_info_dict['interp_points'] = str(
                var_interppts_info[1]
            )
            plot_vha = gdap_vha.ValidHourAverage(logger, job_output_dir,
                                                 job_output_dir,
                                                 model_info_dict,
                                                 date_info_dict,
                                                 plot_info_dict,
                                                 met_info_dict, logo_dir)
            plot_vha.make_valid_hour_average()
    elif plot == 'threshold_average':
        import global_det_atmos_plots_threshold_average as gdap_ta
        for fhr_interppts_info in \
                list(itertools.product(fhrs, interp_points_list)):
            date_info_dict['forecast_hour'] = str(
                fhr_interppts_info[0]
            )
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['fcst_var_threshs'] = fcst_var_thresh_list
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['obs_var_threshs'] = obs_var_thresh_list
            plot_info_dict['interp_points'] = str(
                fhr_interppts_info[1]
            )
            for l in range(len(fcst_var_level_list)):
                plot_info_dict['fcst_var_level'] = fcst_var_level_list[l]
                plot_info_dict['obs_var_level'] = obs_var_level_list[l]
                plot_ta = gdap_ta.ThresholdAverage(logger, job_output_dir,
                                                   job_output_dir,
                                                   model_info_dict,
                                                   date_info_dict,
                                                   plot_info_dict,
                                                   met_info_dict,
                                                   logo_dir)
                plot_ta.make_threshold_average()
    elif plot == 'lead_by_date':
        import global_det_atmos_plots_lead_by_date as gdap_lbd
        for var_interppts_info in \
                list(itertools.product(var_info, interp_points_list)):
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = (
                var_interppts_info[0][0][0]
            )
            plot_info_dict['fcst_var_level'] = (
                var_interppts_info[0][0][1]
            )
            plot_info_dict['fcst_var_thresh'] = (
                var_interppts_info[0][0][2]
            )
            plot_info_dict['obs_var_name'] = (
                var_interppts_info[0][1][0]
            )
            plot_info_dict['obs_var_level'] = (
                var_interppts_info[0][1][1]
            )
            plot_info_dict['obs_var_thresh'] = (
                var_interppts_info[0][1][2]
            )
            plot_info_dict['interp_points'] = str(
                var_interppts_info[1]
            )
            plot_lbd = gdap_lbd.LeadByDate(logger, job_output_dir, job_output_dir,
                                           model_info_dict, date_info_dict,
                                           plot_info_dict, met_info_dict, logo_dir)
            plot_lbd.make_lead_by_date()
    elif plot == 'stat_by_level':
        import global_det_atmos_plots_stat_by_level as gdap_sbl
        for fhr_interppts_info in \
                list(itertools.product(fhrs, interp_points_list)):
            date_info_dict['forecast_hour'] = str(
                fhr_interppts_info[0]
            )
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['vert_profiles'] = ['all', 'trop', 'strat',
                                               'lower_trop', 'upper_trop']
            plot_info_dict['interp_points'] = str(
                fhr_interppts_info[1]
            )
            for t in range(len(fcst_var_thresh_list)):
                plot_info_dict['fcst_var_thresh'] = fcst_var_thresh_list[t]
                plot_info_dict['obs_var_thresh'] = obs_var_thresh_list[t]
                plot_sbl = gdap_sbl.StatByLevel(logger, job_output_dir,
                                                job_output_dir,
                                                model_info_dict,
                                                date_info_dict,
                                                plot_info_dict,
                                                met_info_dict,
                                                logo_dir)
                plot_sbl.make_stat_by_level()
    elif plot == 'lead_by_level':
        import global_det_atmos_plots_lead_by_level as gdap_lbl
        for interppts in interp_points_list:
            date_info_dict['forecast_hours'] = fhrs
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['vert_profiles'] = ['all', 'trop', 'strat',
                                               'lower_trop', 'upper_trop']
            plot_info_dict['interp_points'] = str(interppts)
            for t in range(len(fcst_var_thresh_list)):
                plot_info_dict['fcst_var_thresh'] = fcst_var_thresh_list[t]
                plot_info_dict['obs_var_thresh'] = obs_var_thresh_list[t]
                plot_lbl = gdap_lbl.LeadByLevel(logger, job_output_dir,
                                                job_output_dir,
                                                model_info_dict,
                                                date_info_dict,
                                                plot_info_dict,
                                                met_info_dict,
                                                logo_dir)
                plot_lbl.make_lead_by_level()
    elif plot == 'precip_spatial_map':
        model_info_dict['obs'] = {'name': 'ccpa',
                                  'plot_name': 'ccpa',
                                  'obs_name': '24hrCCPA'}
        pcp_combine_base_dir = os.path.join(VERIF_CASE_STEP_dir, 'data')
        import global_det_atmos_plots_precip_spatial_map as gdap_psm
        for fhr in fhrs:
            date_info_dict['forecast_hour'] = str(fhr)
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['fcst_var_level'] = fcst_var_level_list[0]
            plot_info_dict['fcst_var_thresh'] = 'NA'
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['obs_var_level'] = obs_var_level_list[0]
            plot_info_dict['obs_var_thresh'] = 'NA'
            plot_info_dict['interp_points'] = 'NA'
            plot_psm = gdap_psm.PrecipSpatialMap(logger, pcp_combine_base_dir,
                                                 job_output_dir, model_info_dict,
                                                 date_info_dict, plot_info_dict,
                                                 met_info_dict, logo_dir)
            plot_psm.make_precip_spatial_map()
    elif plot == 'performance_diagram':
        import global_det_atmos_plots_performance_diagram as gdap_pd
        for fhr_interppts_info in \
                list(itertools.product(fhrs, interp_points_list)):
            date_info_dict['forecast_hour'] = str(
                fhr_interppts_info[0]
            )
            plot_info_dict['fcst_var_name'] = fcst_var_name
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['fcst_var_threshs'] = fcst_var_thresh_list
            plot_info_dict['obs_var_name'] = obs_var_name
            plot_info_dict['obs_var_threshs'] = obs_var_thresh_list
            plot_info_dict['interp_points'] = str(
                fhr_interppts_info[1]
            )
            for l in range(len(fcst_var_level_list)):
                plot_info_dict['fcst_var_level'] = fcst_var_level_list[l]
                plot_info_dict['obs_var_level'] = obs_var_level_list[l]
                plot_pd = gdap_pd.PerformanceDiagram(logger, job_output_dir,
                                                     job_output_dir,
                                                     model_info_dict,
                                                     date_info_dict,
                                                     plot_info_dict,
                                                     met_info_dict,
                                                     logo_dir)
                plot_pd.make_performance_diagram()

# Copy images from job directory to main image directory
job_output_image_dir = os.path.join(job_output_dir, 'images')
if len(glob.glob(job_output_image_dir+'/*')) != 0:
    for job_output_image in glob.glob(job_output_image_dir+'/*'):
        logger.debug(f"Copying {job_output_image} to {VERIF_TYPE_image_dir}")
        shutil.copy2(job_output_image, VERIF_TYPE_image_dir)            
else:
    logger.warning(f"No images generated in {job_output_image_dir}")

print("END: "+os.path.basename(__file__))
