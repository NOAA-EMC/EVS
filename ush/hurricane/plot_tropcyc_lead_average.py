from __future__ import (print_function, division)
import os
import sys
import numpy as np
#import plot_util as plot_util
import plot_tropcyc_util as plot_util
import pandas as pd
import warnings
import matplotlib
import math
matplotlib.use('agg')
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# Plot Settings
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.titlepad'] = 15
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['xtick.major.pad'] = 10
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['ytick.major.pad'] = 10
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.subplot.top'] = 0.85
plt.rcParams['figure.subplot.bottom'] = 0.15
plt.rcParams['legend.handletextpad'] = 0.25
plt.rcParams['legend.handlelength'] = 1.25
plt.rcParams['legend.borderaxespad'] = 0
plt.rcParams['legend.columnspacing'] = 1.0
plt.rcParams['legend.frameon'] = False
x_figsize, y_figsize = 14, 7
legend_bbox_x, legend_bbox_y = 0, 1
legend_fontsize = 13
legend_loc = 'upper left'
legend_ncol = 1
title_loc = 'center'
model_type = os.environ['tropcyc_model_type']
if model_type == 'global':
  model_obs_plot_settings_dict = {
    'model1': {'color': '#000000',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 3},
    'model2': {'color': '#FB2020',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model3': {'color': '#1E3CFF',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model4': {'color': '#E69F00',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model5': {'color': '#00DC00',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model6': {'color': '#56B4E9',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model7': {'color': '#696969',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model8': {'color': '#8400C8',
               'marker': 'D', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model9': {'color': '#D269C1',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model10': {'color': '#F0E492',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'obs': {'color': '#AAAAAA',
            'marker': 'None', 'markersize': 0,
            'linestyle': 'solid', 'linewidth': 2}
  }
elif model_type == 'regional':
  model_obs_plot_settings_dict = {
    'model1': {'color': '#8400C8',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 3},
    'model2': {'color': '#00DC00',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 3},
    'model3': {'color': '#E63B7F',
               'marker': 'D', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 2.5},
    'model4': {'color': '#49D9DE',
               'marker': 'D', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 2.5},
    'model5': {'color': '#000000',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 2.5},
    'model6': {'color': '#56B4E9',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 2.5},
    'model7': {'color': '#696969',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model8': {'color': '#FB2020',
               'marker': 'D', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model9': {'color': '#D269C1',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model10': {'color': '#F0E492',
               'marker': 'o', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'obs': {'color': '#AAAAAA',
            'marker': 'None', 'markersize': 0,
            'linestyle': 'solid', 'linewidth': 2}
  }
elif model_type == 'regional_ops':
  model_obs_plot_settings_dict = {
    'model1': {'color': '#8400C8',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 3},
    'model2': {'color': '#00DC00',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model3': {'color': '#000000',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model4': {'color': '#56B4E9',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model5': {'color': '#696969',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
 }
elif model_type == 'regional_all':
  model_obs_plot_settings_dict = {
    'model1': {'color': '#1E3CFF',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 3},
    'model2': {'color': '#FF3399',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model3': {'color': '#56B4E9',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model4': {'color': '#E69F00',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model5': {'color': '#8400C8',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model6': {'color': '#00DC00',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model7': {'color': '#696969',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
 }
elif model_type == 'regional_legacy':
  model_obs_plot_settings_dict = {
    'model1': {'color': '#8400C8',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 3},
    'model2': {'color': '#00DC00',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model3': {'color': '#FF00FF',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model4': {'color': '#00FFFF',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model5': {'color': '#696969',
               'marker': 's', 'markersize': 6,
               'linestyle': 'solid', 'linewidth': 1.5},
 }
elif model_type == 'regional_all':
  model_obs_plot_settings_dict = {
    'model1': {'color': '#8400C8',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 3},
    'model2': {'color': '#00DC00',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 3},
    'model3': {'color': '#FF00FF',
               'marker': 'D', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model4': {'color': '#00FFFF',
               'marker': 'D', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model5': {'color': '#000000',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
    'model6': {'color': '#56B4E9',
               'marker': 'o', 'markersize': 7,
               'linestyle': 'solid', 'linewidth': 1.5},
 }


noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['LOGOroot'], 'noaa.png')
)
noaa_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.1
noaa_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.865
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['LOGOroot'], 'nws.png')
)
nws_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.9
nws_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.865
nws_logo_alpha = 0.5
# modified by Yan Jin
case_num_label_x_loc, case_num_label_y_loc = -0.05, -0.15
case_num_tick_y_loc = case_num_label_y_loc + 0.015

