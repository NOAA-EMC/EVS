#! /usr/bin/env python3

###############################################################################
#
# Name:          threshold_average.py
# Contact(s):    Marcel Caron
# Developed:     Nov. 22, 2021 by Marcel Caron 
# Last Modified: Dec. 2, 2021 by Marcel Caron             
# Title:         Line plot of verification metric as a function of 
#                forecast threshold
# Abstract:      Plots METplus output (e.g., BCRMSE) as a line plot, 
#                varying by forecast threshold, which represents the x-axis. 
#                Line colors and styles are unique for each model, and several
#                models can be plotted at once.
#
###############################################################################

import os
import sys
import numpy as np
import math
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
from decimal import Decimal

SETTINGS_DIR = os.environ['USH_DIR']
sys.path.insert(0, os.path.abspath(SETTINGS_DIR))
from settings import Toggle, Templates, Paths, Presets, ModelSpecs, Reference
from plotter import Plotter
from prune_stat_files import prune_data
import plot_util
import df_preprocessing
from check_variables import *

# ================ GLOBALS AND CONSTANTS ================

plotter = Plotter(fig_size=(28.,14.))
plotter.set_up_plots()
toggle = Toggle()
templates = Templates()
paths = Paths()
presets = Presets()
model_colors = ModelSpecs()
reference = Reference()


# =================== FUNCTIONS =========================


