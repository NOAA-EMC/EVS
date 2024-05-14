#!/usr/bin/env python3

###############################################################################
#
# Name:          roc_curve.py
# Contact(s):    Marcel Caron
# Developed:     Sep. 26, 2022 by Marcel Caron 
# Last Modified: Sep. 26, 2022 by Marcel Caron             
# Title:         Receiver Operator Characteristic (ROC) curve
# Abstract:      Plots METplus CTC output as a line plot, probability of
#                detection, which represents the y-axis, varying by false alarm 
#                rate, which represents the x-axis. Line colors and styles are 
#                unique for each model, and several models can be plotted at 
#                once.
#
###############################################################################

import os
import sys
import numpy as np
import pandas as pd
import logging
from functools import reduce
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from datetime import datetime, timedelta as td

SETTINGS_DIR=os.environ['USHevs']
sys.path.insert(0, os.path.abspath(SETTINGS_DIR))
SETTINGS_DIR = os.environ['USH_DIR']
sys.path.insert(0, os.path.abspath(SETTINGS_DIR))
from evs_wafs_atmos_plot_settings import Toggle, Templates, Presets, ModelSpecs, Reference
from evs_wafs_atmos_plot_plotter import Plotter
from evs_wafs_atmos_plot_prune_stat_files import prune_data
import evs_wafs_atmos_plot_util as plot_util
import evs_wafs_atmos_plot_df_preprocessing as df_preprocessing
from evs_wafs_atmos_plot_check_variables import *

# ================ GLOBALS AND CONSTANTS ================

plotter = Plotter(fig_size=(20., 14.))
plotter.set_up_plots()
toggle = Toggle()
templates = Templates()
presets = Presets()
model_colors = ModelSpecs()
reference = Reference()


# =================== FUNCTIONS =========================


def get_bias_label_position(bias_value, radius):
    x = np.sqrt(np.power(radius, 2)/(np.power(bias_value, 2)+1))
    y = np.sqrt(np.power(radius, 2) - np.power(x, 2))
    return (x, y)