# Read in environment variables
PLOTDATA = os.environ['PLOTDATA']
RUN = os.environ['RUN']
fhr_list = os.environ['fhr_list'].split(',')
fhrs = np.asarray(fhr_list, dtype=int)
#init_hour_list = os.environ['init_hour_list'].split(',')
#valid_hour_list = os.environ['valid_hour_list'].split(',')
#model_atcf_name_list = os.environ['model_atcf_name_list'].split(',')
model_tmp_atcf_name_list = os.environ['model_tmp_atcf_name_list'].split(',')
model_plot_name_list = os.environ['model_plot_name_list'].split(',')
basin = os.environ['basin']
plot_CI_bars = os.environ['plot_CI_bars']
#model_type = os.environ['tropcyc_model_type']
print(model_type)
if 'tc_name' in list(os.environ.keys()):
    plot_info = os.environ['tc_name']
    year = plot_info.split('_')[1]
    name = plot_info.split('_')[2]
    tc_num = os.environ['tc_num']
else:
    plot_info = basin
tc_stat_file_dir = os.path.join(PLOTDATA,'tc_stat')    
#tc_stat_file_dir = os.path.join(PLOTDATA, RUN, 'metplus_output', 'gather',
#                                'tc_stat', plot_info)
plotting_out_dir_imgs = os.path.join(PLOTDATA, 'plot', plot_info, 'images')
#plotting_out_dir_imgs = os.path.join(PLOTDATA, RUN, 'metplus_output', 'plot',
#                                             plot_info, 'images')
if not os.path.exists(plotting_out_dir_imgs):
    os.makedirs(plotting_out_dir_imgs)
img_quality = os.environ['img_quality']

# Set image quality
#if img_quality == 'low':
#    plt.rcParams['savefig.dpi'] = 50
#elif img_quality == 'medium':
#    plt.rcParams['savefig.dpi'] = 75

