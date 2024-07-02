#!/usr/bin/env python3
'''
Name: global_det_atmos_plots_long_term.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This is the driver script for creating long-term plots.
Run By: scripts/plots/global_det/exevs_global_det_atmos_long_term_plots.sh
'''

import sys
import os
import shutil
import logging
import datetime
import dateutil
import calendar
import pandas as pd
pd.plotting.deregister_matplotlib_converters()
#pd.plotting.register_matplotlib_converters()
import numpy as np
import itertools
import global_det_atmos_util as gda_util
import glob

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
FIXevs = os.environ['FIXevs']
MET_ROOT = os.environ['MET_ROOT']
met_ver = os.environ['met_ver']
evs_run_mode = os.environ['evs_run_mode']
COMIN = os.environ['COMIN']
VDATEYYYY = os.environ['VDATEYYYY']
VDATEmm = os.environ['VDATEmm']

# Set up time ranges to do averages for
avg_time_range_list = ['monthly']
if VDATEmm == '12':
    avg_time_range_list.append('yearly')

# Set up plotting information
model_group_dict = {'all_models': ['gfs', 'ecmwf', 'cmc', 'fnmoc', 'ukmet'],
                    'gfs_ecmwf': ['ecmwf', 'gfs'],
                    'gfs_4cycles': ['gfs00Z', 'gfs06Z', 'gfs12Z', 'gfs18Z']}
plot_info_dict = {'HGT': {'level_list': ['P1000', 'P500'],
                          'vx_mask_list': ['NHEM', 'SHEM'],
                          'stat_list': ['ACC', 'ME', 'RMSE']},
                  'UGRD_VGRD': {'level_list': ['P850', 'P200'],
                                'vx_mask_list': ['TROPICS'],
                                'stat_list': ['ME', 'RMSE']}}