def plot_roc_curve(df: pd.DataFrame, logger: logging.Logger, 
                      date_range: tuple, model_list: list, num: int = 0, 
                      level: str = '500', flead='all', thresh: list = ['<20'], 
                      metric1_name: str = 'SRATIO', metric2_name: str = 'POD', 
                      metric3_name: str = 'CSI', date_type: str = 'VALID', 
                      date_hours: list = [0,6,12,18], verif_type: str = 'pres', 
                      line_type: str = 'CTC', save_dir: str = '.', dpi: int = 100, 
                      confidence_intervals: bool = False, bs_nrep: int = 5000, 
                      bs_method: str = 'MATCHED_PAIRS', ci_lev: float = .95, 
                      bs_min_samp: int = 30, eval_period: str = 'TEST', 
                      display_averages: bool = True, save_header: str = '', 
                      plot_group: str = 'sfc_upper',
                      sample_equalization: bool = True,
                      regrid: str = 'g193', component: str = 'wafs',
                      fcst_var_names: list = ['ICESEV'], var_name: str = 'icesev'
                   ):

    logger.info("========================================")
    logger.info(f"Creating Plot {num} ...")

    if (str(metric1_name).upper() != 'FARATE' 
            or str(metric2_name).upper() != 'POD'):
        w1 = (f"The ROC curve may not plot correctly unless the"
              + f" order of metrics provided is \'FARATE\' and \'POD\'.")
        w2 = (f"The order provided is \'{metric1_name}\', and"
              + f" \'{metric2_name}\'.")
        w3 = "Continuing ..."
        logger.warning(w1)
        logger.warning(w2)
        logger.warning(w3)

    if df.empty:
        logger.warning(f"Empty Dataframe. Continuing onto next plot...")
        logger.info("========================================")
        return None

    fig, ax = plotter.get_plots(num)  
    variable_translator = reference.variable_translator
    domain_translator = reference.domain_translator
    model_settings = model_colors.model_settings

    # filter by level
    df = df[df['FCST_LEV'].astype(str).eq(str(level))]

    if df.empty:
        logger.warning(f"Empty Dataframe. Continuing onto next plot...")
        plt.close(num)
        logger.info("========================================")
        return None
    if str(line_type).upper() == 'CTC' and np.array(thresh).size == 0:
        logger.warning(f"Empty list of thresholds. Continuing onto next"
                       + f" plot...")
        logger.info("========================================")
        return None

    # filter by forecast lead times
    if isinstance(flead, list):
        if len(flead) <= 8:
            if len(flead) > 1:
                frange_phrase = 's '+', '.join([str(f) for f in flead])
            else:
                frange_phrase = ' '+', '.join([str(f) for f in flead])
            frange_save_phrase = '-'.join([str(f) for f in flead])
        else:
            frange_phrase = f's {flead[0]}'+u'\u2013'+f'{flead[-1]}'
            frange_save_phrase = f'{flead[0]}_TO_F{flead[-1]}'
        frange_string = f'Forecast Hour{frange_phrase}'
        frange_save_string = f'F{frange_save_phrase}'
        df = df[df['LEAD_HOURS'].isin(flead)]
    elif isinstance(flead, tuple):
        frange_string = (f'Forecast Hours {flead[0]:02d}'+u'\u2013'
                         + f'{flead[1]:02d}')
        frange_save_string = f'F{flead[0]:02d}-F{flead[1]:02d}'
        df = df[
            (df['LEAD_HOURS'] >= flead[0]) & (df['LEAD_HOURS'] <= flead[1])
        ]
    elif isinstance(flead, int):
        frange_string = f'Forecast Hour {flead:02d}'
        frange_save_string = f'F{flead:03d}'
        df = df[df['LEAD_HOURS'] == flead]
    else:
        e1 = f"Invalid forecast lead: \'{flead}\'"
        e2 = f"Please check settings for forecast leads."
        logger.error(e1)
        logger.error(e2)
        raise ValueError(e1+"\n"+e2)

    # Remove from date_hours the valid/init hours that don't exist in the 
    # dataframe
    date_hours = np.array(date_hours)[[
        str(x) in df[str(date_type).upper()].dt.hour.astype(str).tolist() 
        for x in date_hours
    ]]

    requested_thresh_symbol, requested_thresh_letter = list(
        zip(*[plot_util.format_thresh(t) for t in thresh])
    )
    symbol_found = False
    for opt in ['>=', '>', '==', '!=', '<=', '<']: 
        if any(opt in t for t in requested_thresh_symbol):
            if all(opt in t for t in requested_thresh_symbol):
                symbol_found = True
                opt_letter = requested_thresh_letter[0][:2]
                break
            else:
                e = ("Threshold operands do not match among all requested"
                    + f" thresholds.")
                logger.error(e)
                logger.error("Quitting ...")
                raise ValueError(e+"\nQuitting ...")
    if not symbol_found:
        e = "None of the requested thresholds contain a valid symbol."
        logger.error(e)
        logger.error("Quitting ...")
        raise ValueError(e+"\nQuitting ...")

    df_thresh_symbol, df_thresh_letter = list(
        zip(*[plot_util.format_thresh(t) for t in df['FCST_THRESH']])
    )
    df['FCST_THRESH_SYMBOL'] = df_thresh_symbol
    df['FCST_THRESH_VALUE'] = [str(item)[2:] for item in df_thresh_letter]
    requested_thresh_value = [
        str(item)[2:] for item in requested_thresh_letter
    ]
    df = df[df['FCST_THRESH_SYMBOL'].isin(requested_thresh_symbol)]

    thresholds_removed = (
        np.array(requested_thresh_symbol)[
            ~np.isin(requested_thresh_symbol, df['FCST_THRESH_SYMBOL'])
        ]
    )
    requested_thresh_symbol = (
        np.array(requested_thresh_symbol)[
            np.isin(requested_thresh_symbol, df['FCST_THRESH_SYMBOL'])
        ]
    )
    if thresholds_removed.size > 0:
        thresholds_removed_string = ', '.join(thresholds_removed)
        if len(thresholds_removed) > 1:
            warning_string = (f"{thresholds_removed_string} thresholds were"
                              + f" not found and will not be plotted.")
        else:
            warning_string = (f"{thresholds_removed_string} threshold was"
                              + f" not found and will not be plotted.")
        logger.warning(warning_string)
        logger.warning("Continuing ...")

    # If fcst_var_names have more than one variables, they will be plotted together.
    df0 = df.copy()
    model_list0 = model_list.copy()
    for fcst_var_name in fcst_var_names:
        df = df0[df0['FCST_VAR'].astype(str).eq(str(fcst_var_name))]
        # Remove from model_list the models that don't exist in the dataframe
        cols_to_keep = [
            str(model)
            in df['MODEL'].tolist() 
            for model in model_list0
        ]
        models_removed = [
            str(m)
            for (m, keep) in zip(model_list0, cols_to_keep) if not keep
        ]
        models_removed_string = ', '.join(models_removed)
        model_list = [
            str(m)
            for (m, keep) in zip(model_list0, cols_to_keep) if keep
        ]
        if not all(cols_to_keep):
            logger.warning(
                f"{models_removed_string} data were not found and will not be"
                + f" plotted."
            )
        if df.empty:
            logger.warning(f"Empty Dataframe. Continuing onto next plot...")
            plt.close(num)
            logger.info("========================================")
            return None
        group_by = ['MODEL','FCST_THRESH_VALUE']
        if sample_equalization:
            df, bool_success = plot_util.equalize_samples(logger, df, group_by)
            if not bool_success:
                sample_equalization = False
        df_groups = df.groupby(group_by)
        # Aggregate unit statistics before calculating metrics
        df_aggregated = df_groups.sum()
        # Remove data if they exist for some but not all models at some value of 
        # the indep. variable. Otherwise plot_util.calculate_stat will throw an 
        # error
        df_split = [df_aggregated.xs(str(model)) for model in model_list]
        df_reduced = reduce(
            lambda x,y: pd.merge(
                x, y, on='FCST_THRESH_VALUE', how='inner'
            ), 
            df_split
        )
        df_aggregated = df_aggregated[
            df_aggregated.index.get_level_values('FCST_THRESH_VALUE')
            .isin(df_reduced.index)
        ]
        if df_aggregated.empty:
            logger.warning(f"Empty Dataframe. Continuing onto next plot...")
            plt.close(num)
            logger.info("========================================")
            return None

        # Calculate desired metric
        metric_long_names = []
        for metric_name in [metric1_name, metric2_name]:
            stat_output = plot_util.calculate_stat(
                logger, df_aggregated, str(metric_name).lower()
            )
            df_aggregated[str(metric_name).upper()] = stat_output[0]
            metric_long_names.append(stat_output[2])
            if confidence_intervals:
                ci_output = df_groups.apply(
                    lambda x: plot_util.calculate_bootstrap_ci(
                        logger, bs_method, x, str(metric_name).lower(), bs_nrep,
                        ci_lev, bs_min_samp
                    )
                )
                if any(ci_output['STATUS'] == 1):
                    logger.warning(f"Failed attempt to compute bootstrap"
                                   + f" confidence intervals.  Sample size"
                                   + f" for one or more groups is too small."
                                   + f" Minimum sample size can be changed"
                                   + f" in settings.py.")
                    logger.warning(f"Confidence intervals will not be"
                                   + f" plotted.")
                    confidence_intervals = False
                    continue
                ci_output = ci_output.reset_index(level=2, drop=True)
                ci_output = (
                    ci_output
                    .reindex(df_aggregated.index)
                    .reindex(ci_output.index)
                )
                df_aggregated[str(metric_name).upper()+'_BLERR'] = ci_output[
                    'CI_LOWER'
                ].values
                df_aggregated[str(metric_name).upper()+'_BUERR'] = ci_output[
                    'CI_UPPER'
                ].values
        df_aggregated[str(metric1_name).upper()] = (
            df_aggregated[str(metric1_name).upper()]
        ).astype(float).tolist()
        df_aggregated[str(metric2_name).upper()] = (
            df_aggregated[str(metric2_name).upper()]
        ).astype(float).tolist()

        df_aggregated = df_aggregated[
            df_aggregated.index.isin(model_list, level='MODEL')
        ]
        pivot_metric1 = pd.pivot_table(
            df_aggregated, values=str(metric1_name).upper(), columns='MODEL', 
            index='FCST_THRESH_VALUE'
        )
        pivot_metric2 = pd.pivot_table(
            df_aggregated, values=str(metric2_name).upper(), columns='MODEL', 
            index='FCST_THRESH_VALUE'
        )
        pivot_metric1 = pivot_metric1.dropna() 
        pivot_metric2 = pivot_metric2.dropna() 
        all_thresh_idx = np.unique(
            np.concatenate([
                pivot_metric1.index, 
                pivot_metric2.index, 
            ])
        )
        all_model_col = np.unique(
            np.concatenate([
                pivot_metric1.columns,
                pivot_metric2.columns,
            ])
        )
        if confidence_intervals:
            pivot_ci_lower1 = pd.pivot_table(
                df_aggregated, values=str(metric1_name).upper()+'_BLERR',
                columns='MODEL', index='FCST_THRESH_VALUE'
            )
            pivot_ci_upper1 = pd.pivot_table(
                df_aggregated, values=str(metric1_name).upper()+'_BUERR',
                columns='MODEL', index='FCST_THRESH_VALUE'
            )
            pivot_ci_lower2 = pd.pivot_table(
                df_aggregated, values=str(metric2_name).upper()+'_BLERR',
                columns='MODEL', index='FCST_THRESH_VALUE'
            )
            pivot_ci_upper2 = pd.pivot_table(
                df_aggregated, values=str(metric2_name).upper()+'_BUERR',
                columns='MODEL', index='FCST_THRESH_VALUE'
            )
            all_ci_thresh_idx = np.unique(
                np.concatenate([
                    pivot_ci_lower1.index,
                    pivot_ci_upper1.index,
                    pivot_ci_lower2.index,
                    pivot_ci_upper2.index
                ])
            )
        
        for thresh_idx in all_thresh_idx:
            if np.any([
                    thresh_idx not in pivot_metric.index for pivot_metric 
                    in [pivot_metric1, pivot_metric2]]):
                pivot_metric1.drop(
                    labels=thresh_idx, inplace=True, errors='ignore'
                )
                pivot_metric2.drop(
                    labels=thresh_idx, inplace=True, errors='ignore'
                )
        
        if confidence_intervals:
            for ci_thresh_idx in all_ci_thresh_idx:
                if np.any([
                        ci_thresh_idx not in pivot_metric.index for pivot_metric
                        in [pivot_metric1, pivot_metric2]]):
                    pivot_ci_lower1.drop(
                        labels=ci_thresh_idx, inplace=True, errors='ignore'
                    )
                    pivot_ci_upper1.drop(
                        labels=ci_thresh_idx, inplace=True, errors='ignore'
                    )
                    pivot_ci_lower2.drop(
                        labels=ci_thresh_idx, inplace=True, errors='ignore'
                    )
                    pivot_ci_upper2.drop(
                        labels=ci_thresh_idx, inplace=True, errors='ignore'
                    )
        models_in_pivot_metric = []
        for model_col in all_model_col:
            if np.any([
                    model_col not in pivot_metric.columns for pivot_metric
                    in [pivot_metric1, pivot_metric2]]):
                pivot_metric1.drop(
                    columns=model_col, inplace=True, errors='ignore'
                )
                pivot_metric2.drop(
                    columns=model_col, inplace=True, errors='ignore'
                )
                if confidence_intervals:
                    pivot_ci_lower1.drop(
                        columns=model_col, inplace=True, errors='ignore'
                    )
                    pivot_ci_upper1.drop(
                        columns=model_col, inplace=True, errors='ignore'
                    )
                    pivot_ci_lower2.drop(
                        columns=model_col, inplace=True, errors='ignore'
                    )
                    pivot_ci_upper2.drop(
                        columns=model_col, inplace=True, errors='ignore'
                    )
            else:
                models_in_pivot_metric.append(model_col)
        cols_to_keep = [
            str(model)
            in models_in_pivot_metric 
            for model in model_list
        ]
        models_removed = [
            str(m)
            for (m, keep) in zip(model_list, cols_to_keep) if not keep
        ]
        models_removed_string = ', '.join(models_removed)
        model_list = [
            str(m)
            for (m, keep) in zip(model_list, cols_to_keep) if keep
        ]
        if not all(cols_to_keep):
            logger.warning(
                f"{models_removed_string} data were all NaNs and will not be"
                + f" plotted."
            )
        if pivot_metric1.empty or pivot_metric2.empty:
            print_varname = df['FCST_VAR'].tolist()[0]
            logger.warning(
                f"Could not find (and cannot plot) {metric1_name} and/or"
                + f" {metric2_name} stats for {print_varname} at any threshold. "
            )
            logger.warning(
                f"This may occur if no forecast or observed events were counted "
                + f"at any threshold for any model, so that all performance "
                + f"statistics are undefined. Continuing ..."
            )
            plt.close(num)
            logger.info("========================================")
            print(
                "Continuing due to missing data.  Check the log file for details."
            )
            return None

        models_renamed = []
        count_renamed = 1
        for requested_model in model_list:
            if requested_model in model_colors.model_alias:
                requested_model = (
                    model_colors.model_alias[requested_model]['settings_key']
                )
            if requested_model in model_settings:
                models_renamed.append(requested_model)
            else:
                models_renamed.append('model'+str(count_renamed))
                count_renamed+=1
        models_renamed = np.array(models_renamed)
        # Check that there are no repeated colors
        temp_colors = [
            model_colors.get_color_dict(name)['color'] for name in models_renamed
        ]
        colors_corrected = True
        loop_count=0
        while not colors_corrected and loop_count < 10:
            unique, counts = np.unique(temp_colors, return_counts=True)
            repeated_colors = [u for i, u in enumerate(unique) if counts[i] > 1]
            if repeated_colors:
                for c in repeated_colors:
                    models_sharing_colors = models_renamed[
                        np.array(temp_colors)==c
                    ]
                    if np.flatnonzero(np.core.defchararray.find(
                            models_sharing_colors, 'model'
                        )!=-1):
                        need_to_rename = models_sharing_colors[np.flatnonzero(
                            np.core.defchararray.find(
                                models_sharing_colors, 'model'
                            )!=-1
                        )[0]]
                    else:
                        continue
                    models_renamed[models_renamed==need_to_rename] = (
                        'model' + str(count_renamed)
                    )
                    count_renamed+=1
                temp_colors = [
                    model_colors.get_color_dict(name)['color'] 
                    for name in models_renamed
                ]
                loop_count+=1
            else:
                colors_corrected = True
        mod_setting_dicts = [
            model_colors.get_color_dict(name) for name in models_renamed
        ]

        # Plot data
        logger.info("Begin plotting ...")
        '''
        gray_colors = [
        '#ffffff',
        '#f5f5f5',
        '#ececec',
        '#dfdfdf',
        '#cbcbcb',
        '#b2b2b2',
        '#8e8e8e',
        '#6f6f6f',
        '#545454',
        '#3f3f3f',
        ]

        cmap = colors.ListedColormap(gray_colors)
        '''

        thresh_labels = pivot_metric1.index
        thresh_argsort = np.argsort(thresh_labels.astype(float))
        requested_thresh_argsort = np.argsort([
            float(item) for item in requested_thresh_value
        ])
        thresh_labels = [thresh_labels[i] for i in thresh_argsort]
        requested_thresh_labels = [
            requested_thresh_value[i] for i in requested_thresh_argsort
        ]
        thresh_markers = [
            ('o',12),('P',14),('^',14),('X',14),('s',12),('D',12),('v',14),
            ('p',14),('<',14),('d',14),(r'$\spadesuit$',14),('>',14),
            (r'$\clubsuit$',14)
        ]
        if len(thresh_labels)+len(model_list) > 12:
            e = (f"The plot legend may be cut off.  Consider reducing the number"
                 + f" of models or thresholds and rerunning the plotting job.")
            logger.warning(e)
            logger.warning("Continuing ...")
        if len(thresh_labels) > len(thresh_markers):
            e = (f"Too many thresholds were requested.  Only {len(thresh_markers)}"
                 + f" or fewer thresholds may be plotted.")
            logger.error(e)
            logger.error("Quitting ...")
            plt.close(num)
            logger.info("========================================")
            return None
        units = df['FCST_UNITS'].tolist()[0]
        if units in reference.unit_conversions:
            thresh_labels = [float(tlab) for tlab in thresh_labels]
            thresh_labels = reference.unit_conversions[units]['formula'](thresh_labels)
            thresh_diff_categories = np.array([
                [np.power(10., y)]
                for y in [-5,-4,-3,-2,-1,0,1,2,3,4,5]
            ]).flatten()
            precision_scale_indiv_mult = [
                thresh_diff_categories[item] 
                for item in np.digitize(thresh_labels, thresh_diff_categories)
            ]
            precision_scale_collective_mult = 100/min(precision_scale_indiv_mult)
            precision_scale = np.multiply(
                precision_scale_indiv_mult, precision_scale_collective_mult
            )
            thresh_labels = [
                f'{np.round(tlab)/precision_scale[t]}' 
                for t, tlab in enumerate(
                        np.multiply(thresh_labels, precision_scale)
                )
            ]
            units = reference.unit_conversions[units]['convert_to']
        if units == '-':
            units = ''
        # If a variable has a suffix, like mean, max, etc.
        var_name_suffix = ""
        if fcst_var_name.find(var_name) != -1:
            var_name_suffix = fcst_var_name[fcst_var_name.find(var_name)+len(var_name):]
        for m in range(len(mod_setting_dicts)):
            if model_list[m] in model_colors.model_alias:
                model_plot_name = (
                    model_colors.model_alias[model_list[m]]['plot_name']
                )
            else:
                model_plot_name = model_list[m]
            model_plot_name = model_plot_name + " " + var_name_suffix
            x_vals = [
                pivot_metric1[str(model_list[m])].values[i] 
                for i in thresh_argsort
            ]
            y_vals = [
                pivot_metric2[str(model_list[m])].values[i] 
                for i in thresh_argsort
            ]
            #mosaic_vals = pivot_metric3[str(model_list[m])].values
            x_mean = np.nanmean(x_vals)
            y_mean = np.nanmean(y_vals)
            #mosaic_mean = np.nanmean(mosaic_vals)
            if confidence_intervals:
                x_vals_ci_lower = pivot_ci_lower1[
                    str(model_list[m])
                ].values
                x_vals_ci_upper = pivot_ci_upper1[
                    str(model_list[m])
                ].values
                y_vals_ci_lower = pivot_ci_lower2[
                    str(model_list[m])
                ].values
                y_vals_ci_upper = pivot_ci_upper2[
                    str(model_list[m])
                ].values
            if display_averages:
                metric_mean_fmt_string = (f'{model_plot_name} ({x_mean:.2f},'
                                          + f' {y_mean:.2f})')
            else:
                metric_mean_fmt_string = f'{model_plot_name}'
            if var_name_suffix == "max":
                plt_marker = '^'
                plt_ls = 'dashed'
            else:
                plt_marker = mod_setting_dicts[m]['marker']
                plt_ls = mod_setting_dicts[m]['linestyle']
            plt.plot(
                np.concatenate(([1.],x_vals,[0.])), 
                np.concatenate(([1.],y_vals,[0.])), 
                marker=plt_marker, c=mod_setting_dicts[m]['color'], 
                mew=2., mec='white', figure=fig, ms=mod_setting_dicts[m]['markersize'], 
                ls=plt_ls,
                lw=mod_setting_dicts[m]['linewidth'],
                label=metric_mean_fmt_string
            )
            '''
            for i, item in enumerate(x_vals):
                plt.scatter(
                    x_vals[i], y_vals[i], marker=thresh_markers[i][0], 
                    c=mod_setting_dicts[m]['color'], linewidths=2., 
                    edgecolors='white', figure=fig, s=thresh_markers[i][1]**2,
                    zorder=10
                )
            '''
            if confidence_intervals:
                pc = plotter.get_error_boxes(
                    x_vals, y_vals, [x_vals_ci_lower, x_vals_ci_upper],
                    [y_vals_ci_lower, y_vals_ci_upper], 
                    ec=mod_setting_dicts[m]['color'],
                    ls=mod_setting_dicts[m]['linestyle'], lw=2.
                )
                ax.add_collection(pc)

    # Draw a diagonal line
    grid_ticks = np.arange(0.001, 1.001, 0.001)
    fr_g, pod_g = np.meshgrid(grid_ticks, grid_ticks)
    random_contour = plt.contour(
        fr_g, pod_g, pod_g / fr_g, [1.],
        colors='gray', linestyles='dashed'
    )

    # Configure axis ticks
    xticks_min = 0.
    xticks_max = 1.
    incr = .1
    xticks = [
        x_val for x_val in np.arange(xticks_min, xticks_max+incr, incr)
    ] 
    xtick_labels = [f'{xtick:.1f}' for xtick in xticks]
    x_buffer_size = .015
    ax.set_xlim(
        xticks_min-incr*x_buffer_size, xticks_max+incr*x_buffer_size
    )
    yticks_min = 0.
    yticks_max = 1.
    yticks = [
        y_val for y_val in np.arange(yticks_min, yticks_max+incr, incr)
    ] 
    ytick_labels = [f'{ytick:.1f}' for ytick in yticks]
    y_buffer_size = .015
    ax.set_ylim(
        yticks_min-incr*y_buffer_size, yticks_max+incr*y_buffer_size
    )
    #var_long_name_key = df['FCST_VAR'].tolist()[0]
    var_long_name_key = var_name
    if str(var_long_name_key).upper() == 'HGT':
        if str(df['OBS_VAR'].tolist()[0]).upper() == 'CEILING':
            var_long_name_key = 'HGTCLDCEIL'
    var_long_name = variable_translator[var_long_name_key]
    metrics_using_var_units = [
        'BCRMSE','RMSE','BIAS','ME','FBAR','OBAR','MAE','FBAR_OBAR',
        'SPEED_ERR','DIR_ERR','RMSVE','VDIFF_SPEED','VDIF_DIR',
        'FBAR_OBAR_SPEED','FBAR_OBAR_DIR','FBAR_SPEED','FBAR_DIR'
    ]
    ax.set_ylabel(f'{metric_long_names[1]}')
    ax.set_xlabel(f'{metric_long_names[0]}') 
    ax.set_xticklabels(xtick_labels)
    ax.set_yticklabels(ytick_labels)
    ax.set_yticks(yticks)
    ax.set_xticks(xticks)
    ax.tick_params(
        labelleft=True, labelright=False, labelbottom=True, labeltop=False
    )
    ax.tick_params(
        left=False, labelleft=False, labelright=False, labelbottom=False, 
        labeltop=False, which='minor', pad=15
    )

    ax.legend(
        loc='upper center', fontsize=15, framealpha=1, 
        bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=True, numpoints=1, 
        borderpad=.8, labelspacing=2., columnspacing=3., handlelength=3., 
        handletextpad=.4, borderaxespad=.5)
    '''
    ax.grid(
        visible=True, which='major', axis='both', alpha=.35, linestyle='--', 
        linewidth=.5, c='black', zorder=0
    )
    '''
    fig.subplots_adjust(bottom=.2, right=.77, left=.23, wspace=0, hspace=0)
    '''
    cax = fig.add_axes([.775, .2, .01, .725])
    cbar_ticks = [0.,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.]
    cb = plt.colorbar(
        csi_contour, orientation='vertical', cax=cax, ticks=cbar_ticks,
        spacing='uniform', drawedges=True
    )
    cb.dividers.set_color('black')
    cb.dividers.set_linewidth(2)
    cb.ax.tick_params(
        labelsize=8, labelright=True, labelleft=False, right=False
    )
    cb.ax.set_yticklabels(
        [f'{cbar_tick:.1f}' for cbar_tick in cbar_ticks], 
        fontdict={'fontsize': 12}
    )
    cax.hlines([0, 1], 0, 1, colors='black', linewidth=4)
    cb.set_label(f'{metric_long_names[2]}')
    '''

    # Title
    domain = df['VX_MASK'].tolist()[0]
    #var_savename = df['FCST_VAR'].tolist()[0]
    var_savename = var_name.lower()
    if domain in list(domain_translator.keys()):
        domain_string = domain_translator[domain]
    else:
        domain_string = domain
    '''
    date_hours_string = plot_util.get_name_for_listed_items(
        [f'{date_hour:02d}' for date_hour in date_hours],
        ', ', '', 'Z', '', ''
    )
    '''
    date_hours_string = ""
    '''
    date_hours_string = ' '.join([
        f'{date_hour:02d}Z,' for date_hour in date_hours
    ])
    '''
    date_start_string = date_range[0].strftime('%d %b %Y')
    date_end_string = date_range[1].strftime('%d %b %Y')
    if str(verif_type).lower() in ['pres', 'upper_air'] or 'P' in str(level):
        level_num = float(level.replace('P', ''))
        level_string = f'{level_num} hPa '
        level_num = int(level_num)
        level_savename = f'p{level_num}'
    elif (str(verif_type).lower() 
            in ['sfc', 'conus_sfc', 'polar_sfc', 'mrms']):
        if 'Z' in str(level):
            if str(level).upper() == 'Z0':
                level_string = 'Surface '
                level_savename = 'SFC_'
            else:
                level_num = level.replace('Z', '')
                if var_savename in ['TSOIL', 'SOILW']:
                    level_string = f'{level_num}-cm '
                    level_savename = f'{level_num}CM_'
                else:
                    level_string = f'{level_num}-m '
                    level_savename = f'{level_num}M_'
        elif 'L' in str(level) or 'A' in str(level):
            level_string = ''
            level_savename = ''
        else:
            level_string = f'{level} '
            level_savename = f'{level}_'
    elif str(verif_type).lower() in ['ccpa']:
        if 'A' in str(level):
            level_num = level.replace('A', '')
            level_string = f'{level_num}-hour '
            level_savename = f'{level_num}H_'
        else:
            level_string = f''
            level_savename = f''
    else:
        level_string = f'{level} '
        level_savename = f'{level}_'
    thresholds_phrase = ', '.join([
        f'{opt}{thresh_label}' for thresh_label in thresh_labels
    ])
    thresholds_save_phrase = ''.join([
        f'{opt_letter}{thresh_label}' 
        for thresh_label in requested_thresh_labels
    ])
    thresholds_string = f'Forecast Thresholds {thresholds_phrase}'
    title1 = f'ROC Curve'
    if not units:
        title2 = (f'{level_string}{var_long_name} (-), {domain_string}')
    else:
        title2 = (f'{level_string}{var_long_name} ({units}), {domain_string}')
    title3 = (f'{str(date_type).capitalize()} {date_hours_string}'
              + f'{date_start_string} to {date_end_string}, {frange_string}')
    title_center = '\n'.join([title1, title2, title3])
    title_pad = 13
    ax.set_title(title_center, loc=plotter.title_loc, pad=title_pad)
    logger.info("... Plotting complete.")

    # Adding logo
    if logo_dir:
        left_logo_arr = mpimg.imread(os.path.join(logo_dir, 'noaa.png'))
        left_image_box = OffsetImage(left_logo_arr, zoom=zoom_logo_left, alpha=logo_alpha)
        ab_left = AnnotationBbox(
            left_image_box, xy=(-0.05,0.975), xycoords='axes fraction',
            xybox=(0, 20), boxcoords='offset points', frameon = False,
            box_alignment=(0,0)
        )
        ax.add_artist(ab_left)

        right_logo_arr = mpimg.imread(os.path.join(logo_dir, 'nws.png'))
        right_image_box = OffsetImage(right_logo_arr, zoom=zoom_logo_right, alpha=logo_alpha)
        ab_right = AnnotationBbox(
            right_image_box, xy=(1.05,0.975), xycoords='axes fraction',
            xybox=(0, 20), boxcoords='offset points', frameon = False,
            box_alignment=(1,0)
        )
        ax.add_artist(ab_right)

    # Saving
    if len(date_hours) <= 8: 
        date_hours_savename = '_'.join([
            f'{date_hour:02d}Z' for date_hour in date_hours
        ])
    else:
        date_hours_savename = '-'.join([
            f'{date_hour:02d}Z' 
            for date_hour in [date_hours[0], date_hours[-1]]
        ])
    date_start_savename = date_range[0].strftime('%Y%m%d')
    date_end_savename = date_range[1].strftime('%Y%m%d')
    if str(eval_period).upper() == 'TEST':
        time_period_savename = f'{date_start_savename}-{date_end_savename}'
    else:
        time_period_savename = f'{str(eval_period).lower()}'
    save_name = (f'evs.{str(component)}.ctc.'
                 + f'{str(var_savename).lower()}_'
                 + f'{str(level_savename).lower()}.'
                 + f'{time_period_savename}.'
                 + f'roc_{str(frange_save_string).lower()}.')
    if str(domain).lower() == str(regrid).lower():
        save_name = save_name + f'{str(regrid)}'
    else:
        save_name = save_name + f'{str(regrid)}_{str(domain).lower()}'
    if save_header:
        save_name = f'{save_header}_'+save_name
    save_subdir = save_dir
    if not os.path.isdir(save_subdir):
        os.makedirs(save_subdir, exist_ok=True)
    save_path = os.path.join(save_subdir, save_name+'.png')
    fig.savefig(save_path, dpi=dpi)
    logger.info(u"\u2713"+f" plot saved successfully as {save_path}")
    plt.close(num)
    logger.info('========================================')


