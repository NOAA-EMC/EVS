#! /usr/bin/env python3

###############################################################################
#
# Name:          stat_by_level.py
# Contact(s):    Marcel Caron
# Developed:     Oct. 14, 2021 by Marcel Caron 
# Last Modified: Nov. 02, 2022 by Marcel Caron             
# Title:         Line plot of pressure level as a function of 
#                verification metric
# Abstract:      Plots METplus output (e.g., BCRMSE) as a line plot, 
#                stratified by pressure level, which represents the y-axis. 
#                Line colors and styles are unique for each model, and several
#                models can be plotted at once.
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

SETTINGS_DIR = os.environ['USH_DIR']
sys.path.insert(0, os.path.abspath(SETTINGS_DIR))
from settings import Toggle, Templates, Paths, Presets, ModelSpecs, Reference
from plotter import Plotter
from prune_stat_files import prune_data
import plot_util
import df_preprocessing
from check_variables import *

# ================ GLOBALS AND CONSTANTS ================

plotter = Plotter(fig_size=(18., 14.))
plotter.set_up_plots()
toggle = Toggle()
templates = Templates()
paths = Paths()
presets = Presets()
model_colors = ModelSpecs()
reference = Reference()


# =================== FUNCTIONS =========================


def plot_stat_by_level(df: pd.DataFrame, logger: logging.Logger, 
                       date_range: tuple, model_list: list, num: int = 0, 
                       flead='all', metric1_name: str = 'BCRMSE', 
                       metric2_name: str = 'ME', x_min_limit: float = -10., 
                       x_max_limit: float = 10., x_lim_lock: bool = False, 
                       y_min_limit: float = 50., y_max_limit: float = 1000., 
                       y_lim_lock: bool = False,  
                       ylabel: str = 'Pressure Level (hPa)', 
                       date_type: str = 'VALID', line_type: str = 'SL1L2',
                       date_hours: list = [0,6,12,18], save_dir: str = '.', 
                       dpi: int = 300, confidence_intervals: bool = False,
                       interp_pts: list = [],
                       bs_nrep: int = 5000, bs_method: str = 'MATCHED_PAIRS',
                       bs_min_samp: int = 300, ci_lev: float = .95, 
                       eval_period: str = 'TEST', save_header: str = '', 
                       display_averages: bool = True, 
                       plot_group: str = 'sfc_upper',
                       sample_equalization: bool = True,
                       plot_logo_left: bool = False,
                       plot_logo_right: bool = False, path_logo_left: str = '.',
                       path_logo_right: str = '.', zoom_logo_left: float = 1.,
                       zoom_logo_right: float = 1.):

    logger.info("========================================")
    logger.info(f"Creating Plot {num} ...")
   
    if df.empty:
        logger.warning(f"Empty Dataframe. Continuing onto next plot...")
        logger.info("========================================")
        return None

    fig, ax = plotter.get_plots(num)  
    variable_translator = reference.variable_translator
    domain_translator = reference.domain_translator
    model_settings = model_colors.model_settings

    # filter by forecast lead times
    if str(flead).upper() == 'ALL':
        frange_string = 'All Available Forecasts'
        frange_save_string = 'ALL_LEADS'
        pass
    elif isinstance(flead, list):
        if len(flead) <= 8:
            if len(flead) > 1:
                frange_phrase = 's '+', '.join([str(f) for f in flead])
            else:
                frange_phrase = ' '+', '.join([str(f) for f in flead])
            frange_save_phrase = '-'.join([str(f) for f in flead])
        else:
            frange_phrase = f's {flead[0]}'+u'\u2013'+f'{flead[-1]}'
            frange_save_phrase = f'{flead[0]}-TO-F{flead[-1]}'
        frange_string = f'Forecast Hour{frange_phrase}'
        frange_save_string = f'F{frange_save_phrase}'
        df = df[df['LEAD_HOURS'].isin(flead)]
    elif isinstance(flead, tuple):
        frange_string = (f'Forecast Hours {flead[0]:02d}'
                         +u'\u2013'+f'{flead[1]:02d}')
        frange_save_string = f'F{flead[0]:02d}-F{flead[1]:02d}'
        df = df[
            (df['LEAD_HOURS'] >= flead[0]) & (df['LEAD_HOURS'] <= flead[1])
        ]
    elif isinstance(flead, np.int):
        frange_string = f'Forecast Hour {flead:02d}'
        frange_save_string = f'F{flead:02d}'
        df = df[df['LEAD_HOURS'] == flead]
    else:
        e1 = f"Invalid forecast lead: \'{flead}\'"
        e2 = f"Please check settings for forecast leads"
        logger.error(e1)
        logger.error(e2)
        raise ValueError(e1+"\n"+e2)

    # Remove from date_hours the valid/init hours that don't exist in the 
    # dataframe
    date_hours = np.array(date_hours)[[
        str(x) in df[str(date_type).upper()].dt.hour.astype(str).tolist() 
        for x in date_hours
    ]]

    if interp_pts and '' not in interp_pts:
        interp_shape = list(df['INTERP_MTHD'])[0]
        if 'SQUARE' in interp_shape:
            widths = [int(np.sqrt(float(p))) for p in interp_pts]
        elif 'CIRCLE' in interp_shape:
            widths = [int(np.sqrt(float(p)+4)) for p in interp_pts]
        elif np.all([int(p) == 1 for p in interp_pts]):
            widths = [1 for p in interp_pts]
        else:
            error_string = (
                f"Unknown INTERP_MTHD used to compute INTERP_PNTS: {interp_shape}."
                + f" Check the INTERP_MTHD column in your METplus stats files."
                + f" INTERP_MTHD must have either \"SQUARE\" or \"CIRCLE\""
                + f" in the name"
            )
            logger.error(error_string)
            raise ValueError(error_string)
        if isinstance(interp_pts, list):
            if len(interp_pts) <= 8:
                if len(interp_pts) > 1:
                    interp_pts_phrase = 's '+', '.join([str(p) for p in widths])
                else:
                    interp_pts_phrase = ' '+', '.join([str(p) for p in widths])
                interp_pts_save_phrase = '-'.join([str(p) for p in widths])
            else:
                interp_pts_phrase = f's {widths[0]}'+u'\u2013'+f'{widths[-1]}'
                interp_pts_save_phrase = f'{widths[0]}-{widths[-1]}'
            interp_pts_string = f'(Width{interp_pts_phrase})'
            interp_pts_save_string = f'width{interp_pts_save_phrase}'
            df = df[df['INTERP_PNTS'].isin(interp_pts)]
        elif isinstance(intep_pts, np.int):
            interp_pts_string = f'(Wifth {widths:d})'
            interp_pts_save_string = f'width{widths:d}'
            df = df[df['INTERP_PNTS'] == widths]
        else:
            error_string = (
                f"Invalid interpolation points entry: \'{interp_pts}\'\n"
                + f"Please check settings for interpolation points."
            )
            logger.error(error_string)
            raise ValueError(error_string)

    plevs = df['OBS_LEV'].str[1:].astype(int)
    df['PLEV'] = plevs.tolist()

    # Remove from model_list the models that don't exist in the dataframe
    cols_to_keep = [
        str(model) 
        in df['MODEL'].tolist() 
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
            f"{models_removed_string} data were not found and will not be"
            + f" plotted."
        )
    if df.empty:
        logger.warning(f"Empty Dataframe. Continuing onto next plot...")
        plt.close(num)
        logger.info("========================================")
        return None
    group_by = ['MODEL','PLEV']
    if sample_equalization:
        df, bool_success = plot_util.equalize_samples(logger, df, group_by)
        if not bool_success:
            sample_equalization = False
    df_groups = df.groupby(group_by)
    # Aggregate unit statistics before calculating metrics
    if str(line_type).upper() == 'CTC':
        df_aggregated = df_groups.sum()
    else:
        df_aggregated = df_groups.mean()
    if sample_equalization:
        df_aggregated['COUNTS']=df_groups.size()
    # Remove data if they exist for some but not all models at some value of 
    # the indep. variable. Otherwise plot_util.calculate_stat will throw an 
    # error
    df_split = [df_aggregated.xs(str(model)) for model in model_list]
    df_reduced = reduce(
        lambda x,y: pd.merge(
            x, y, on='PLEV', how='inner'
        ), 
        df_split
    )
    df_aggregated = df_aggregated[
        df_aggregated.index.get_level_values('PLEV').isin(df_reduced.index)
    ]

    if df_aggregated.empty:
        logger.warning(f"Empty Dataframe. Continuing onto next plot...")
        plt.close(num)
        logger.info("========================================")
        return None

    # Calculate desired metrics
    metric_long_names = []
    for stat in [metric1_name, metric2_name]:
        if stat:
            stat_output = plot_util.calculate_stat(
                logger, df_aggregated, str(stat).lower()
            )
            df_aggregated[str(stat).upper()] = stat_output[0]
            metric_long_names.append(stat_output[2])
            if confidence_intervals:
                ci_output = df_groups.apply(
                    lambda x: plot_util.calculate_bootstrap_ci(
                        logger, bs_method, x, str(stat).lower(), bs_nrep,
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
                df_aggregated[str(stat).upper()+'_BLERR'] = ci_output[
                    'CI_LOWER'
                ].values
                df_aggregated[str(stat).upper()+'_BUERR'] = ci_output[
                    'CI_UPPER'
                ].values

    df_aggregated[str(metric1_name).upper()] = (
        df_aggregated[str(metric1_name).upper()]
    ).astype(float).tolist()
    if metric2_name is not None:
        df_aggregated[str(metric2_name).upper()] = (
            df_aggregated[str(metric2_name).upper()]
        ).astype(float).tolist()

    df_aggregated = df_aggregated[
        df_aggregated.index.isin(model_list, level='MODEL')
    ]

    pivot_metric1 = pd.pivot_table(
        df_aggregated, values=str(metric1_name).upper(), columns='MODEL', 
        index='PLEV'
    )
    if sample_equalization:
        pivot_counts = pd.pivot_table(
            df_aggregated, values='COUNTS', columns='MODEL', 
            index='PLEV'
        )
    if metric2_name:
        pivot_metric2 = pd.pivot_table(
            df_aggregated, values=str(metric2_name).upper(), columns='MODEL', 
            index='PLEV'
        )
    if confidence_intervals:
        pivot_ci_lower1 = pd.pivot_table(
            df_aggregated, values=str(metric1_name).upper()+'_BLERR',
            columns='MODEL', index='PLEV'
        )
        pivot_ci_upper1 = pd.pivot_table(
            df_aggregated, values=str(metric1_name).upper()+'_BUERR',
            columns='MODEL', index='PLEV'
        )
        if metric2_name:
            pivot_ci_lower2 = pd.pivot_table(
                df_aggregated, values=str(metric2_name).upper()+'_BLERR',
                columns='MODEL', index='PLEV'
            )
            pivot_ci_upper2 = pd.pivot_table(
                df_aggregated, values=str(metric2_name).upper()+'_BUERR',
                columns='MODEL', index='PLEV'
            )
    if (metric2_name and (pivot_metric1.empty or pivot_metric2.empty)):
        print_varname = df['FCST_VAR'].tolist()[0]
        logger.warning(
            f"Could not find (and cannot plot) {metric1_name} and/or"
            + f" {metric2_name} stats for {print_varname} at any pressure"
            + f" level. Continuing ..."
        )
        plt.close(num)
        logger.info("========================================")
        return None
    elif not metric2_name and pivot_metric1.empty:
        print_varname = df['FCST_VAR'].tolist()[0]
        logger.warning(
            f"Could not find (and cannot plot) {metric1_name}"
            + f" stats for {print_varname} at any pressure level. "
            + f"Continuing ..."
        )
        plt.close(num)
        logger.info("========================================")
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
    colors_corrected=False
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
                        models_sharing_colors, 'model')!=-1):
                    need_to_rename = models_sharing_colors[
                        np.flatnonzero(np.core.defchararray.find(
                            models_sharing_colors, 'model'
                        )!=-1)[0]
                    ]
                else:
                    continue
                models_renamed[models_renamed==need_to_rename] = (
                    'model'+str(count_renamed)
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
    if confidence_intervals:
        indices_in_common1 = list(set.intersection(*map(
            set, 
            [
                pivot_metric1.index, 
                pivot_ci_lower1.index, 
                pivot_ci_upper1.index
            ]
        )))
        pivot_metric1 = pivot_metric1[pivot_metric1.index.isin(indices_in_common1)]
        pivot_ci_lower1 = pivot_ci_lower1[pivot_ci_lower1.index.isin(indices_in_common1)]
        pivot_ci_upper1 = pivot_ci_upper1[pivot_ci_upper1.index.isin(indices_in_common1)]
        if sample_equalization:
            pivot_counts = pivot_counts[pivot_counts.index.isin(indices_in_common1)]
        if metric2_name is not None:
            indices_in_common2 = list(set.intersection(*map(
                set, 
                [
                    pivot_metric2.index, 
                    pivot_ci_lower2.index, 
                    pivot_ci_upper2.index
                ]
            )))
            pivot_metric2 = pivot_metric2[pivot_metric2.index.isin(indices_in_common2)]
            pivot_ci_lower2 = pivot_ci_lower2[pivot_ci_lower2.index.isin(indices_in_common2)]
            pivot_ci_upper2 = pivot_ci_upper2[pivot_ci_upper2.index.isin(indices_in_common2)]
    y_vals1 = pivot_metric1.index
    if metric2_name is not None:
        y_vals2 = pivot_metric2.index
    plev_incr = np.abs(np.diff(y_vals1))
    if plev_incr.size == 0:
        min_incr = 100
    else:
        min_incr = np.min(plev_incr) 
    x_min = x_min_limit
    x_max = x_max_limit
    plot_reference = [False, False]
    ref_metrics = ['OBAR']
    if str(metric1_name).upper() in ref_metrics:
        plot_reference[0] = True
        pivot_reference1 = pivot_metric1
        reference1 = pivot_reference1.mean(axis=1)
        if confidence_intervals:
            reference_ci_lower1 = pivot_ci_lower1.mean(axis=1)
            reference_ci_upper1 = pivot_ci_upper1.mean(axis=1)
        if not np.any((pivot_reference1.T/reference1).T == 1.):
            logger.warning(
                f"{str(metric1_name).upper()} is requested, but the value "
                + f"varies from model to model. "
                + f"Will plot an individual line for each model. If a "
                + f"single reference line is preferred, set the "
                + f"sample_equalization toggle in ush/settings.py to 'True', "
                + f"and check in the log file if sample equalization "
                + f"completed successfully."
            )
            plot_reference[0] = False
    if metric2_name is not None and str(metric2_name).upper() in ref_metrics:
        plot_reference[1] = True
        pivot_reference2 = pivot_metric2
        reference2 = pivot_reference2.mean(axis=1)
        if confidence_intervals:
            reference_ci_lower2 = pivot_ci_lower2.mean(axis=1)
            reference_ci_upper2 = pivot_ci_upper2.mean(axis=1)
        if not np.any((pivot_reference2.T/reference2).T == 1.):
            logger.warning(
                f"{str(metric2_name).upper()} is requested, but the value "
                + f"varies from model to model. "
                + f"Will plot an individual line for each model. If a "
                + f"single reference line is preferred, set the "
                + f"sample_equalization toggle in ush/settings.py to 'True', "
                + f"and check in the log file if sample equalization "
                + f"completed successfully."
            )
            plot_reference[1] = False
    if np.any(plot_reference):
        plotted_reference = [False, False]
        if confidence_intervals:
            plotted_reference_CIs = [False, False]
    f = lambda m,c,ls,lw,ms,mec: plt.plot(
        [], [], marker=m, mec=mec, mew=2., c=c, ls=ls, lw=lw, ms=ms
    )[0]
    if metric2_name is not None:
        if np.any(plot_reference):
            ref_color_dict = model_colors.get_color_dict('obs')
            handles = []
            labels = []
            line_settings = ['solid','dashed']
            metric_names = [metric1_name, metric2_name]
            for p, rbool in enumerate(plot_reference):
                if rbool:
                    handles += [
                        f('', ref_color_dict['color'], line_settings[p], 5., 0, 'white')
                    ]
                else:
                    handles += [
                        f('', 'black', line_settings[p], 5., 0, 'white')
                    ]
                labels += [
                    str(metric_names[p]).upper()
                ]
        else:
            handles = [
                f('', 'black', line_setting, 5., 0, 'white') 
                for line_setting in ['solid','dashed']
            ]
            labels = [
                str(metric_name).upper() 
                for metric_name in [metric1_name, metric2_name]
            ]
    else:
        handles = []
        labels = []
    for m in range(len(mod_setting_dicts)):
        if model_list[m] in model_colors.model_alias:
            model_plot_name = (
                model_colors.model_alias[model_list[m]]['plot_name']
            )
        else:
            model_plot_name = model_list[m]
        if str(model_list[m]) not in pivot_metric1:
            continue
        x_vals_metric1 = pivot_metric1[str(model_list[m])].values
        x_vals_metric1_mean = np.nanmean(x_vals_metric1)
        if metric2_name is not None:
            x_vals_metric2 = pivot_metric2[str(model_list[m])].values
            x_vals_metric2_mean = np.nanmean(x_vals_metric2)
        if confidence_intervals:
            x_vals_ci_lower1 = pivot_ci_lower1[
                str(model_list[m])
            ].values
            x_vals_ci_upper1 = pivot_ci_upper1[
                str(model_list[m])
            ].values
            if metric2_name is not None:
                x_vals_ci_lower2 = pivot_ci_lower2[
                    str(model_list[m])
                ].values
                x_vals_ci_upper2 = pivot_ci_upper2[
                    str(model_list[m])
                ].values
        if not x_lim_lock:
            if metric2_name is not None:
                x_vals_metric_min = np.nanmin([
                    x_vals_metric1, x_vals_metric2
                ])
                x_vals_metric_max = np.nanmax([
                    x_vals_metric1, x_vals_metric2
                ])
            else:
                x_vals_metric_min = np.nanmin(x_vals_metric1)
                x_vals_metric_max = np.nanmax(x_vals_metric1)
            if m == 0:
                x_mod_min = x_vals_metric_min
                x_mod_max = x_vals_metric_max
            else:
                x_mod_min = np.nanmin([x_mod_min, x_vals_metric_min])
                x_mod_max = np.nanmax([x_mod_max, x_vals_metric_max])
            if (x_vals_metric_min > x_min_limit 
                    and x_vals_metric_min <= x_mod_min):
                x_min = x_vals_metric_min
            if (x_vals_metric_max < x_max_limit 
                    and x_vals_metric_max >= x_mod_max):
                x_max = x_vals_metric_max
        if np.abs(x_vals_metric1_mean) < 1E4:
            metric1_mean_fmt_string = f'{x_vals_metric1_mean:.2f}'
        else:
            metric1_mean_fmt_string = f'{x_vals_metric1_mean:.2E}'
        if plot_reference[0]:
            if not plotted_reference[0]:
                ref_color_dict = model_colors.get_color_dict('obs')
                plt.plot(
                    reference1, y_vals1.tolist(),
                    marker=ref_color_dict['marker'],
                    c=ref_color_dict['color'], mew=2., mec='white',
                    figure=fig, ms=ref_color_dict['markersize'], ls='solid',
                    lw=ref_color_dict['linewidth']
                )
                plotted_reference[0] = True
        else:
            plt.plot(
                x_vals_metric1, y_vals1.tolist(), 
                marker=mod_setting_dicts[m]['marker'], 
                c=mod_setting_dicts[m]['color'], mew=2., mec='white', 
                figure=fig, ms=mod_setting_dicts[m]['markersize'], ls='solid', 
                lw=mod_setting_dicts[m]['linewidth']
            )
        if metric2_name is not None:
            if np.abs(x_vals_metric2_mean) < 1E4:
                metric2_mean_fmt_string = f'{x_vals_metric2_mean:.2f}'
            else:
                metric2_mean_fmt_string = f'{x_vals_metric2_mean:.2E}'
            if plot_reference[1]:
                if not plotted_reference[0]:
                    ref_color_dict = model_colors.get_color_dict('obs')
                    plt.plot(
                        reference2, y_vals2.tolist(),
                        marker=ref_color_dict['marker'],
                        c=ref_color_dict['color'], mew=2., mec='white',
                        figure=fig, ms=ref_color_dict['markersize'], ls='dashed',
                        lw=ref_color_dict['linewidth']
                    )
                    plotted_reference[1] = True
            else:
                plt.plot(
                    x_vals_metric2, y_vals2.tolist(), 
                    marker=mod_setting_dicts[m]['marker'], 
                    c=mod_setting_dicts[m]['color'], mew=2., mec='white', 
                    figure=fig, ms=mod_setting_dicts[m]['markersize'], ls='dashed', 
                    lw=mod_setting_dicts[m]['linewidth']
                )
        if confidence_intervals:
            if plot_reference[0]:
                if not plotted_reference_CIs[0]:
                    ref_color_dict = model_colors.get_color_dict('obs')
                    plt.errorbar(
                        reference1, y_vals1.tolist(),
                        xerr=[np.abs(reference_ci_lower1), reference_ci_upper1],
                        fmt='none', ecolor=ref_color_dict['color'],
                        elinewidth=ref_color_dict['linewidth']/1.5,
                        capsize=9., capthick=ref_color_dict['linewidth']/1.5,
                        alpha=.70, zorder=0
                    )
                    plotted_reference_CIs[0] = True
            else:
                plt.errorbar(
                    x_vals_metric1, y_vals1.tolist(),
                    xerr=[np.abs(x_vals_ci_lower1), x_vals_ci_upper1],
                    fmt='none', ecolor=mod_setting_dicts[m]['color'],
                    elinewidth=mod_setting_dicts[m]['linewidth']/1.5,
                    capsize=9., capthick=mod_setting_dicts[m]['linewidth']/1.5,
                    alpha=.70, zorder=0
                )
            if metric2_name is not None:
                if plot_reference[1]:
                    if not plotted_reference_CIs[1]:
                        ref_color_dict = model_colors.get_color_dict('obs')
                        plt.errorbar(
                            reference2, y_vals2.tolist(),
                            xerr=[np.abs(reference_ci_lower2), reference_ci_upper2],
                            fmt='none', ecolor=ref_color_dict['color'],
                            elinewidth=ref_color_dict['linewidth']/1.5,
                            capsize=9., capthick=ref_color_dict['linewidth']/1.5,
                            alpha=.70, zorder=0
                        )
                        plotted_reference_CIs[1] = True
                else:
                    plt.errorbar(
                        x_vals_metric2, y_vals2.tolist(),
                        xerr=[np.abs(x_vals_ci_lower2), x_vals_ci_upper2],
                        fmt='none', ecolor=mod_setting_dicts[m]['color'],
                        elinewidth=mod_setting_dicts[m]['linewidth']/1.5,
                        capsize=9., capthick=mod_setting_dicts[m]['linewidth']/1.5,
                        alpha=.70, zorder=0
                    )
        handles+=[
            f(
                mod_setting_dicts[m]['marker'], mod_setting_dicts[m]['color'], 
                'solid', mod_setting_dicts[m]['linewidth'], 
                mod_setting_dicts[m]['markersize'], 'white'
            )
        ]
        if display_averages:
            if metric2_name is not None:
                labels+=[
                    f'{model_plot_name} ({metric1_mean_fmt_string},'
                    + f' {metric2_mean_fmt_string})'
                ]
            else:
                labels+=[
                    f'{model_plot_name} ({metric1_mean_fmt_string})'
                ]
        else:
            labels+=[f'{model_plot_name}']

    # Zero line
    plt.axvline(x=0, color='black', linestyle='--', linewidth=1, zorder=0) 

    # Configure axis ticks
    yticks = [1000, 925, 850, 700, 500, 300, 250, 200, 100, 50, 10, 1]
    if metric2_name is not None:
        yticks = np.array([
            ytick 
            for ytick in yticks 
            if (
                ytick>=min([min(y_vals1),min(y_vals2)]) 
                and ytick<=max([max(y_vals1),max(y_vals2)])
            )
        ])
    else:
        yticks = np.array([
            ytick 
            for ytick in yticks 
            if (
                ytick>=min(y_vals1) 
                and ytick<=max(y_vals1)
            )
        ])
    ytick_labels = yticks.astype(str)
    # x ticks and axis limits adjust based on the size of the x_range 
    x_range_categories = np.array([
        [np.power(10.,x), 2.*np.power(10.,x)] 
        for x in [-5,-4,-3,-2,-1,0,1,2,3,4,5]
    ]).flatten()
    round_to_nearest_categories = x_range_categories/20.
    x_range = x_max-x_min
    round_to_nearest =  round_to_nearest_categories[
        np.digitize(x_range, x_range_categories[:-1])
    ]
    xlim_min = np.floor(x_min/round_to_nearest)*round_to_nearest
    xlim_max = np.ceil(x_max/round_to_nearest)*round_to_nearest
    if len(str(xlim_min)) > 5 and np.abs(xlim_min) < 1.:
        xlim_min = float(
            np.format_float_scientific(xlim_min, unique=False, precision=3)
        )
    xticks = np.arange(xlim_min, xlim_max+round_to_nearest, round_to_nearest)
    if any([len(str(xtick)) > 5 and np.abs(xtick) < 1. for xtick in xticks]):
        xtick_labels = []
        for xtick in xticks:
            xtick_labels.append(float(np.format_float_scientific(
                xtick, unique=False, precision=3
            )))
    else:
        xtick_labels = [str(xtick) for xtick in xticks]
    if len(xticks) < 20:
        if max([len(str(xtick)) for xtick in xticks]) < 5:
            show_xtick_every = 1
        else:
            show_xtick_every = 2
    else:
        show_xtick_every = 2
    xtick_labels_with_blanks = ['' for item in xtick_labels]
    for i, item in enumerate(xtick_labels[::int(show_xtick_every)]):
        xtick_labels_with_blanks[int(show_xtick_every)*i] = item
    var_long_name_key = df['FCST_VAR'].tolist()[0]
    if str(var_long_name_key).upper() == 'HGT':
        if str(df['OBS_VAR'].tolist()[0]).upper() in ['CEILING']:
            var_long_name_key = 'HGTCLDCEIL'
        elif str(df['OBS_VAR'].tolist()[0]).upper() in ['HPBL']:
            var_long_name_key = 'HPBL'
    var_long_name = variable_translator[var_long_name_key]
    units = df['FCST_UNITS'].tolist()[0]
    if units in reference.unit_conversions:
        units = reference.unit_conversions[units]['convert_to']
    if units == '-':
        units = ''
    metrics_using_var_units = [
        'BCRMSE','RMSE','BIAS','ME','FBAR','OBAR','MAE','FBAR_OBAR',
        'SPEED_ERR','DIR_ERR','RMSVE','VDIFF_SPEED','VDIF_DIR',
        'FBAR_OBAR_SPEED','FBAR_OBAR_DIR','FBAR_SPEED','FBAR_DIR'
    ]
    if metric2_name is not None:
        metric1_string, metric2_string = metric_long_names
        if (str(metric1_name).upper() in metrics_using_var_units 
                and str(metric2_name).upper() in metrics_using_var_units):
            if units:
                xlabel = f'{var_long_name} ({units})'
            else:
                xlabel = f'{var_long_name} (unitless)'
        else:
            xlabel = f'{metric1_string} and {metric2_string}'
    else:
        metric1_string = metric_long_names[0]
        if str(metric1_name).upper() in metrics_using_var_units:
            if units:
                xlabel = f'{var_long_name} ({units})'
            else:
                xlabel = f'{var_long_name} (unitless)'
        else:
            xlabel = f'{metric1_string}'
    ax.set_xlim(xlim_min, xlim_max)
    if y_lim_lock:
        y_min, y_max = [y_min_limit, y_max_limit]
    else:
        if metric2_name is not None:
            y_min, y_max = [
                min([min(y_vals1),min(y_vals2)]), 
                max([max(y_vals1),max(y_vals2)])
            ]
        else:
            y_min, y_max = [
                min(y_vals1), 
                max(y_vals1)
            ]
        if y_min < y_min_limit:
            y_min = y_min_limit
        if y_max > y_max_limit:
            y_max = y_max_limit
    y_buffer_size = .015
    ylim_min = np.exp(np.log(y_min)-y_buffer_size)
    ylim_max = np.exp(np.log(y_max)+y_buffer_size)
    ax.set_ylim(ylim_min, ylim_max)
    # Y-values should decrease upward; set the following after setting ax 
    # limits
    ax.invert_yaxis()
    # Pressure decreases logarithmically with height
    ax.set_yscale('log')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel) 
    ax.set_yticklabels(ytick_labels)
    ax.set_xticklabels(xtick_labels_with_blanks)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.tick_params(
        labelleft=True, labelright=False, labelbottom=True, labeltop=False
    )
    ax.tick_params(
        left=False, labelleft=False, labelright=False, labelbottom=False, 
        labeltop=False, which='minor', axis='y'
    )

    ax.legend(
        handles, labels, loc='upper center', fontsize=15, framealpha=1, 
        bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=True, numpoints=2, 
        borderpad=.8, labelspacing=2., columnspacing=3., handlelength=3., 
        handletextpad=.4, borderaxespad=.5) 
    fig.subplots_adjust(bottom=.15, wspace=0., hspace=0)
    ax.grid(
        visible=True, which='major', axis='both', alpha=.5, linestyle='--', 
        linewidth=.5, zorder=0
    )

    if sample_equalization:
        counts = pivot_counts.mean(axis=1, skipna=True).fillna('')
        for count, yval in zip(counts, y_vals1.tolist()):
            if not isinstance(count, str):
                count = str(int(count))
            ax.annotate(
                f'{count}', xy=(1.,yval),
                xycoords=('axes fraction','data'), xytext=(9,0),
                textcoords='offset points', va='center', fontsize=16,
                color='dimgrey', ha='left'
            )
        ax.annotate(
            '#SAMPLES', xy=(1.,1.), xycoords='axes fraction',
            xytext=(9,5), textcoords='offset points', va='bottom',
            fontsize=11, color='dimgrey', ha='right'
        )
        fig.subplots_adjust(right=.95)

    # Title
    domain = df['VX_MASK'].tolist()[0]
    var_savename = df['FCST_VAR'].tolist()[0]
    if domain in list(domain_translator.keys()):
        domain_string = domain_translator[domain]
    else:
        domain_string = domain
    date_hours_string = plot_util.get_name_for_listed_items(
        [f'{date_hour:02d}' for date_hour in date_hours],
        ', ', '', 'Z', 'and ', ''
    )
    '''
    date_hours_string = ' '.join([
        f'{date_hour:02d}Z,' for date_hour in date_hours
    ])
    '''
    date_start_string = date_range[0].strftime('%d %b %Y')
    date_end_string = date_range[1].strftime('%d %b %Y')
    if metric2_name is not None:
        title1 = f'{metric1_string} and {metric2_string}'
    else:
        title1 = f'{metric1_string}'
    if interp_pts and '' not in interp_pts:
        title1+=f' {interp_pts_string}'
    if units:
        title2 = f'{var_long_name} ({units}), {domain_string}'
    else:
        title2 = f'{var_long_name} (unitless), {domain_string}'
    title3 = (f'{str(date_type).capitalize()} {date_hours_string}'
              + f' {date_start_string} to {date_end_string}, {frange_string}')
    title_center = '\n'.join([title1, title2, title3])
    ax.set_title(title_center, loc=plotter.title_loc) 
    logger.info("... Plotting complete.")

    # Logos
    if plot_logo_left:
        if os.path.exists(path_logo_left):
            left_logo_arr = mpimg.imread(path_logo_left)
            left_image_box = OffsetImage(left_logo_arr, zoom=zoom_logo_left*0.9)
            ab_left = AnnotationBbox(
                left_image_box, xy=(0.,1.), xycoords='axes fraction',
                xybox=(0, 3), boxcoords='offset points', frameon = False,
                box_alignment=(0,0)
            )
            ax.add_artist(ab_left)
        else:
            logger.warning(
                f"Left logo path ({path_logo_left}) doesn't exist. "
                + f"Left logo will not be plotted."
            )
    if plot_logo_right:
        if os.path.exists(path_logo_right):
            right_logo_arr = mpimg.imread(path_logo_right)
            if sample_equalization:
                right_image_box = OffsetImage(right_logo_arr, zoom=zoom_logo_right*0.65)
                ab_right = AnnotationBbox(
                    right_image_box, xy=(1.,1.), xycoords='axes fraction',
                    xybox=(0, 20), boxcoords='offset points', frameon = False,
                    box_alignment=(1,0)
                )
            else:
                right_image_box = OffsetImage(right_logo_arr, zoom=zoom_logo_right*0.9)
                ab_right = AnnotationBbox(
                    right_image_box, xy=(1.,1.), xycoords='axes fraction',
                    xybox=(0, 3), boxcoords='offset points', frameon = False,
                    box_alignment=(1,0)
                )
            ax.add_artist(ab_right)
        else:
            logger.warning(
                f"Right logo path ({path_logo_right}) doesn't exist. "
                + f"Right logo will not be plotted."
            )

    # Saving 
    models_savename = '_'.join([str(model) for model in model_list])
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
        time_period_savename = f'{eval_period}'
    save_name = (f'stat_by_level_regional_'
                 + f'{str(domain).lower()}_{str(date_type).lower()}_'
                 + f'{str(date_hours_savename).lower()}_'
                 + f'{str(var_savename).lower()}_'
                 + f'{str(metric1_name).lower()}')
    if metric2_name is not None:
        save_name+=f'_{str(metric2_name).lower()}'
    if interp_pts and '' not in interp_pts:
        save_name+=f'_{str(interp_pts_save_string).lower()}'
    save_name+=f'_{str(frange_save_string).lower()}'
    if save_header:
        save_name = f'{save_header}_'+save_name
    save_subdir = os.path.join(
        save_dir, f'{str(plot_group).lower()}', 
        f'{str(time_period_savename).lower()}'
    )
    if not os.path.isdir(save_subdir):
        try:
            os.makedirs(save_subdir)
        except FileExistsError as e:
            logger.warning(f"Several processes are making {save_subdir} at "
                           + f"the same time. Passing")
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
        os.makedirs(log_metplus_dir)
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
        valid_beg = presets.date_presets[EVAL_PERIOD]['valid_beg']
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
        e = (
            f"Invalid DATE_TYPE: {str(date_type).upper()}. Valid values are"
            + f" VALID or INIT"
        )
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
    logger.debug(f"INTERP_PNTS: {INTERP_PNTS if INTERP_PNTS else 'No interpolation points'}")

    logger.debug('----------------------------------------')
    logger.debug(f"Advanced settings (configurable in {SETTINGS_DIR}/settings.py)")
    logger.debug(f"Y_MIN_LIMIT: {Y_MIN_LIMIT}")
    logger.debug(f"Y_MAX_LIMIT: {Y_MAX_LIMIT}")
    logger.debug(f"Y_LIM_LOCK: {Y_LIM_LOCK}")
    logger.debug(f"X_MIN_LIMIT: {X_MIN_LIMIT}")
    logger.debug(f"X_MAX_LIMIT: {X_MAX_LIMIT}")
    logger.debug(f"X_LIM_LOCK: {X_LIM_LOCK}")
    logger.debug(f"Display averages? {'yes' if display_averages else 'no'}")
    logger.debug(
        f"Clear prune directories? {'yes' if clear_prune_dir else 'no'}"
    )
    logger.debug(f"Plot upper-left logo? {'yes' if plot_logo_left else 'no'}")
    logger.debug(
        f"Plot upper-right logo? {'yes' if plot_logo_right else 'no'}"
    )
    logger.debug(f"Upper-left logo path: {path_logo_left}")
    logger.debug(f"Upper-right logo path: {path_logo_right}")
    logger.debug(
        f"Upper-left logo fraction of original size: {zoom_logo_left}"
    )
    logger.debug(
        f"Upper-right logo fraction of original size: {zoom_logo_right}"
    )
    if CONFIDENCE_INTERVALS:
        logger.debug(f"Confidence Level: {int(ci_lev*100)}%")
        logger.debug(f"Bootstrap method: {bs_method}")
        logger.debug(f"Bootstrap repetitions: {bs_nrep}")
        logger.debug(
            f"Minimum sample size for confidence intervals: {bs_min_samp}"
        )
    logger.debug('========================================')

    date_range = (
        datetime.strptime(date_beg, '%Y%m%d'), 
        datetime.strptime(date_end, '%Y%m%d')+td(days=1)-td(milliseconds=1)
    )
    if len(METRICS) == 1:
        metrics = (METRICS[0], None)
    elif len(METRICS) > 1:
        metrics = METRICS[:2]
    else:
        e = (f"Received no list of metrics.  Check that, for the METRICS"
             + f" setting, a comma-separated string of at least one metric is"
             + f" provided")
        logger.error(e)
        raise ValueError(e)
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
        if metric is not None:
            if (str(metric).lower()
                    not in case_specs['plot_stats_list']
                    .replace(' ','').split(',')):
                e = (f"The requested metric is not valid for the"
                     + f" requested case type ({VERIF_CASETYPE}) and"
                     + f" line type ({LINE_TYPE}): {metric}")
                logger.error(e)
                logger.error("Quitting ...")
                raise ValueError(e+"\nQuitting ...")
    for requested_var in VARIABLES:
        if requested_var in list(case_specs['var_dict'].keys()):
            var_specs = case_specs['var_dict'][requested_var]
        else:
            e = (f"The requested variable is not valid for the requested case"
                 + f" type ({VERIF_CASETYPE}) and line_type ({LINE_TYPE}):"
                 + f"{requested_var}")
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
        for domain in DOMAINS:
            if str(domain) not in case_specs['vx_mask_list']:
                e = (f"The requested domain is not valid for the requested"
                     + f" case type ({VERIF_CASETYPE}) and line_type"
                     + f" ({LINE_TYPE}): {domain}")
                logger.warning(e)
                logger.warning("Continuing ...")
                continue
            df = df_preprocessing.get_preprocessed_data(
                logger, STATS_DIR, PRUNE_DIR, OUTPUT_BASE_TEMPLATE, VERIF_CASE, 
                VERIF_TYPE, LINE_TYPE, DATE_TYPE, date_range, EVAL_PERIOD, 
                date_hours, FLEADS, requested_var, fcst_var_names, obs_var_names, 
                MODELS, domain, INTERP, MET_VERSION, clear_prune_dir
            )
            if df is None:
                continue
            plot_stat_by_level(
                df, logger, date_range, MODELS, num=num, flead=FLEADS, 
                metric1_name=metrics[0], metric2_name=metrics[1], 
                date_type=DATE_TYPE, x_min_limit=X_MIN_LIMIT, 
                x_max_limit=X_MAX_LIMIT, x_lim_lock=X_LIM_LOCK, 
                y_min_limit=Y_MIN_LIMIT, y_max_limit=Y_MAX_LIMIT, 
                y_lim_lock=Y_LIM_LOCK, ylabel='Pressure Level (hPa)', 
                line_type=LINE_TYPE, date_hours=date_hours, 
                save_dir=SAVE_DIR, eval_period=EVAL_PERIOD,
                display_averages=display_averages, save_header=URL_HEADER,
                plot_group=plot_group, 
                confidence_intervals=CONFIDENCE_INTERVALS, interp_pts=INTERP_PNTS,
                bs_nrep=bs_nrep, bs_method=bs_method, ci_lev=ci_lev, 
                bs_min_samp=bs_min_samp, sample_equalization=sample_equalization,
                plot_logo_left=plot_logo_left, plot_logo_right=plot_logo_right,
                path_logo_left=path_logo_left, path_logo_right=path_logo_right,
                zoom_logo_left=zoom_logo_left, zoom_logo_right=zoom_logo_right
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
    VALID_BEG = check_VALID_BEG(os.environ['VALID_BEG'], DATE_TYPE, EVAL_PERIOD, plot_type='time_series')
    VALID_END = check_VALID_END(os.environ['VALID_END'], DATE_TYPE, EVAL_PERIOD, plot_type='time_series')
    INIT_BEG = check_INIT_BEG(os.environ['INIT_BEG'], DATE_TYPE, EVAL_PERIOD, plot_type='time_series')
    INIT_END = check_INIT_END(os.environ['INIT_END'], DATE_TYPE, EVAL_PERIOD, plot_type='time_series')

    # list of variables
    # Options: {'TMP','HGT','CAPE','RH','DPT','UGRD','VGRD','UGRD_VGRD','TCDC',
    #           'VIS'}
    VARIABLES = check_var_name(os.environ['var_name']).replace(' ','').split(',')

    # list of lead hours
    # Options: {list of lead hours; string, 'all'; tuple, start/stop flead; 
    #           string, single flead}
    FLEADS = check_FCST_LEAD(os.environ['FCST_LEAD']).replace(' ','').split(',')

    # list of levels
    FCST_LEVELS = re.split(r',(?![0*])', check_FCST_LEVEL(os.environ['FCST_LEVEL']).replace(' ',''))
    OBS_LEVELS = re.split(r',(?![0*])', check_OBS_LEVEL(os.environ['OBS_LEVEL']).replace(' ',''))

    FCST_THRESH = check_FCST_THRESH(os.environ['FCST_THRESH'], LINE_TYPE)
    OBS_THRESH = check_OBS_THRESH(os.environ['OBS_THRESH'], FCST_THRESH, LINE_TYPE).replace(' ','').split(',')
    FCST_THRESH = FCST_THRESH.replace(' ','').split(',')
    
    # requires two metrics to plot
    METRICS = list(filter(None, check_STATS(os.environ['STATS']).replace(' ','').split(',')))

    # set the lowest possible lower (and highest possible upper) axis limits. 
    # E.g.: If X_LIM_LOCK == True, use X_MIN_LIMIT as the definitive lower 
    # limit (ditto with X_MAX_LIMIT)
    # If X_LIM_LOCK == False, then allow lower and upper limits to adjust to 
    # data as long as limits don't overcome X_MIN_LIMIT or X_MAX_LIMIT 
    X_MIN_LIMIT = toggle.plot_settings['x_min_limit']
    X_MAX_LIMIT = toggle.plot_settings['x_max_limit']
    X_LIM_LOCK = toggle.plot_settings['x_lim_lock']
    Y_MIN_LIMIT = toggle.plot_settings['y_min_limit']
    Y_MAX_LIMIT = toggle.plot_settings['y_max_limit']
    Y_LIM_LOCK = toggle.plot_settings['y_lim_lock']

    # configure CIs
    CONFIDENCE_INTERVALS = check_CONFIDENCE_INTERVALS(os.environ['CONFIDENCE_INTERVALS']).replace(' ','')
    bs_nrep = toggle.plot_settings['bs_nrep']
    bs_method = toggle.plot_settings['bs_method']
    ci_lev = toggle.plot_settings['ci_lev']
    bs_min_samp = toggle.plot_settings['bs_min_samp']

    # list of points used in interpolation method
    INTERP_PNTS = check_INTERP_PTS(os.environ['INTERP_PNTS']).replace(' ','').split(',')

    # At each value of the independent variable, whether or not to remove
    # samples used to aggregate each statistic if the samples are not shared
    # by all models.  Required to display sample sizes
    sample_equalization = toggle.plot_settings['sample_equalization']

    # Whether or not to display average values beside legend labels
    display_averages = toggle.plot_settings['display_averages']

    # Whether or not to clear the intermediate directory that stores pruned data
    clear_prune_dir = toggle.plot_settings['clear_prune_directory']

    # Information about logos
    plot_logo_left = toggle.plot_settings['plot_logo_left']
    plot_logo_right = toggle.plot_settings['plot_logo_right']
    zoom_logo_left = toggle.plot_settings['zoom_logo_left']
    zoom_logo_right = toggle.plot_settings['zoom_logo_right']
    path_logo_left = paths.logo_left_path
    path_logo_right = paths.logo_right_path

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
    INTERP_PNTS = [str(pts) for pts in INTERP_PNTS]
    VERIF_CASETYPE = str(VERIF_CASE).lower() + '_' + str(VERIF_TYPE).lower()
    CONFIDENCE_INTERVALS = str(CONFIDENCE_INTERVALS).lower() in [
        'true', '1', 't', 'y', 'yes'
    ]
    main()