for avg_time_range in avg_time_range_list:
    # Set forecast days to plot
    forecast_day_list = [str(x) for x in np.arange(0,11,1)]
    # Set run lengths to plot
    run_length_list = ['allyears', 'past10years']
    # Set time range stats directory
    time_range_stats_dir = os.path.join(COMIN, 'stats', COMPONENT, RUN,
                                        f"{avg_time_range}_means")
    # Set up time range directory
    avg_time_range_dir = os.path.join(DATA, avg_time_range)
    gda_util.make_dir(avg_time_range_dir)
    ### Do grid-to-grid plots
    print(f"Doing {avg_time_range} grid-to-grid plots")
    avg_time_range_g2g_dir = os.path.join(avg_time_range_dir, 'grid2grid')
    avg_time_range_logs_g2g_dir = os.path.join(avg_time_range_dir,
                                               'grid2grid', 'logs')
    avg_time_range_images_g2g_dir = os.path.join(avg_time_range_dir,
                                                 'grid2grid', 'images')
    gda_util.make_dir(avg_time_range_g2g_dir)
    gda_util.make_dir(avg_time_range_logs_g2g_dir)
    gda_util.make_dir(avg_time_range_images_g2g_dir)
    print(f"Working in {avg_time_range_g2g_dir}")
    # Make plots for groupings
    for model_group in list(model_group_dict.keys()):
        model_list = model_group_dict[model_group]
        print(f"Doing  model group {model_group}: "
              +f"{' '.join(model_list)}")
        now = datetime.datetime.now()
        logging_file = os.path.join(
            avg_time_range_logs_g2g_dir,
            'evs_'+COMPONENT+'_atmos_'+RUN+'_'+STEP+'_'+model_group
            +'_runon'+now.strftime('%Y%m%d%H%M%S')+'.log'
        )
        logger = gda_util.get_logger(logging_file)
        for var_name in list(plot_info_dict.keys()):
            if model_group == 'gfs_4cycles':
                start_YYYYmm = '200301'
            elif model_group == 'all_models' and var_name == 'UGRD_VGRD':
                start_YYYYmm = '201001'
            else:
                start_YYYYmm = '199601'
            if avg_time_range == 'monthly':
                all_dt_list = list(
                    dateutil.rrule.rrule(
                        dateutil.rrule.MONTHLY,
                        dtstart=dateutil.parser.parse(start_YYYYmm
                                                      +'01T000000'),
                        until=dateutil.parser.parse(VDATEYYYY+VDATEmm
                                                    +'01T000000')
                    )
                )
            elif avg_time_range == 'yearly':
                all_dt_list = list(
                    dateutil.rrule.rrule(
                        dateutil.rrule.YEARLY,
                        dtstart=dateutil.parser.parse(start_YYYYmm[0:4]
                                                      +'0101T000000'),
                        until=dateutil.parser.parse(VDATEYYYY
                                                    +'0101T000000')
                    )
                )
            for plot_loop in list(
                itertools.product(plot_info_dict[var_name]['level_list'],
                                  plot_info_dict[var_name]['vx_mask_list'],
                                  plot_info_dict[var_name]['stat_list'])
            ):
                var_level = plot_loop[0]
                vx_mask = plot_loop[1]
                stat = plot_loop[2]
                logger.info(f"Working on {avg_time_range} {model_group}: "
                            +f"{var_name} {var_level} {vx_mask} {stat}")
                if avg_time_range == 'monthly':
                    import global_det_atmos_plots_long_term_time_series_diff \
                        as gdap_lttsd
                    plot_lttsd = gdap_lttsd.LongTermTimeSeriesDiff(
                        logger, time_range_stats_dir, avg_time_range_g2g_dir,
                        os.path.join(FIXevs, 'logos'), avg_time_range,
                        all_dt_list, model_group, model_list, var_name,
                        var_level, 'NA', 'G004', vx_mask, stat, 'NA',
                        forecast_day_list, run_length_list
                    )
                    plot_lttsd.make_long_term_time_series_diff()
                    import global_det_atmos_plots_long_term_lead_by_date \
                        as gdap_ltlbd
                    plot_ltlbd = gdap_ltlbd.LongTermLeadByDate(
                        logger, time_range_stats_dir, avg_time_range_g2g_dir,
                        os.path.join(FIXevs, 'logos'), avg_time_range,
                        all_dt_list, model_group, model_list, var_name,
                        var_level, 'NA', 'G004', vx_mask, stat, 'NA',
                        forecast_day_list, run_length_list
                    )
                    plot_ltlbd.make_long_term_lead_by_date()
                    if stat == 'ACC' and var_name == 'HGT' \
                            and model_group == 'all_models':
                        import global_det_atmos_plots_long_term_useful_forecast_days \
                            as gdap_ltufd
                        plot_ltufd = gdap_ltufd.LongTermUsefulForecastDays(
                            logger, time_range_stats_dir,
                            avg_time_range_g2g_dir,
                            os.path.join(FIXevs, 'logos'), avg_time_range,
                            all_dt_list, model_group, model_list, var_name,
                            var_level, 'NA', 'G004', vx_mask, stat, 'NA',
                            run_length_list
                        )
                        plot_ltufd.make_long_term_useful_forecast_days_time_series()
                elif avg_time_range == 'yearly':
                    import global_det_atmos_plots_long_term_annual_mean \
                        as gdap_ltam
                    plot_ltam = gdap_ltam.LongTermAnnualMean(
                        logger, time_range_stats_dir, avg_time_range_g2g_dir,
                        os.path.join(FIXevs, 'logos'), avg_time_range,
                        all_dt_list, model_group, model_list, var_name,
                        var_level, 'NA', 'G004', vx_mask, stat, 'NA',
                        forecast_day_list, run_length_list
                    )
                    plot_ltam.make_long_term_annual_mean()

# Make monthly ACC archive plots
print(f"Making {VDATEYYYY} {VDATEmm} "
      +"Grid-to-Grid - Geopotential Height 500-hPa ACC NH plots")