def main():

    # Logging
    log_metplus_dir = '/'
    for subdir in LOG_METPLUS.split('/')[:-1]:
        log_metplus_dir = os.path.join(log_metplus_dir, subdir)
    if not os.path.isdir(log_metplus_dir):
        os.makedirs(log_metplus_dir, exist_ok=True)
    logger = logging.getLogger(LOG_METPLUS)
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
        + '%(message)s',
        '%m/%d %H:%M:%S'
    )
    file_handler = logging.FileHandler(LOG_METPLUS, mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger_info = f"Log file: {LOG_METPLUS}"
    print(logger_info)
    logger.info(logger_info)

    if str(EVAL_PERIOD).upper() == 'TEST':
        valid_beg = VALID_BEG
        valid_end = VALID_END
        init_beg = INIT_BEG
        init_end = INIT_END
    else:
        if 'VALID_BEG' in globals():
            valid_beg = VALID_BEG
        else:
            valid_beg = presets.date_presets[EVAL_PERIOD]['valid_beg']
        if 'VALID_END' in globals():
            valid_end = VALID_END
        else:
            valid_end = presets.date_presets[EVAL_PERIOD]['valid_end']
        init_beg = presets.date_presets[EVAL_PERIOD]['init_beg']
        init_end = presets.date_presets[EVAL_PERIOD]['init_end']
    if str(DATE_TYPE).upper() == 'VALID':
        date_beg = valid_beg
        date_end = valid_end
        date_hours = VALID_HOURS
        date_type_string = DATE_TYPE
    elif str(DATE_TYPE).upper() == 'INIT':
        date_beg = init_beg
        date_end = init_end
        date_hours = INIT_HOURS
        date_type_string = 'Initialization'
    else:
        e = (f"Invalid DATE_TYPE: {str(date_type).upper()}. Valid values are"
             + f" VALID or INIT")
        logger.error(e)
        raise ValueError(e)

    logger.debug('========================================')
    logger.debug("Config file settings")
    logger.debug(f"LOG_LEVEL: {LOG_LEVEL}")
    logger.debug(f"MET_VERSION: {MET_VERSION}")
    logger.debug(f"URL_HEADER: {URL_HEADER if URL_HEADER else 'No header'}")
    logger.debug(f"OUTPUT_BASE_DIR: {OUTPUT_BASE_DIR}")
    logger.debug(f"STATS_DIR: {STATS_DIR}")
    logger.debug(f"PRUNE_DIR: {PRUNE_DIR}")
    logger.debug(f"SAVE_DIR: {SAVE_DIR}")
    logger.debug(f"VERIF_CASETYPE: {VERIF_CASETYPE}")
    logger.debug(f"MODELS: {MODELS}")
    logger.debug(f"VARIABLES: {VARIABLES}")
    logger.debug(f"DOMAINS: {DOMAINS}")
    logger.debug(f"INTERP: {INTERP}")
    logger.debug(f"DATE_TYPE: {DATE_TYPE}")
    logger.debug(
        f"EVAL_PERIOD: {EVAL_PERIOD}"
    )
    logger.debug(
        f"{DATE_TYPE}_BEG: {date_beg}"
    )
    logger.debug(
        f"{DATE_TYPE}_END: {date_end}"
    )
    logger.debug(f"VALID_HOURS: {VALID_HOURS}")
    logger.debug(f"INIT_HOURS: {INIT_HOURS}")
    logger.debug(f"FCST_LEADS: {FLEADS}")
    logger.debug(f"FCST_LEVELS: {FCST_LEVELS}")
    logger.debug(f"OBS_LEVELS: {OBS_LEVELS}")
    logger.debug(
        f"FCST_THRESH: {FCST_THRESH if FCST_THRESH else 'No thresholds'}"
    )
    logger.debug(
        f"OBS_THRESH: {OBS_THRESH if OBS_THRESH else 'No thresholds'}"
    )
    logger.debug(f"LINE_TYPE: {LINE_TYPE}")
    logger.debug(f"METRICS: {METRICS}")
    logger.debug(f"CONFIDENCE_INTERVALS: {CONFIDENCE_INTERVALS}")

    logger.debug('----------------------------------------')
    logger.debug(f"Advanced settings (configurable in {SETTINGS_DIR}/settings.py)")
    logger.debug(f"Y_MIN_LIMIT: {Y_MIN_LIMIT}")
    logger.debug(f"Y_MAX_LIMIT: {Y_MAX_LIMIT}")
    logger.debug(f"Y_LIM_LOCK: {Y_LIM_LOCK}")
    logger.debug(f"X_MIN_LIMIT: Ignored for ROC curves")
    logger.debug(f"X_MAX_LIMIT: Ignored for ROC curves")
    logger.debug(f"X_LIM_LOCK: Ignored for ROC curves")
    logger.debug(f"Display averages? {'yes' if display_averages else 'no'}")
    logger.debug(
        f"Clear prune directories? {'yes' if clear_prune_dir else 'no'}"
    )
    if CONFIDENCE_INTERVALS:
        logger.debug(f"Confidence Level: {int(ci_lev*100)}%")
        logger.debug(f"Bootstrap method: {bs_method}")
        logger.debug(f"Bootstrap repetitions: {bs_nrep}")
        logger.debug(
            f"Minimum sample size for confidence intervals: {bs_min_samp}"
        )
    logger.debug('========================================')

    metrics = METRICS
    date_range = (
        datetime.strptime(date_beg, '%Y%m%d'), 
        datetime.strptime(date_end, '%Y%m%d')+td(days=1)-td(milliseconds=1)
    )
    fcst_thresh_symbol, fcst_thresh_letter = list(
        zip(*[plot_util.format_thresh(thresh) for thresh in FCST_THRESH])
    )
    obs_thresh_symbol, obs_thresh_letter = list(
        zip(*[plot_util.format_thresh(thresh) for thresh in OBS_THRESH])
    )
    num=0
    e = ''
    if str(VERIF_CASETYPE).lower() not in list(reference.case_type.keys()):
        e = (f"The requested verification case/type combination is not valid:"
             + f" {VERIF_CASETYPE}")
    elif str(LINE_TYPE).upper() not in list(
            reference.case_type[str(VERIF_CASETYPE).lower()].keys()):
        e = (f"The requested line_type is not valid for {VERIF_CASETYPE}:"
             + f" {LINE_TYPE}")
    else:
        case_specs = (
            reference.case_type
            [str(VERIF_CASETYPE).lower()]
            [str(LINE_TYPE).upper()]
        )
    if e:
        logger.error(e)
        logger.error("Quitting ...")
        raise ValueError(e+"\nQuitting ...")
    if (str(INTERP).upper()
           not in case_specs['interp'].replace(' ','').split(',')):
        e = (f"The requested interp method is not valid for the"
             + f" requested case type ({VERIF_CASETYPE}) and"
             + f" line_type ({LINE_TYPE}): {INTERP}")
        logger.error(e)
        logger.error("Quitting ...")
        raise ValueError(e+"\nQuitting ...")
    for metric in metrics:
        if (str(metric).lower()
                not in case_specs['plot_stats_list']
                .replace(' ','').split(',')):
            e = (f"The requested metric is not valid for the"
                 + f" requested case type ({VERIF_CASETYPE}) and"
                 + f" line_type ({LINE_TYPE}): {metric}")
            logger.error(e)
            logger.error("Quitting ...")
            raise ValueError(e+"\nQuitting ...")
    for requested_var in VARIABLES:
        if requested_var in list(case_specs['var_dict'].keys()):
            var_specs = case_specs['var_dict'][requested_var]
        else:
            e = (f"The requested variable is not valid for the requested case"
                 + f" type ({VERIF_CASETYPE}) and line_type ({LINE_TYPE}):"
                 + f" {requested_var}")
            logger.warning(e)
            logger.warning("Continuing ...")
            continue
        fcst_var_names = var_specs['fcst_var_names']
        obs_var_names = var_specs['obs_var_names']
        symbol_keep = []
        letter_keep = []
        for fcst_thresh, obs_thresh in list(
                zip(*[fcst_thresh_symbol, obs_thresh_symbol])):
            if (fcst_thresh in var_specs['fcst_var_thresholds']
                    and obs_thresh in var_specs['obs_var_thresholds']):
                symbol_keep.append(True)
            else:
                symbol_keep.append(False)
        for fcst_thresh, obs_thresh in list(
                zip(*[fcst_thresh_letter, obs_thresh_letter])):
            if (fcst_thresh in var_specs['fcst_var_thresholds']
                    and obs_thresh in var_specs['obs_var_thresholds']):
                letter_keep.append(True)
            else:
                letter_keep.append(False)
        keep = np.add(letter_keep, symbol_keep)
        dropped_items = np.array(FCST_THRESH)[~keep].tolist()
        fcst_thresh = np.array(FCST_THRESH)[keep].tolist()
        obs_thresh = np.array(OBS_THRESH)[keep].tolist()
        if dropped_items:
            dropped_items_string = ', '.join(dropped_items)
            e = (f"The requested thresholds are not valid for the requested"
                 + f" case type ({VERIF_CASETYPE}) and line_type"
                 + f" ({LINE_TYPE}): {dropped_items_string}")
            logger.warning(e)
            logger.warning("Continuing ...")
        plot_group = var_specs['plot_group']
        for l, fcst_level in enumerate(FCST_LEVELS):
            if len(FCST_LEVELS) != len(OBS_LEVELS):
                e = ("FCST_LEVELS and OBS_LEVELS must be lists of the same"
                     + f" size")
                logger.error(e)
                logger.error("Quitting ...")
                raise ValueError(e+"\nQuitting ...")
            if (FCST_LEVELS[l] not in var_specs['fcst_var_levels'] 
                    or OBS_LEVELS[l] not in var_specs['obs_var_levels']):
                e = (f"The requested variable/level combination is not valid:"
                     + f" {requested_var}/{level}")
                logger.warning(e)
                logger.warning("Continuing ...")
                continue
            for flead in FLEADS:
                for domain in DOMAINS:
                    if str(domain) not in case_specs['vx_mask_list']:
                        e = (f"The requested domain is not valid for the"
                             + f" requested case type ({VERIF_CASETYPE}) and"
                             + f" line_type ({LINE_TYPE}): {domain}")
                        logger.warning(e)
                        logger.warning("Continuing ...")
                        continue
                    df = df_preprocessing.get_preprocessed_data(
                        logger, STATS_DIR, PRUNE_DIR, OUTPUT_BASE_TEMPLATE, VERIF_CASE, 
                        VERIF_TYPE, LINE_TYPE, DATE_TYPE, date_range, EVAL_PERIOD, 
                        date_hours, [flead], requested_var, fcst_var_names, 
                        obs_var_names, MODELS, domain, INTERP, MET_VERSION, 
                        clear_prune_dir
                    )
                    if df is None:
                        continue
                    plot_roc_curve(
                        df, logger, date_range, MODELS, num=num, 
                        flead=flead, level=fcst_level, thresh=fcst_thresh, 
                        metric1_name=metrics[0], metric2_name=metrics[1],
                        date_type=DATE_TYPE,  verif_type=VERIF_TYPE, 
                        line_type=LINE_TYPE, date_hours=date_hours, 
                        save_dir=SAVE_DIR, eval_period=EVAL_PERIOD, 
                        display_averages=display_averages, save_header=URL_HEADER,
                        plot_group=plot_group, 
                        confidence_intervals=CONFIDENCE_INTERVALS, 
                        bs_nrep=bs_nrep, bs_method=bs_method, ci_lev=ci_lev, 
                        bs_min_samp=bs_min_samp,
                        sample_equalization=sample_equalization,
                        regrid=REGRID, component=COMPONENT,
                        fcst_var_names=fcst_var_names, var_name=requested_var
                    )
                    num+=1

# ============ START USER CONFIGURATIONS ================

if __name__ == "__main__":
    print("\n=================== CHECKING CONFIG VARIABLES =====================\n")
    LOG_METPLUS = check_LOG_METPLUS(os.environ['LOG_METPLUS'])
    LOG_LEVEL = check_LOG_LEVEL(os.environ['LOG_LEVEL'])
    MET_VERSION = check_MET_VERSION(os.environ['MET_VERSION'])
    URL_HEADER = check_URL_HEADER(os.environ['URL_HEADER'])
    VERIF_CASE = check_VERIF_CASE(os.environ['VERIF_CASE'])
    VERIF_TYPE = check_VERIF_TYPE(os.environ['VERIF_TYPE'])
    OUTPUT_BASE_DIR = check_OUTPUT_BASE_DIR(os.environ['OUTPUT_BASE_DIR'])
    STATS_DIR = OUTPUT_BASE_DIR
    PRUNE_DIR = check_PRUNE_DIR(os.environ['PRUNE_DIR'])
    SAVE_DIR = check_SAVE_DIR(os.environ['SAVE_DIR'])
    DATE_TYPE = check_DATE_TYPE(os.environ['DATE_TYPE'])
    LINE_TYPE = check_LINE_TYPE(os.environ['LINE_TYPE'])
    INTERP = check_INTERP(os.environ['INTERP'])
    MODELS = check_MODEL(os.environ['MODEL']).replace(' ','').split(',')
    DOMAINS = check_VX_MASK_LIST(os.environ['VX_MASK_LIST']).replace(' ','').split(',')

    # valid hour (each plot will use all available valid_hours listed below)
    VALID_HOURS = check_FCST_VALID_HOUR(os.environ['FCST_VALID_HOUR'], DATE_TYPE).replace(' ','').split(',')
    INIT_HOURS = check_FCST_INIT_HOUR(os.environ['FCST_INIT_HOUR'], DATE_TYPE).replace(' ','').split(',')

    # time period to cover (inclusive)
    EVAL_PERIOD = check_EVAL_PERIOD(os.environ['EVAL_PERIOD'])
    VALID_BEG = check_VALID_BEG(os.environ['VALID_BEG'], DATE_TYPE, EVAL_PERIOD)
    VALID_END = check_VALID_END(os.environ['VALID_END'], DATE_TYPE, EVAL_PERIOD)
    INIT_BEG = check_INIT_BEG(os.environ['INIT_BEG'], DATE_TYPE, EVAL_PERIOD)
    INIT_END = check_INIT_END(os.environ['INIT_END'], DATE_TYPE, EVAL_PERIOD)

    # list of variables
    # Options: {'TMP','HGT','CAPE','RH','DPT','UGRD','VGRD','UGRD_VGRD','TCDC',
    #           'VIS'}
    VARIABLES = check_var_name(os.environ['var_name']).replace(' ','').split(',')

    # list of lead hours
    # Options: {list of lead hours; string, 'all'; tuple, start/stop flead; 
    #           string, single flead}
    FLEADS = check_FCST_LEAD(os.environ['FCST_LEAD']).replace(' ','').split(',')

    # list of levels
    FCST_LEVELS = check_FCST_LEVEL(os.environ['FCST_LEVEL']).replace(' ','').split(',')
    OBS_LEVELS = check_OBS_LEVEL(os.environ['OBS_LEVEL']).replace(' ','').split(',')

    FCST_THRESH = check_FCST_THRESH(os.environ['FCST_THRESH'], LINE_TYPE)
    OBS_THRESH = check_OBS_THRESH(os.environ['OBS_THRESH'], FCST_THRESH, LINE_TYPE).replace(' ','').split(',')
    FCST_THRESH = FCST_THRESH.replace(' ','').split(',')
    
    # requires two metrics to plot
    METRICS = check_STATS(os.environ['STATS']).replace(' ','').split(',')[:3]

    #Extra variables to name the images
    REGRID=os.environ['REGRID'].replace(' ','').lower()
    COMPONENT=os.environ['COMPONENT'].replace(' ','').lower()

    # set the lowest possible lower (and highest possible upper) axis limits. 
    # E.g.: If Y_LIM_LOCK == True, use Y_MIN_LIMIT as the definitive lower 
    # limit (ditto with Y_MAX_LIMIT)
    # If Y_LIM_LOCK == False, then allow lower and upper limits to adjust to 
    # data as long as limits don't overcome Y_MIN_LIMIT or Y_MAX_LIMIT 
    Y_MIN_LIMIT = toggle.plot_settings['y_min_limit']
    Y_MAX_LIMIT = toggle.plot_settings['y_max_limit']
    Y_LIM_LOCK = toggle.plot_settings['y_lim_lock']


    # Still need to configure CIs (doesn't work yet)
    CONFIDENCE_INTERVALS = check_CONFIDENCE_INTERVALS(os.environ['CONFIDENCE_INTERVALS']).replace(' ','')
    bs_nrep = toggle.plot_settings['bs_nrep']
    bs_method = toggle.plot_settings['bs_method']
    ci_lev = toggle.plot_settings['ci_lev']
    bs_min_samp = toggle.plot_settings['bs_min_samp']

    # At each value of the independent variable, whether or not to remove
    # samples used to aggregate each statistic if the samples are not shared
    # by all models.  Required to display sample sizes
    sample_equalization = toggle.plot_settings['sample_equalization']

    # Whether or not to display average values beside legend labels
    display_averages = toggle.plot_settings['display_averages']

    # Whether or not to clear the intermediate directory that stores pruned data
    clear_prune_dir = toggle.plot_settings['clear_prune_directory']

    # Information about logos
    logo_dir = check_LOGO_DIR(os.environ['LOGO_DIR'])
    zoom_logo_left = toggle.plot_settings['zoom_logo_left']
    zoom_logo_right = toggle.plot_settings['zoom_logo_right']
    logo_alpha = toggle.plot_settings['logo_alpha']

    OUTPUT_BASE_TEMPLATE = templates.output_base_template

    print("\n===================================================================\n")
    # ============= END USER CONFIGURATIONS =================

    LOG_METPLUS = str(LOG_METPLUS)
    LOG_LEVEL = str(LOG_LEVEL)
    MET_VERSION = float(MET_VERSION)
    VALID_HOURS = [
        int(valid_hour) if valid_hour else None for valid_hour in VALID_HOURS
    ]
    INIT_HOURS = [
        int(init_hour) if init_hour else None for init_hour in INIT_HOURS
    ]
    FLEADS = [int(flead) for flead in FLEADS]
    VERIF_CASETYPE = str(VERIF_CASE).lower() + '_' + str(VERIF_TYPE).lower()
    FCST_LEVELS = [str(level) for level in FCST_LEVELS]
    OBS_LEVELS = [str(level) for level in OBS_LEVELS]
    CONFIDENCE_INTERVALS = str(CONFIDENCE_INTERVALS).lower() in [
        'true', '1', 't', 'y', 'yes'
    ]
    # Modify the global variable presets, add "LAST[XX]DAYS" to the dictionary.
    presets = Presets(EVAL_PERIOD)
    main()