# Read and plot stats
print("Working on track and intensity error plots for "+plot_info)
print("Reading in data")
summary_tcst_filename = os.path.join(tc_stat_file_dir, 'tc_stat.out')
if os.path.exists(summary_tcst_filename):
    nrow = sum(1 for line in open(summary_tcst_filename))
    if nrow == 3:
        print("ERROR: "+summary_tcst_filename+" empty")
        sys.exit(1)
    else:
        print(summary_tcst_filename+" exists")
        summary_tcst_file = open(summary_tcst_filename, 'r')
        tc_stat_job = summary_tcst_file.readline()
        summary_tcst_read_columns = summary_tcst_file.readline().split(' ')
        summary_tcst_file.close()
        tc_stat_summary_job_columns = []
        for col in summary_tcst_read_columns:
            if col != '':
                tc_stat_summary_job_columns.append(col.rstrip())
        summary_tcst_data = pd.read_csv(summary_tcst_filename,
                                        sep=" ", skiprows=2,
                                        skipinitialspace=True,
                                        header=None, dtype=str,
                                        names=tc_stat_summary_job_columns)
        summary_tcst_data_groupby_COLUMN = (
            summary_tcst_data.groupby(['COLUMN'])
        )
        for COLUMN_group in summary_tcst_data_groupby_COLUMN.groups.keys():
            print("Creating plot for "+COLUMN_group)
            if COLUMN_group == 'AMAX_WIND-BMAX_WIND':
                formal_stat_name = 'Intensity Bias (knots)'
            elif COLUMN_group == 'ABS(AMAX_WIND-BMAX_WIND)':
                formal_stat_name = 'Absolute Intensity Error (knots)'
            elif COLUMN_group == 'ABS(TK_ERR)':
                formal_stat_name =  'Absolute Track Error (nm)'
            elif COLUMN_group == 'ALTK_ERR':
                formal_stat_name =  'Along Track Bias (nm)'
            elif COLUMN_group == 'CRTK_ERR':
                formal_stat_name =  'Cross Track Bias (nm)'
            else:
                formal_stat_name = COLUMN_group
            summary_tcst_data_COLUMN = (
                summary_tcst_data_groupby_COLUMN.get_group(COLUMN_group)
            )
            summary_tcst_data_COLUMN_groupby_AMODEL = (
                summary_tcst_data_COLUMN.groupby(['AMODEL'])
            )
            nmodels = len(
                summary_tcst_data_COLUMN_groupby_AMODEL.groups.keys()
            )
            if nmodels != len(model_tmp_atcf_name_list):
                print("ERROR: Model(s) missing in "+summary_tcst_filename)
                continue
            stat_max = np.ma.masked_invalid(np.nan)
            fig, ax = plt.subplots(1,1,figsize=(x_figsize, y_figsize))
            ax.grid(True, color = 'grey', linestyle = '--')
            ax.axhline(0, color = 'black')
            ax.set_xlabel('Forecast Hour')
            ax.xaxis.set_label_coords(0.5, -0.15)
            if len(fhrs) > 15:
                ax.set_xticks(fhrs[::2])
                ax.set_xticks(fhrs, minor=True)
            else:
                ax.set_xticks(fhrs)
            ax.set_xlim([fhrs[0], fhrs[-1]])
            ax.set_ylabel(formal_stat_name)
            model_num = 0
            CI_bar_max_widths = np.append(np.diff(fhrs),
                                          fhrs[-1]-fhrs[-2])/1.5
            CI_bar_min_widths = np.append(np.diff(fhrs),
                                          fhrs[-1]-fhrs[-2])/nmodels
            CI_bar_intvl_widths = (
                (CI_bar_max_widths-CI_bar_min_widths)/nmodels
            )
            tcstat_file_AMODEL_list = (
                summary_tcst_data_COLUMN_groupby_AMODEL.groups.keys()
            )
            for AMODEL in model_tmp_atcf_name_list:
                AMODEL_idx = model_tmp_atcf_name_list.index(AMODEL)
                #AMODEL_plot_name = (model_plot_name_list[AMODEL_idx]+' '
                #                    +'('+model_atcf_name_list[AMODEL_idx]+')')
                # modified by Yan Jin
                AMODEL_plot_name = model_plot_name_list[AMODEL_idx]
                print("Plotting "+AMODEL_plot_name)
                model_num+=1
                model_plot_settings_dict = (
                    model_obs_plot_settings_dict['model'+str(model_num)]
                )
                fhrs_column_amodel_mean = np.full_like(fhrs, np.nan,
                                                       dtype=float)
                fhrs_column_amodel_total = np.full_like(fhrs, np.nan,
                                                        dtype=float)
                fhrs_column_amodel_mean_ncl = np.full_like(fhrs, np.nan,
                                                           dtype=float)
                fhrs_column_amodel_mean_ncu = np.full_like(fhrs, np.nan,
                                                           dtype=float)
                if AMODEL not in tcstat_file_AMODEL_list:
                    print("Data for "+AMODEL+" missing...setting to NaN")
                else:
                    summary_tcst_data_COLUMN_AMODEL = (
                        summary_tcst_data_COLUMN_groupby_AMODEL. \
                        get_group(AMODEL)
                    )
                    summary_tcst_data_COLUMN_AMODEL_LEAD = (
                        summary_tcst_data_COLUMN_AMODEL['LEAD'].values
                    )
                    summary_tcst_data_COLUMN_AMODEL_MEAN = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['MEAN'].values,
                        dtype=float
                    )
                    summary_tcst_data_COLUMN_AMODEL_TOTAL = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['TOTAL'].values,
                        dtype=float
                    )
                    summary_tcst_data_COLUMN_AMODEL_MEAN_NCL = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['MEAN_NCL'].values,
                        dtype=float
                    )
                    summary_tcst_data_COLUMN_AMODEL_MEAN_NCU = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['MEAN_NCU'].values,
                        dtype=float
                    )
                    summary_tcst_data_COLUMN_AMODEL_STDEV = np.asarray(
                        summary_tcst_data_COLUMN_AMODEL['STDEV'].values,
                        dtype=float
                    )
                    leads_list = []
                    for lead in summary_tcst_data_COLUMN_AMODEL_LEAD:
                        if lead[0] != '0':
                            leads_list.append(lead[0:3])
                        else:
                            leads_list.append(lead[1:3])
                    leads = np.asarray(leads_list, dtype=int)
                    for fhr in fhrs:
                        fhr_idx = np.where(fhr == fhrs)[0][0]
                        if fhr in leads:
                            matching_lead_idx = np.where(fhr == leads)[0][0]
                            fhrs_column_amodel_mean[fhr_idx] = (
                                summary_tcst_data_COLUMN_AMODEL_MEAN[
                                    matching_lead_idx
                                ]
                            )
                            fhrs_column_amodel_total[fhr_idx] = (
                                summary_tcst_data_COLUMN_AMODEL_TOTAL[
                                    matching_lead_idx
                                ]
                            )
                            fhrs_column_amodel_mean_ncl[fhr_idx] = (
                                summary_tcst_data_COLUMN_AMODEL_MEAN_NCL[
                                    matching_lead_idx
                                ]
                            )
                            fhrs_column_amodel_mean_ncu[fhr_idx] = (
                                summary_tcst_data_COLUMN_AMODEL_MEAN_NCU[
                                    matching_lead_idx
                                ]
                            )
                fhrs_column_amodel_mean = np.ma.masked_invalid(
                    fhrs_column_amodel_mean
                )
                fhrs_column_amodel_total = np.ma.masked_invalid(
                    fhrs_column_amodel_total
                )
                fhrs_column_amodel_mean_ncl = np.ma.masked_invalid(
                    fhrs_column_amodel_mean_ncl
                )
                fhrs_column_amodel_mean_ncu = np.ma.masked_invalid(
                    fhrs_column_amodel_mean_ncu
                )
                if model_num == 1:
                    all_amodel_total = [fhrs_column_amodel_total]
                else:
                    all_amodel_total = np.vstack(
                        (all_amodel_total, fhrs_column_amodel_total)
                    )
                all_amodel_total = np.ma.masked_invalid(all_amodel_total)
                count = (
                    len(fhrs_column_amodel_mean)
                     - np.ma.count_masked(fhrs_column_amodel_mean)
                )
                mfhrs =  np.ma.array(
                    fhrs, mask=np.ma.getmaskarray(fhrs_column_amodel_mean)
                )
                if count != 0:
                    ax.plot(mfhrs.compressed(),
                            fhrs_column_amodel_mean.compressed(),
                            color = model_plot_settings_dict['color'],
                            linestyle = model_plot_settings_dict['linestyle'],
                            linewidth = model_plot_settings_dict['linewidth'],
                            marker = model_plot_settings_dict['marker'],
                            markersize = model_plot_settings_dict['markersize'],
                            label=AMODEL_plot_name,
                            zorder=(nmodels-model_num-1)+4)
                    if fhrs_column_amodel_mean.max() > stat_max \
                            or np.ma.is_masked(stat_max):
                        stat_max = fhrs_column_amodel_mean.max()
                if plot_CI_bars == 'YES':
                    for fhr in fhrs:
                        fhr_idx = np.where(fhr == fhrs)[0][0]
                        ax.bar(fhrs[fhr_idx],
                               (fhrs_column_amodel_mean_ncu[fhr_idx]
                                - fhrs_column_amodel_mean_ncl[fhr_idx]),
                               bottom=fhrs_column_amodel_mean_ncl[fhr_idx],
                               color='None',
                               width=CI_bar_max_widths-(CI_bar_intvl_widths
                                                        *(model_num-1)),
                               edgecolor= model_plot_settings_dict['color'],
                               linewidth=0.5)
                        if fhrs_column_amodel_mean_ncu[fhr_idx] > stat_max \
                                or np.ma.is_masked(stat_max):
                            if not np.ma.is_masked(fhrs_column_amodel_mean_ncu[fhr_idx]):
                                stat_max = fhrs_column_amodel_mean_ncu[fhr_idx]
            # Adjust y axis limits and ticks
            preset_y_axis_tick_min = ax.get_yticks()[0]
            preset_y_axis_tick_max = ax.get_yticks()[-1]
            preset_y_axis_tick_inc = ax.get_yticks()[1] - ax.get_yticks()[0]
            
            # modified by Yan Jin
            #y_axis_min = math.floor(preset_y_axis_tick_min - 10)
            #y_axis_max = math.ceil(preset_y_axis_tick_max + 10)
            if plot_CI_bars == 'YES':
                y_axis_min = math.ceil(preset_y_axis_tick_max) * (-1.0) - 50.0
                y_axis_max = math.ceil(preset_y_axis_tick_max) + 50.0
            else:
                y_axis_min = math.floor(preset_y_axis_tick_min)
                y_axis_max = math.ceil(preset_y_axis_tick_max)
               
                #y_axis_min = -max(abs(math.floor(preset_y_axis_tick_min)), abs(math.ceil(preset_y_axis_tick_max)))  
            
            y_axis_tick_inc = preset_y_axis_tick_inc
            if np.ma.is_masked(stat_max):
                y_axis_max = preset_y_axis_tick_max
            else:
                y_axis_max = preset_y_axis_tick_max
                while y_axis_max < stat_max:
                    y_axis_max = y_axis_max + y_axis_tick_inc

            if COLUMN_group == 'ABS(TK_ERR)' or COLUMN_group == 'ABS(AMAX_WIND-BMAX_WIND)':
                y_axis_min = 0
            #y_axis_max = y_axis_max + 50.0
            ax.set_yticks(
                np.arange(y_axis_min,
                          y_axis_max+y_axis_tick_inc,
                          y_axis_tick_inc)
            )
            ax.set_ylim([y_axis_min, y_axis_max])
            # Check y axis limit
            if stat_max >= ax.get_ylim()[1]:
                while stat_max >= ax.get_ylim()[1]:
                    y_axis_max = y_axis_max + y_axis_tick_inc
                    y_axis_min = y_axis_max * (-1.0) - 50.0
                    if COLUMN_group == 'ABS(TK_ERR)' or COLUMN_group == 'ABS(AMAX_WIND-BMAX_WIND)':
                       y_axis_min = 0
                    y_axis_max = y_axis_max + 50.0
                    ax.set_yticks(
                        np.arange(y_axis_min,
                                  y_axis_max +  y_axis_tick_inc,
                                  y_axis_tick_inc)
                    )
                    ax.set_ylim([y_axis_min, y_axis_max])
            # Add legend, adjust if points in legend
            if len(ax.lines) != 0:
                legend = ax.legend(bbox_to_anchor=(legend_bbox_x,
                                                   legend_bbox_y),
                                   loc=legend_loc, ncol=legend_ncol,
                                   fontsize=legend_fontsize)
                plt.draw()
                legend_box = legend.get_window_extent() \
                    .transformed(ax.transData.inverted())
                if stat_max > legend_box.y1:
                    while stat_max > legend_box.y1:
                        y_axis_max = y_axis_max + y_axis_tick_inc
                        ax.set_yticks(
                        np.arange(y_axis_min,
                                  y_axis_max + y_axis_tick_inc,
                                  y_axis_tick_inc)
                        )
                        ax.set_ylim([y_axis_min, y_axis_max])
                        legend = ax.legend(
                            bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                            loc=legend_loc, ncol=legend_ncol,
                            fontsize=legend_fontsize
                        )
                        plt.draw()
                        legend_box = (
                            legend.get_window_extent() \
                            .transformed(ax.transData.inverted())
                        )
            # Add number of cases
            x_axis_ticks_fraction = np.linspace(0, 1,len(fhrs), endpoint=True)
            ax.annotate('# of\nCases',
                        xy=(case_num_label_x_loc, case_num_label_y_loc),
                        xycoords='axes fraction')
            if len(fhrs) > 15:
              fhrs_ncase_to_plot = fhrs[::2]
            else:
              fhrs_ncase_to_plot = fhrs
            for fhr in fhrs_ncase_to_plot:
                fhr_idx = np.where(fhr == fhrs)[0][0]
                if not np.ma.is_masked(all_amodel_total[:,fhr_idx]):
                    if np.all(all_amodel_total[:,fhr_idx]
                            == all_amodel_total[0,fhr_idx]):
                        num_cases = all_amodel_total[0,fhr_idx]
                        num_cases_str = str(int(num_cases))
                        ax.annotate(num_cases_str,
                                    xy=(x_axis_ticks_fraction[fhr_idx],
                                        case_num_tick_y_loc), size=12,
                                    xycoords='axes fraction', ha='center')
                    else:
                        print("Working with nonhomogeneous sample for fhr "
                              +str(fhr)+"...not printing number of cases")
            props = {
                'boxstyle': 'square',
                'pad': 0.35,
                'facecolor': 'white',
                'linestyle': 'solid',
                'linewidth': 1,
                'edgecolor': 'black'
            }
            x_axis_tick_inc = fhrs[1] - fhrs[0]
            # modified by Yan Jin       
            #if len(ax.lines) != 0:
            #    ax.text(legend_box.x1 + (x_axis_tick_inc * 0.75),
            #            ax.get_ylim()[1] - (0.15 * y_axis_tick_inc),
            #            'Note: statistical significance at the 95% '
            #            +'confidence level where confidence intervals '
            #            +'do not intersect',
            #            ha='left', va='top', fontsize=10,
            #            bbox=props, transform=ax.transData)
            # Build formal plot title
            full_title = formal_stat_name+'\n'
            #full_title = ""
            if basin == 'AL':
                formal_basin = 'Atlantic'
            elif basin == 'CP':
                formal_basin = 'Central Pacific'
            elif basin == 'EP':
                formal_basin = 'Eastern Pacific'
            elif basin == 'WP':
                 formal_basin = 'Western Pacific'
            if len(plot_info) == 2:
                full_title = full_title+formal_basin+' Mean\n'
            else:
                full_title = full_title + name.title().upper() + ' ' + '(' + basin + str(tc_num) + ' ' + year + ')'
            #full_title = (full_title+'Cycles: '+', '.join(init_hour_list)+', '
            #              +' Valid Hours: '+', '.join(valid_hour_list))
            ax.set_title(full_title)
            noaa_img = fig.figimage(noaa_logo_img_array,
                                    noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                                    zorder=1, alpha=noaa_logo_alpha)
            nws_img = fig.figimage(nws_logo_img_array,
                                   nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                                   zorder=1, alpha=nws_logo_alpha)
            #if img_quality in ['low', 'medium']:
            #    noaa_img.set_visible(False)
            #    nws_img.set_visible(False)
            # Build savefig name
            savefig_name = os.path.join(
                plotting_out_dir_imgs,
                COLUMN_group.replace('(', '').replace(')', '')
                +'_fhrmean_'+plot_info+'_'+model_type+'.png'
            )
            print("Saving image as "+savefig_name)
            plt.savefig(savefig_name)
            plt.close()
else:
    print("ERROR: "+summary_tcst_filename+" does not exist")
    sys.exit(1)