yyyymm_acc_dir = os.path.join(DATA, VDATEYYYY+'_'+VDATEmm+'_ACC')
yyyymm_acc_logs_dir = os.path.join(yyyymm_acc_dir, 'logs')
yyyymm_acc_data_dir = os.path.join(yyyymm_acc_dir, 'data')
yyyymm_acc_images_dir = os.path.join(yyyymm_acc_dir, 'images')
gda_util.make_dir(yyyymm_acc_dir)
gda_util.make_dir(yyyymm_acc_logs_dir)
gda_util.make_dir(yyyymm_acc_data_dir)
gda_util.make_dir(yyyymm_acc_images_dir)
print(f"Working in {yyyymm_acc_dir}")
yyyymm_acc_forecast_hour_list = list(range(0, 240+24, 24))
yyyymm_acc_valid_hour_list = [str(x).zfill(2) for x in np.arange(0,13,12)]
yyyymm_acc_met_info_dict = {
    'root': MET_ROOT,
    'version': met_ver
}
yyyymm_acc_model_info_dict = {
    'model1': {'name': 'gfs',
               'plot_name': 'gfs',
               'obs_name': 'gfs_anl'},
    'model2': {'name': 'ecmwf',
               'plot_name': 'ecmwf',
               'obs_name': 'ecmwf_anl'},
    'model3': {'name': 'cmc',
               'plot_name': 'cmc',
               'obs_name': 'cmc_anl'},
    'model4': {'name': 'ukmet',
               'plot_name': 'ukmet',
               'obs_name': 'ukmet_anl'},
    'model5': {'name': 'jma',
               'plot_name': 'jma',
               'obs_name': 'jma_anl'},
    'model6': {'name': 'imd',
               'plot_name': 'imd',
               'obs_name': 'imd_anl'},
    'model7': {'name': 'fnmoc',
               'plot_name': 'fnmoc',
               'obs_name': 'fnmoc_anl'},
    'model8': {'name': 'cfs',
               'plot_name': 'cfs',
               'obs_name': 'gfs_anl'},
}
yyyymm_acc_plot_info_dict = {
    'line_type': 'SAL1L2',
    'grid': 'G004',
    'stat': 'ACC',
    'vx_mask': 'NHEM',
    'event_equalization': 'NO',
    'interp_method': 'NEAREST',
    'interp_points': '1',
    'fcst_var_name': 'HGT',
    'fcst_var_level': 'P500',
    'fcst_var_thresh': 'NA',
    'obs_var_name': 'HGT',
    'obs_var_level': 'P500',
    'obs_var_thresh': 'NA',
}
yyyymm_acc_date_info_dict = {
    'date_type': 'VALID',
    'start_date': VDATEYYYY+VDATEmm+'01',
    'end_date': (VDATEYYYY+VDATEmm
                 +str(calendar.monthrange(int(VDATEYYYY), int(VDATEmm))[1])),
    'valid_hr_inc': '24',
    'init_hr_inc': '24',
}
acc_job_name = ('GeoHeight/SA1L2/ACC/'
                +f"{yyyymm_acc_plot_info_dict['line_type']}/"
                +f"{yyyymm_acc_plot_info_dict['vx_mask']}")