def plot_threshold_average(df: pd.DataFrame, logger: logging.Logger, 
                      date_range: tuple, model_list: list, num: int = 0, 
                      level: str = '500', flead='all', thresh: list = ['<20'], 
                      metric_name: str = 'BCRMSE', 
                      y_min_limit: float = -10., y_max_limit: float = 10., 
                      y_lim_lock: bool = False, ylabel: str = '',  
                      date_type: str = 'VALID', date_hours: list = [0,6,12,18], 
                      verif_type: str = 'pres', save_dir: str = '.',
                      requested_var: str = 'HGT', line_type: str = 'SL1L2',
                      dpi: int = 100, confidence_intervals: bool = False,
                      interp_pts: list = [],
                      bs_nrep: int = 5000, bs_method: str = 'MATCHED_PAIRS', 
                      ci_lev: float = .95, bs_min_samp: int = 30,
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
        frange_string = (f'Forecast Hours {flead[0]:02d}'
                         + u'\u2013' + f'{flead[1]:02d}')
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
        e2 = f"Please check settings for forecast leads."
        logger.error(e1)
        logger.error(e2)
        raise ValueError(e1+"\n"+e2)
    if df.empty:
        logger.warning(f"Empty Dataframe. Continuing onto next plot...")
        plt.close(num)
        logger.info("========================================")
        return None
    
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

    requested_thresh_symbol, requested_thresh_letter = list(
        zip(*[plot_util.format_thresh(t) for t in thresh])
    )
    symbol_found = False
    for opt in ['>=', '>', '==','!=','<=', '<']:
        if any(opt in t for t in requested_thresh_symbol):
            if all(opt in t for t in requested_thresh_symbol):
                symbol_found = True
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
    
    group_by = ['MODEL','FCST_THRESH_VALUE']
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
    stat_output = plot_util.calculate_stat(
        logger, df_aggregated, str(metric_name).lower()
    )
    df_aggregated[str(metric_name).upper()] = stat_output[0]
    metric_long_name = stat_output[2]
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
        else:
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

    df_aggregated[str(metric_name).upper()] = (
        df_aggregated[str(metric_name).upper()]
    ).astype(float).tolist()

    df_aggregated = df_aggregated[
        df_aggregated.index.isin(model_list, level='MODEL')
    ]

    pivot_metric = pd.pivot_table(
        df_aggregated, values=str(metric_name).upper(), columns='MODEL', 
        index='FCST_THRESH_VALUE'
    )
    if sample_equalization:
        pivot_counts = pd.pivot_table(
            df_aggregated, values='COUNTS', columns='MODEL',
            index='FCST_THRESH_VALUE'
        )
    pivot_metric = pivot_metric.dropna()
    if confidence_intervals:
        pivot_ci_lower = pd.pivot_table(
            df_aggregated, values=str(metric_name).upper()+'_BLERR', 
            columns='MODEL', index='FCST_THRESH_VALUE'
        )
        pivot_ci_upper = pd.pivot_table(
            df_aggregated, values=str(metric_name).upper()+'_BUERR', 
            columns='MODEL', index='FCST_THRESH_VALUE'
        )
    if pivot_metric.empty:
        print_varname = df['FCST_VAR'].tolist()[0]
        logger.warning(
            f"Could not find (and cannot plot) {metric_name}"
            + f" stats for {print_varname} at any level. "
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
    colors_corrected = False
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
        indices_in_common = list(set.intersection(*map(
            set, 
            [
                pivot_metric.index, 
                pivot_ci_lower.index, 
                pivot_ci_upper.index
            ]
        )))
        pivot_metric = pivot_metric[pivot_metric.index.isin(indices_in_common)]
        pivot_ci_lower = pivot_ci_lower[pivot_ci_lower.index.isin(indices_in_common)]
        pivot_ci_upper = pivot_ci_upper[pivot_ci_upper.index.isin(indices_in_common)]
        if sample_equalization:
            pivot_counts = pivot_counts[pivot_counts.index.isin(indices_in_common)]
    units = df['FCST_UNITS'].tolist()[0]
    #pivot_metric = 
    x_vals = pivot_metric.index.astype(float).tolist()
    if units in reference.unit_conversions:
        x_vals = reference.unit_conversions[units]['formula'](x_vals)
        units = reference.unit_conversions[units]['convert_to']
    if units == '-':
        units = ''
    x_vals_argsort = np.argsort(x_vals)
    x_vals = np.sort(x_vals)
    x_vals_incr = np.diff(x_vals)
    if len(x_vals) > 1:
        min_incr = np.min(x_vals_incr)
    else:
        min_incr = 0
    incrs = [.05,.1,.5,1.,5.,10.,50.,100.,500.,1E3,5E3,1E4,5E4,1E5,5E5]
    incr_idx = np.digitize(min_incr, incrs)
    if incr_idx < 1:
        incr_idx = 1
    incr = incrs[incr_idx-1]
    y_min = y_min_limit
    y_max = y_max_limit
    if np.all([val==1 for val in pivot_metric.count(axis=1)]):
        connect_points = True
    else:
        connect_points = False
    n_mods = 0
    for m in range(len(mod_setting_dicts)):
        if model_list[m] in model_colors.model_alias:
            model_plot_name = (
                model_colors.model_alias[model_list[m]]['plot_name']
            )
        else:
            model_plot_name = model_list[m]
        if str(model_list[m]) not in pivot_metric:
            continue
        y_vals_metric = pivot_metric[str(model_list[m])].values
        y_vals_metric = np.array([y_vals_metric[i] for i in x_vals_argsort])
        y_vals_metric_mean = np.nanmean(y_vals_metric)
        if confidence_intervals:
            y_vals_ci_lower = pivot_ci_lower[
                str(model_list[m])
            ].values
            y_vals_ci_upper = pivot_ci_upper[
                str(model_list[m])
            ].values
        if not y_lim_lock:
            if np.any(y_vals_metric != np.inf):
                y_vals_metric_min = np.nanmin(y_vals_metric[y_vals_metric != np.inf])
                y_vals_metric_max = np.nanmax(y_vals_metric[y_vals_metric != np.inf])
            else:
                y_vals_metric_min = np.nanmin(y_vals_metric)
                y_vals_metric_max = np.nanmax(y_vals_metric)
            if n_mods == 0:
                y_mod_min = y_vals_metric_min
                y_mod_max = y_vals_metric_max
                n_mods+=1
            else:
                if math.isinf(y_mod_min):
                    y_mod_min = y_vals_metric_min
                else:
                    y_mod_min = np.nanmin([y_mod_min, y_vals_metric_min])
                if math.isinf(y_mod_max):
                    y_mod_max = y_vals_metric_max
                else:
                    y_mod_max = np.nanmax([y_mod_max, y_vals_metric_max])
            if (y_vals_metric_min > y_min_limit 
                    and y_vals_metric_min <= y_mod_min):
                y_min = y_vals_metric_min
            if (y_vals_metric_max < y_max_limit 
                    and y_vals_metric_max >= y_mod_max):
                y_max = y_vals_metric_max
        if display_averages:
            if np.abs(y_vals_metric_mean) < 1E4:
                metric_mean_fmt_string = (f'{model_plot_name}'
                                          + f' ({y_vals_metric_mean:.2f})')
            else:
                metric_mean_fmt_string = (f'{model_plot_name}'
                                          + f' ({y_vals_metric_mean:.2E})')
        else:
            metric_mean_fmt_string = f'{model_plot_name}'
        if connect_points:
            x_vals_plot = x_vals[~np.isnan(y_vals_metric)]
            y_vals_plot = y_vals_metric[~np.isnan(y_vals_metric)]
        else:
            x_vals_plot = x_vals
            y_vals_plot = y_vals_metric
        plt.plot(
            x_vals_plot, y_vals_plot, 
            marker='o', c=mod_setting_dicts[m]['color'], mew=2., mec='white', 
            figure=fig, ms=12, ls=mod_setting_dicts[m]['linestyle'], 
            lw=mod_setting_dicts[m]['linewidth'],
            label=f'{metric_mean_fmt_string}'
        )
        if confidence_intervals:
            plt.errorbar(
                x_vals.tolist(), y_vals_metric,
                yerr=[np.abs(y_vals_ci_lower), y_vals_ci_upper],
                fmt='none', ecolor=mod_setting_dicts[m]['color'],
                elinewidth=mod_setting_dicts[m]['linewidth'],
                capsize=10., capthick=mod_setting_dicts[m]['linewidth'],
                alpha=.70, zorder=0
            )
    # Zero line
    plt.axhline(y=0, color='black', linestyle='--', linewidth=1, zorder=0) 
    metrics_with_axline_at_1 = [
        'FBIAS','RSD'
    ]
    if str(metric_name).upper() in metrics_with_axline_at_1:
        plt.axhline(y=1, color='black', linestyle='--', linewidth=1, zorder=0)

    # Configure axis ticks
    if units in reference.unit_conversions:
        x_vals_incr = reference.unit_conversions[units]['formulas'](x_vals)

    xticks_min = np.min(x_vals)
    xticks_max = np.max(x_vals)
    xlim_min = np.floor(xticks_min/incr)*incr
    xlim_max = np.ceil(xticks_max/incr)*incr
    if incr < 1.:
        precision_scale = 100/incr
    else:
        precision_scale = 1.
    xticks = [
        x_val for x_val 
        in np.arange(
            xlim_min*precision_scale, 
            xlim_max*precision_scale+incr*precision_scale, 
            incr*precision_scale
        )
    ]
    xticks=np.divide(xticks,precision_scale)
    xtick_labels = [f'{opt}{xtick}' for xtick in xticks]
    number_of_ticks_dig = [25,50,75,100,125,150,175,200]
    show_xtick_every = np.ceil((
        np.digitize(len(xtick_labels), number_of_ticks_dig) + 2
    )/2.)*2
    xtick_labels_with_blanks = ['' for item in xtick_labels]
    #for i, item in enumerate(xtick_labels[::int(show_xtick_every)]):
    #     xtick_labels_with_blanks[int(show_xtick_every)*i] = item
     
    replace_xticks = [
        xtick for xtick in xticks 
        if np.any([
            np.absolute(xtick-x_val) < incr/2.*show_xtick_every 
            for x_val in x_vals.tolist()
        ])
    ]
    res_xticks = [val for val in xticks if val not in replace_xticks]
    res_xlabels = [
        xtick_labels_with_blanks[v] if val not in replace_xticks
        else '' for v, val in enumerate(xticks)  
    ]
    add_labels = [
        f'{opt}{np.round(x_val)/precision_scale}' for x_val in x_vals*precision_scale
    ]
    xticks_argsort = np.argsort(np.concatenate((xticks, x_vals.tolist())))
    xticks = np.concatenate((
        xticks, x_vals.tolist()
    ))[xticks_argsort]
    xtick_labels_with_blanks = np.concatenate((
        res_xlabels, add_labels
    ))[xticks_argsort]
    #xticks_argsort = np.argsort(x_vals.tolist())
    #xticks = np.array(x_vals.tolist())[xticks_argsort]
    #xtick_labels_with_blanks = np.array(add_labels)[xticks_argsort]
    res_diff = np.diff(
        [xtick for x, xtick in enumerate(xticks) if xtick_labels_with_blanks[x]]
    )
    arg_xtick_labels = [
        i for i, lab in enumerate(xtick_labels_with_blanks) if lab
    ]
    for i, d in enumerate(res_diff):
        if d < (incr/2.*show_xtick_every):
            xtick_labels_with_blanks[arg_xtick_labels[i+1]] = ''

    x_buffer_size = .015
    ax.set_xlim(
        xlim_min-incr*x_buffer_size, xlim_max+incr*x_buffer_size
    )
    y_range_categories = np.array([
        [np.power(10.,y), 2.*np.power(10.,y)] 
        for y in [-5,-4,-3,-2,-1,0,1,2,3,4,5]
    ]).flatten()
    round_to_nearest_categories = y_range_categories/20.
    y_range = y_max-y_min
    round_to_nearest =  round_to_nearest_categories[
        np.digitize(y_range, y_range_categories[:-1])
    ]
    ylim_min = np.floor(y_min/round_to_nearest)*round_to_nearest
    ylim_max = np.ceil(y_max/round_to_nearest)*round_to_nearest
    if len(str(ylim_min)) > 5 and np.abs(ylim_min) < 1.:
        ylim_min = float(
            np.format_float_scientific(ylim_min, unique=False, precision=3)
        )
    yticks = np.arange(ylim_min, ylim_max+round_to_nearest, round_to_nearest)
    var_long_name_key = df['FCST_VAR'].tolist()[0]
    if str(var_long_name_key).upper() == 'HGT':
        if str(df['OBS_VAR'].tolist()[0]).upper() in ['CEILING']:
            var_long_name_key = 'HGTCLDCEIL'
        elif str(df['OBS_VAR'].tolist()[0]).upper() in ['HPBL']:
            var_long_name_key = 'HPBL'
    var_long_name = variable_translator[var_long_name_key]
    metrics_using_var_units = [
        'BCRMSE','RMSE','BIAS','ME','FBAR','OBAR','MAE','FBAR_OBAR',
        'SPEED_ERR','DIR_ERR','RMSVE','VDIFF_SPEED','VDIF_DIR',
        'FBAR_OBAR_SPEED','FBAR_OBAR_DIR','FBAR_SPEED','FBAR_DIR'
    ]
    if str(metric_name).upper() in metrics_using_var_units:
        if units:
            ylabel = f'{var_long_name} ({units})'
        else:
            ylabel = f'{var_long_name} (unitless)'
    else:
        ylabel = f'{metric_long_name}'
    ax.set_ylim(ylim_min, ylim_max)
    ax.set_ylabel(ylabel)
    if units:
        ax.set_xlabel(f'Forecast Threshold ({units})') 
    else:
        ax.set_xlabel(f'Forecast Threshold (unitless)')
    ax.set_xticklabels(xtick_labels_with_blanks)
    ax.set_yticks(yticks)
    ax.set_xticks(xticks)
    ax.tick_params(
        labelleft=True, labelright=False, labelbottom=True, labeltop=False
    )
    ax.tick_params(
        left=False, labelleft=False, labelright=False, labelbottom=False, 
        labeltop=False, which='minor', axis='y', pad=15
    )
    majticks = [i for i, item in enumerate(xtick_labels_with_blanks) if item]
    for mt in majticks:
        ax.xaxis.get_major_ticks()[mt].tick1line.set_markersize(8)
    ax.legend(
        loc='upper center', fontsize=15, framealpha=1, 
        bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=True, numpoints=2, 
        borderpad=.8, labelspacing=2., columnspacing=3., handlelength=3., 
        handletextpad=.4, borderaxespad=.5) 
    fig.subplots_adjust(bottom=.15, wspace=0, hspace=0)
    fig.subplots_adjust(top=0.85)
    ax.grid(
        visible=True, which='major', axis='both', alpha=.5, linestyle='--', 
        linewidth=.5, zorder=0
    )

    if sample_equalization:
        counts = pivot_counts.mean(axis=1, skipna=True).fillna('')
        for count, xval in zip(counts, x_vals.tolist()):
            if not isinstance(count, str):
                count = str(int(count))
            ax.annotate(
                f'{count}', xy=(xval,1.),
                xycoords=('data','axes fraction'), xytext=(0,18),
                textcoords='offset points', va='top', fontsize=16,
                color='dimgrey', ha='center'
            )
        ax.annotate(
            '#SAMPLES', xy=(0.,1.), xycoords='axes fraction',
            xytext=(-50, 21), textcoords='offset points', va='top',
            fontsize=11, color='dimgrey', ha='center'
        )
        #fig.subplots_adjust(top=.9)
        fig.subplots_adjust(top=.85)

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
    metric_string = metric_long_name
    if str(level).upper() in ['CEILING', 'TOTAL', 'PBL']:
        if str(level).upper() == 'CEILING':
            level_string = ''
            level_savename = ''
        elif str(level).upper() == 'TOTAL':
            level_string = 'Total '
            level_savename = ''
        elif str(level).upper() == 'PBL':
            level_string = ''
            level_savename = ''
    elif str(verif_type).lower() in ['pres', 'upper_air', 'raob'] or 'P' in str(level):
        if 'P' in str(level):
            if str(level).upper() == 'P90-0':
                level_string = f'Mixed-Layer '
                level_savename = f'ML'
            else:
                level_num = level.replace('P', '')
                level_string = f'{level_num} hPa '
                level_savename = f'{level_num}MB_'
        elif str(level).upper() == 'L0':
            level_string = f'Surface-Based '
            level_savename = f'SB'
        else:
            level_string = ''
            level_savename = ''
    elif str(verif_type).lower() in ['sfc', 'conus_sfc', 'polar_sfc', 'mrms','metar']:
        if 'Z' in str(level):
            if str(level).upper() == 'Z0':
                if str(var_long_name_key).upper() in ['MLSP', 'MSLET', 'MSLMA', 'PRMSL']:
                    level_string = ''
                    level_savename = ''
                else:
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
    title1 = f'{metric_string}'
    if interp_pts and '' not in interp_pts:
        title1+=f' {interp_pts_string}'
    if units:
        title2 = f'{level_string}{var_long_name} ({units}), {domain_string}'
    else:
        title2 = f'{level_string}{var_long_name} (unitless), {domain_string}'
    title3 = (f'{str(date_type).capitalize()} {date_hours_string} '
              + f'{date_start_string} to {date_end_string}, {frange_string}')
    title_center = '\n'.join([title1, title2, title3])
    if sample_equalization:
        title_pad=40
    else:
        title_pad=None
    ax.set_title(title_center, loc=plotter.title_loc, pad=title_pad) 
    logger.info("... Plotting complete.")

    # Logos
    if plot_logo_left:
        if os.path.exists(path_logo_left):
            left_logo_arr = mpimg.imread(path_logo_left)
            left_image_box = OffsetImage(left_logo_arr, zoom=zoom_logo_left)
            ab_left = AnnotationBbox(
                left_image_box, xy=(0.,1.), xycoords='axes fraction',
                xybox=(0, 20), boxcoords='offset points', frameon = False,
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
            right_image_box = OffsetImage(right_logo_arr, zoom=zoom_logo_right)
            ab_right = AnnotationBbox(
                right_image_box, xy=(1.,1.), xycoords='axes fraction',
                xybox=(0, 20), boxcoords='offset points', frameon = False,
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
    save_name = (f'threshold_average_regional_'
                 + f'{str(domain).lower()}_{str(date_type).lower()}_'
                 + f'{str(date_hours_savename).lower()}_'
                 + f'{str(level_savename).lower()}'
                 + f'{str(var_savename).lower()}_{str(metric_name).lower()}')
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
    logger.debug(f"INTERP_PNTS: {INTERP_PNTS if INTERP_PNTS else 'No interpolation points'}")

    logger.debug('----------------------------------------')
    logger.debug(f"Advanced settings (configurable in {SETTINGS_DIR}/settings.py)")
    logger.debug(f"Y_MIN_LIMIT: {Y_MIN_LIMIT}")
    logger.debug(f"Y_MAX_LIMIT: {Y_MAX_LIMIT}")
    logger.debug(f"Y_LIM_LOCK: {Y_LIM_LOCK}")
    logger.debug(f"X_MIN_LIMIT: Ignored for series by threshold")
    logger.debug(f"X_MAX_LIMIT: Ignored for series by threshold")
    logger.debug(f"X_LIM_LOCK: Ignored for series by threshold")
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
                     + f" {requested_var}/{fcst_level}")
                logger.warning(e)
                logger.warning("Continuing ...")
                continue
            for domain in DOMAINS:
                if str(domain) not in case_specs['vx_mask_list']:
                    e = (f"The requested domain is not valid for the requested"
                         + f" case type ({VERIF_CASETYPE}) and line_type"
                         + f" ({LINE_TYPE}): {domain}")
                    logger.warning(e)
                    logger.warning("Continuing ...")
                    continue
                df = df_preprocessing.get_preprocessed_data(
                    logger, STATS_DIR, PRUNE_DIR, OUTPUT_BASE_TEMPLATE, VERIF_CASE, VERIF_TYPE, 
                    LINE_TYPE, DATE_TYPE, date_range, EVAL_PERIOD, date_hours, 
                    FLEADS, requested_var, fcst_var_names, obs_var_names, MODELS, 
                    domain, INTERP, MET_VERSION, clear_prune_dir
                )
                if df is None:
                    continue
                for metric in metrics:
                    if (str(metric).lower()
                            not in case_specs['plot_stats_list']
                            .replace(' ','').split(',')):
                        e = (f"The requested metric is not valid for the"
                             + f" requested case type ({VERIF_CASETYPE}) and"
                             + f" line_type ({LINE_TYPE}): {metric}")
                        logger.warning(e)
                        logger.warning("Continuing ...")
                        continue
                    df_metric = df
                    plot_threshold_average(
                        df_metric, logger, date_range, MODELS, num=num, 
                        flead=FLEADS, level=fcst_level, thresh=fcst_thresh, 
                        metric_name=metric, date_type=DATE_TYPE, 
                        y_min_limit=Y_MIN_LIMIT, y_max_limit=Y_MAX_LIMIT, 
                        y_lim_lock=Y_LIM_LOCK, ylabel='Metric (unitless)', 
                        line_type=LINE_TYPE, verif_type=VERIF_TYPE, 
                        date_hours=date_hours, save_dir=SAVE_DIR, 
                        eval_period=EVAL_PERIOD,
                        display_averages=display_averages, 
                        save_header=URL_HEADER, plot_group=plot_group,
                        confidence_intervals=CONFIDENCE_INTERVALS, 
                        interp_pts=INTERP_PNTS,
                        bs_nrep=bs_nrep, bs_method=bs_method, ci_lev=ci_lev,
                        bs_min_samp=bs_min_samp,
                        sample_equalization=sample_equalization,
                        plot_logo_left=plot_logo_left,
                        plot_logo_right=plot_logo_right,
                        path_logo_left=path_logo_left,
                        path_logo_right=path_logo_right,
                        zoom_logo_left=zoom_logo_left,
                        zoom_logo_right=zoom_logo_right
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
    METRICS = check_STATS(os.environ['STATS']).replace(' ','').split(',')

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
    FCST_LEVELS = [str(level) for level in FCST_LEVELS]
    OBS_LEVELS = [str(level) for level in OBS_LEVELS]
    CONFIDENCE_INTERVALS = str(CONFIDENCE_INTERVALS).lower() in [
        'true', '1', 't', 'y', 'yes'
    ]
    main()