acc_output_dir = os.path.join(
    yyyymm_acc_dir, acc_job_name.replace('/','_')
)
gda_util.make_dir(acc_output_dir)
now = datetime.datetime.now()
acc_logging_file = os.path.join(
    yyyymm_acc_logs_dir,
    'evs_'+COMPONENT+'_atmos_'+RUN+'_'+STEP+'_'
    +acc_job_name.replace('/','_')+'_runon'
    +now.strftime('%Y%m%d%H%M%S')+'.log'
)
acc_logger = gda_util.get_logger(acc_logging_file)
# Get model daily stat files and condense
for model_num in list(yyyymm_acc_model_info_dict.keys()):
    model = yyyymm_acc_model_info_dict[model_num]['name']
    obs_name = yyyymm_acc_model_info_dict[model_num]['obs_name']
    stat_model_dir = os.path.join(yyyymm_acc_data_dir, model)
    gda_util.make_dir(stat_model_dir)
    date_dt = datetime.datetime.strptime(
        yyyymm_acc_date_info_dict['start_date'], '%Y%m%d'
    )
    while date_dt <= datetime.datetime.strptime(
            yyyymm_acc_date_info_dict['end_date'],'%Y%m%d'
    ):
        source_model_date_stat_file = os.path.join(
            os.path.join(COMIN, 'stats', COMPONENT),
            model+'.'+date_dt.strftime('%Y%m%d'),
            'evs.stats.'+model+'.atmos.grid2grid.'
            +'v'+date_dt.strftime('%Y%m%d')+'.stat'
        )
        dest_model_date_stat_file = os.path.join(
            stat_model_dir,  model+'_grid2grid_v'+date_dt.strftime('%Y%m%d')
            +'.stat'
        )
        if not os.path.exists(dest_model_date_stat_file):
            if os.path.exists(source_model_date_stat_file):
                acc_logger.debug("Linking "+source_model_date_stat_file+" to "
                                 +dest_model_date_stat_file)
                os.symlink(source_model_date_stat_file,
                           dest_model_date_stat_file)
            else:
                acc_logger.debug(source_model_date_stat_file+" "
                                 +"DOES NOT EXIST")
        date_dt = date_dt + datetime.timedelta(days=1)
    acc_logger.info("Condensing model .stat files for job")
    gda_util.condense_model_stat_files(
        acc_logger, yyyymm_acc_data_dir, acc_output_dir,
        model, obs_name, yyyymm_acc_plot_info_dict['vx_mask'],
        yyyymm_acc_plot_info_dict['fcst_var_name'],
        yyyymm_acc_plot_info_dict['fcst_var_level'],
        yyyymm_acc_plot_info_dict['obs_var_name'],
        yyyymm_acc_plot_info_dict['obs_var_level'],
        yyyymm_acc_plot_info_dict['line_type']
    )
# Make time series and forecast mean plots
import global_det_atmos_plots_time_series as gdap_ts
import global_det_atmos_plots_lead_average as gdap_la
for valid_hour in yyyymm_acc_valid_hour_list:
    yyyymm_acc_date_info_dict['valid_hr_start'] = valid_hour
    yyyymm_acc_date_info_dict['valid_hr_end'] = valid_hour
    yyyymm_acc_date_info_dict['init_hr_start'] = valid_hour
    yyyymm_acc_date_info_dict['init_hr_end'] = valid_hour
    for fhr in yyyymm_acc_forecast_hour_list:
        yyyymm_acc_date_info_dict['forecast_hour'] = str(fhr)
        plot_ts = gdap_ts.TimeSeries(acc_logger, acc_output_dir,
                                     acc_output_dir,
                                     yyyymm_acc_model_info_dict,
                                     yyyymm_acc_date_info_dict,
                                     yyyymm_acc_plot_info_dict,
                                     yyyymm_acc_met_info_dict,
                                     os.path.join(FIXevs, 'logos'))
        plot_ts.make_time_series()
    del yyyymm_acc_date_info_dict['forecast_hour']
    yyyymm_acc_date_info_dict['forecast_hours'] = yyyymm_acc_forecast_hour_list
    plot_la = gdap_la.LeadAverage(acc_logger, acc_output_dir,
                                  acc_output_dir,
                                  yyyymm_acc_model_info_dict,
                                  yyyymm_acc_date_info_dict,
                                  yyyymm_acc_plot_info_dict,
                                  yyyymm_acc_met_info_dict,
                                  os.path.join(FIXevs, 'logos'))
    plot_la.make_lead_average()
# Rename images to have year month
VDATEYYYY_VDATEmm_ndays = int(
    (datetime.datetime.strptime(yyyymm_acc_date_info_dict['end_date'],
                                '%Y%m%d')
     - datetime.datetime.strptime(yyyymm_acc_date_info_dict['start_date'],
                                  '%Y%m%d')).total_seconds()/86400

) + 1
for old_image in glob.glob(os.path.join(acc_output_dir, '*.png')):
    old_image_name = old_image.rpartition('/')[2]
    new_image = os.path.join(
        yyyymm_acc_images_dir,
        old_image_name.replace('last'+str(VDATEYYYY_VDATEmm_ndays)+'days',
                               VDATEYYYY+VDATEmm)
    )
    print(f"Copying {old_image} to {new_image}")
    shutil.copy2(old_image, new_image)

print("END: "+os.path.basename(__file__))
