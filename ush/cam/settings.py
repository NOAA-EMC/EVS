#!/usr/bin/env python3
import os
from datetime import datetime, timedelta as td
import numpy as np

class Toggle():
    def __init__(self):
        
        '''
        Dictionary with values that can be adjusted by the user to change a
        particular plot setting.  
        '''
        self.plot_settings = {
            'x_min_limit': -9999., # x-axis values will not subceed this value
            'x_max_limit': 9999., # x-axis values will not exceed this value
            'x_lim_lock': False, # lock the x-axis lower an upper limits to x_min_limit and x_max_limit, respectively
            'y_min_limit': -9999.,
            'y_max_limit': 9999.,
            'y_lim_lock': False,
            'ci_lev': .95, # confidence level, as a float > 0. and < 1.
            'bs_nrep': 5000, # number of bootstrap repetitions when confidence intervals are computed
            'bs_method': 'FORECASTS', # bootstrap method. 'FORECASTS' bootstraps the lines in the stat files, 'MATCHED_PAIRS' bootstraps the f-o matched pairs
            'bs_min_samp': 30, # Minimum number of samples allowed for boostrapping to performed (if there are fewer samples, no confidence intervals)
            'display_averages': False, # display mean statistic for each model, averaged across the dimension of the independent variable
            'sample_equalization': True, # equalize samples along each value of the independent variable where data exist
            'keep_shared_events_only': False, # functional for time_series only.
            'clear_prune_directory': True, # remove the intermediate directory created to store pruned data files temporarily
            'plot_logo_left': True,
            'plot_logo_right': True,
            'zoom_logo_left': 1.0, 
            'zoom_logo_right': 1.0,
            'delete_intermed_data': True # whether of not to delete DataFrame rows if, for any model, rows include NaN (currently only used in lead_average.py)
        }

class Templates():
    def __init__(self):
        
        '''
        Custom template used to find .stat files in OUTPUT_BASE_DIR.
        
        output_base_template must be a string. Use curly braces {} to enclose variable
        names that will be substituted with the appropriate value according to
        the plotting request.   

        Current possible variable names:    Example substituted values:
        ================================    ===========================
        RUN_CASE                            grid2obs
        RUN_TYPE                            conus_sfc
        LINE_TYPE                           sl1l2
        VX_MASK                             conus
        FCST_VAR_NAME                       VIS
        VAR_NAME                            VISsfc
        MODEL                               HRRR
        EVAL_PERIOD                         PAST30DAYS
        valid?fmt=%Y%m or VALID?fmt=%Y%m    202206

        Additionally, variable names may have the _LOWER or _UPPER suffix to 
        substitute a lower- or upper-case conversion of the desired string.

        Finally, use asterisk * as a wildcard to match with and use data from
        several .stat files, or for portions of the .stat file name that vary but 
        are inconsequential.

        Example: 
        "{RUN_CASE_LOWER}/{MODEL}/{valid?fmt=%Y%m}/{MODEL}_{valid?fmt=%Y%m%d}*"
        '''
        self.output_base_template = "{MODEL}.{valid?fmt=%Y%m%d}/evs.stats.{MODEL}.atmos.grid2obs.v{valid?fmt=%Y%m%d}*"

class Paths():
    def __init__(self):
        '''
        Custom paths to left and right logos. 
        
        Referenced if plot_logo_left and plot_logo_right, in the Toggle class,
        are set to True
        '''
        self.logo_left_path = f"{os.environ['FIXevs']}/logos/noaa.png"
        self.logo_right_path = f"{os.environ['FIXevs']}/logos/nws.png"

class Presets():
    def __init__(self):

        self.level_presets = {
            'all': 'P1000,P925,P850,P700,P500,P400,P300,P200,P150,P100,P50',
            'ltrop': 'P1000,P950,P900,P850,P800,P750,P700,P650,P600,P550,P500',
            'strat': 'P100,P75,P50,P30,P20,P10',
            'trop': 'P1000,P900,P850,P700,P600,P500,P400,P300,P200,P100',
            'utrop': 'P500,P450,P400,P350,P300,P250,P200,P150,P100'
        }

        '''
        Evaluation periods that are requested regularly can be defined here 
        and then requested as the 'EVAL_PERIOD' variable in the plotting 
        configuration file.
        
        Additional presets can be added, but must look like this:
        'NAME_OF_PRESET': {
            'valid_beg': 'YYYYmmdd',
            'valid_end': 'YYYYmmdd',
            'init_beg': 'YYYYmmdd',
            'init_end': 'YYYYmmdd',
        },

        Dates must be in YYYYmmdd format.  A date can be written directly as
        a string, or may be defined using python's built-in datetime and/or 
        timedelta (use td) libraries, which are already imported.  Check 
        the online documentation to learn how to use these libraries.
        '''
        self.date_presets = {
            'LAST90DAYS': {
                'valid_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=90)
                ).strftime('%Y%m%d'),
                'valid_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d'),
                'init_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=90)
                    ).strftime('%Y%m%d'),
                'init_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d')
            },
            'LAST31DAYS': {
                'valid_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=31)
                ).strftime('%Y%m%d'),
                'valid_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d'),
                'init_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=31)
                    ).strftime('%Y%m%d'),
                'init_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d')
            },
            'LAST30DAYS': {
                'valid_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=30)
                ).strftime('%Y%m%d'),
                'valid_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d'),
                'init_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=30)
                    ).strftime('%Y%m%d'),
                'init_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d')
            },
            'LAST7DAYS': {
                'valid_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=7)
                ).strftime('%Y%m%d'),
                'valid_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d'),
                'init_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=7)
                    ).strftime('%Y%m%d'),
                'init_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d')
            },
            'LAST3DAYS': {
                'valid_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=3)
                ).strftime('%Y%m%d'),
                'valid_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d'),
                'init_beg': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=3)
                    ).strftime('%Y%m%d'),
                'init_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                ).strftime('%Y%m%d')
            },
            'PDYM1': {
                'valid_beg': '',
                'valid_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                    ).strftime('%Y%m%d'),
                'init_beg': '',
                'init_end': (
                    datetime.strptime(os.environ['VDATE'], '%Y%m%d')-td(days=1)
                    ).strftime('%Y%m%d'),
            },
            '2020': {
                'valid_beg': '20200101',
                'valid_end': '20201231',
                'init_beg': '20200101',
                'init_end': '20201231'
            },
            '2021': {
                'valid_beg': '20210101',
                'valid_end': '20211231',
                'init_beg': '20210101',
                'init_end': '20211231'
            },
            '2022': {
                'valid_beg': '20220101',
                'valid_end': '20221231',
                'init_beg': '20220101',
                'init_end': '20221231'
            },
        }
            
class ModelSpecs():
    def __init__(self):
        
        '''
        The model_alias dictionary defines the appropriate key to be used
        when finding settings and the long name for certain requested models 
        that may have several possible names in MET .stat files and file names.  
        
        e.g., AKARW and CONUSARW, although they are different, may use the same 
        line/marker settings and the same long name on plots, and so both can 
        be defined here as aliases of the same model settings, if desired.
        '''
        self.model_alias = {
            'ARW': {
                'settings_key':'HRW_ARW', 
                'plot_name':'HiResW ARW'
            },
            'ARW2': {
                'settings_key':'HRW_ARW2', 
                'plot_name':'HiResW ARW2'
            },
            'FV3': {
                'settings_key':'HRW_FV3', 
                'plot_name':'HiResW FV3'
            },
            'NMMB': {
                'settings_key':'HRW_NMMB', 
                'plot_name':'HiResW NMMB'
            },
            'AKARW': {
                'settings_key':'HRW_ARW', 
                'plot_name':'HiResW ARW'
            },
            'AKARW2': {
                'settings_key':'HRW_ARW2', 
                'plot_name':'HiResW ARW2'
            },
            'AKFV3': {
                'settings_key':'HRW_FV3', 
                'plot_name':'HiResW FV3'
            },
            'AKNEST': {
                'settings_key':'NAM_NEST', 
                'plot_name':'NAM Nest'
            },
            'AKNMMB': {
                'settings_key':'HRW_NMMB', 
                'plot_name':'HiResW NMMB'
            },
            'CONUSARW': {
                'settings_key':'HRW_ARW', 
                'plot_name':'HiResW ARW'
            },
            'CONUSARW2': {
                'settings_key':'HRW_ARW2', 
                'plot_name':'HiResW ARW2'
            },
            'CONUSFV3': {
                'settings_key':'HRW_FV3', 
                'plot_name':'HiResW FV3'
            },
            'CONUSNEST': {
                'settings_key':'NAM_NEST', 
                'plot_name':'NAM Nest'
            },
            'CONUSNMMB': {
                'settings_key':'HRW_NMMB', 
                'plot_name':'HiResW NMMB'
            },
            'hireswarw': {
                'settings_key':'HRW_ARW', 
                'plot_name':'HiResW ARW'
            },
            'hireswarwmem2': {
                'settings_key':'HRW_ARW2', 
                'plot_name':'HiResW ARW2'
            },
            'hireswfv3': {
                'settings_key':'HRW_FV3', 
                'plot_name':'HiResW FV3'
            },
            'HREF_MEAN':{
                'settings_key':'HREF_MEAN', 
                'plot_name':'HREF Mean'
            },
            'HREF_AVRG':{
                'settings_key':'HREF_AVRG', 
                'plot_name':'HREF Average of MEAN and PMMN'
            },
            'HREF_LPMM':{
                'settings_key':'HREF_LPMM', 
                'plot_name':'HREF Local Probability-Matched Mean'
            },
            'HREF_PMMN':{
                'settings_key':'HREF_PMMN', 
                'plot_name':'HREF Probability-Matched Mean'
            },
            'HREF_PROB':{
                'settings_key':'HREF_PROB', 
                'plot_name':'HREF Probability'
            },
            'HREFX_MEAN':{
                'settings_key':'HREFX_MEAN', 
                'plot_name':'HREF-X Mean'
            },
            'CONUSHREF_MEAN':{
                'settings_key':'HREF_MEAN', 
                'plot_name':'HREF Mean'
            },
            'CONUSHREF_AVRG':{
                'settings_key':'HREF_AVRG', 
                'plot_name':'HREF Average of MEAN and PMMN'
            },
            'CONUSHREF_LPMM':{
                'settings_key':'HREF_LPMM', 
                'plot_name':'HREF Local Probability-Matched Mean'
            },
            'CONUSHREF_PMMN':{
                'settings_key':'HREF_PMMN', 
                'plot_name':'HREF Probability-Matched Mean'
            },
            'CONUSHREF_PROB':{
                'settings_key':'HREF_PROB', 
                'plot_name':'HREF Probability'
            },
            'CONUSHREFX_MEAN':{
                'settings_key':'HREFX_MEAN', 
                'plot_name':'HREF-X Mean'
            },
            'AKHREF_MEAN':{
                'settings_key':'HREF_MEAN', 
                'plot_name':'HREF Mean'
            },
            'AKHREF_AVRG':{
                'settings_key':'HREF_AVRG', 
                'plot_name':'HREF Average of MEAN and PMMN'
            },
            'AKHREF_LPMM':{
                'settings_key':'HREF_LPMM', 
                'plot_name':'HREF Local Probability-Matched Mean'
            },
            'AKHREF_PMMN':{
                'settings_key':'HREF_PMMN', 
                'plot_name':'HREF Probability-Matched Mean'
            },
            'AKHREF_PROB':{
                'settings_key':'HREF_PROB', 
                'plot_name':'HREF Probability'
            },
            'AKHREFX_MEAN':{
                'settings_key':'HREFX_MEAN', 
                'plot_name':'HREF-X Mean'
            },
            'PRHREF_MEAN':{
                'settings_key':'HREF_MEAN', 
                'plot_name':'HREF Mean'
            },
            'PRHREF_AVRG':{
                'settings_key':'HREF_AVRG', 
                'plot_name':'HREF Average of MEAN and PMMN'
            },
            'PRHREF_LPMM':{
                'settings_key':'HREF_LPMM', 
                'plot_name':'HREF Local Probability-Matched Mean'
            },
            'PRHREF_PMMN':{
                'settings_key':'HREF_PMMN', 
                'plot_name':'HREF Probability-Matched Mean'
            },
            'PRHREF_PROB':{
                'settings_key':'HREF_PROB', 
                'plot_name':'HREF Probability'
            },
            'PRHREFX_MEAN':{
                'settings_key':'HREFX_MEAN', 
                'plot_name':'HREF-X Mean'
            },
            'HIHREF_MEAN':{
                'settings_key':'HREF_MEAN', 
                'plot_name':'HREF Mean'
            },
            'HIHREF_AVRG':{
                'settings_key':'HREF_AVRG', 
                'plot_name':'HREF Average of MEAN and PMMN'
            },
            'HIHREF_LPMM':{
                'settings_key':'HREF_LPMM', 
                'plot_name':'HREF Local Probability-Matched Mean'
            },
            'HIHREF_PMMN':{
                'settings_key':'HREF_PMMN', 
                'plot_name':'HREF Probability-Matched Mean'
            },
            'HIHREF_PROB':{
                'settings_key':'HREF_PROB', 
                'plot_name':'HREF Probability'
            },
            'HIHREFX_MEAN':{
                'settings_key':'HREFX_MEAN', 
                'plot_name':'HREF-X Mean'
            },
            'NARRE_MEAN':{
                'settings_key':'NARRE_MEAN', 
                'plot_name':'NARRE Mean'
            },
            'HIARW': {
                'settings_key':'HRW_ARW', 
                'plot_name':'HiResW ARW'
            },
            'HIARW2': {
                'settings_key':'HRW_ARW2', 
                'plot_name':'HiResW ARW2'
            },
            'HIFV3': {
                'settings_key':'HRW_FV3', 
                'plot_name':'HiResW FV3'
            },
            'HINMMB': {
                'settings_key':'HRW_NMMB', 
                'plot_name':'HiResW NMMB'
            },
            'HAWAIINEST': {
                'settings_key':'NAM_NEST', 
                'plot_name':'NAM Nest'
            },
            'PRARW': {
                'settings_key':'HRW_ARW', 
                'plot_name':'HiResW ARW'
            },
            'PRARW2': {
                'settings_key':'HRW_ARW2', 
                'plot_name':'HiResW ARW2'
            },
            'PRFV3': {
                'settings_key':'HRW_FV3', 
                'plot_name':'HiResW FV3'
            },
            'PRNMMB': {
                'settings_key':'HRW_NMMB', 
                'plot_name':'HiResW NMMB'
            },
            'PRICONEST': {
                'settings_key':'NAM_NEST', 
                'plot_name':'NAM Nest'
            },
            'FV3LAMDA': {
                'settings_key':'LAMDA', 
                'plot_name':'FV3LAM-DA'
            },
            'FV3LAMDAX': {
                'settings_key':'LAMDAX', 
                'plot_name':'FV3LAM-DAX'
            },
            'FV3LAMDAXAK': {
                'settings_key':'LAMDAX', 
                'plot_name':'FV3LAM-DAX'
            },
            'FV3LAMDAXHI': {
                'settings_key':'LAMDAX', 
                'plot_name':'FV3LAM-DAX'
            },
            'FV3LAMDAXNA': {
                'settings_key':'LAMDAX', 
                'plot_name':'FV3LAM-DAX'
            },
            'FV3LAMDAXPR': {
                'settings_key':'LAMDAX', 
                'plot_name':'FV3LAM-DAX'
            },
            'FV3LAM': {
                'settings_key':'LAM', 
                'plot_name':'FV3LAM'
            },
            'FV3LAMAK': {
                'settings_key':'LAM', 
                'plot_name':'FV3LAM'
            },
            'FV3LAMHI': {
                'settings_key':'LAM', 
                'plot_name':'FV3LAM'
            },
            'FV3LAMNA': {
                'settings_key':'LAM', 
                'plot_name':'FV3LAM'
            },
            'FV3LAMPR': {
                'settings_key':'LAM', 
                'plot_name':'FV3LAM'
            },
            'FV3LAMX': {
                'settings_key':'LAMX', 
                'plot_name':'FV3LAM-X'
            },
            'FV3LAMXAK': {
                'settings_key':'LAMX', 
                'plot_name':'FV3LAM-X'
            },
            'FV3LAMXHI': {
                'settings_key':'LAMX', 
                'plot_name':'FV3LAM-X'
            },
            'FV3LAMXNA': {
                'settings_key':'LAMX', 
                'plot_name':'FV3LAM-X'
            },
            'FV3LAMXPR': {
                'settings_key':'LAMX', 
                'plot_name':'FV3LAM-X'
            },
            'NAM_NEST': {
                'settings_key':'NAM_NEST', 
                'plot_name':'NAM Nest'
            },
            'NAM_FIREWXNEST': {
                'settings_key':'NAM_NEST', 
                'plot_name':'NAM Fire Wx Nest'
            },
            'namnest': {
                'settings_key':'NAM_NEST', 
                'plot_name':'NAM Nest'
            },
            'HRRRAK': {
                'settings_key':'HRRR', 
                'plot_name':'HRRR'
            },
            'hrrr': {
                'settings_key':'HRRR', 
                'plot_name':'HRRR'
            },
            'NAMNA': {
                'settings_key':'NAM', 
                'plot_name':'NAM'
            },
            'RAPAK': {
                'settings_key':'RAP', 
                'plot_name':'RAP'
            },
            'RAPNA': {
                'settings_key':'RAP', 
                'plot_name':'RAP'
            },
            'RRFS_A': {
                'settings_key':'RRFS_A', 
                'plot_name':'RRFS-A'
            },
            'RRFS_A_AK': {
                'settings_key':'RRFS_A', 
                'plot_name':'RRFS-A Alaska'
            },
            'RRFS_A_PR': {
                'settings_key':'RRFS_A', 
                'plot_name':'RRFS-A Puerto Rico'
            },
            'RRFS_A_HI': {
                'settings_key':'RRFS_A', 
                'plot_name':'RRFS-A Hawaii'
            },
            'RRFS_A_CONUS': {
                'settings_key':'RRFS_A', 
                'plot_name':'RRFS-A CONUS'
            },
            'RRFS_A_NACONUS': {
                'settings_key':'RRFS_A_NA', 
                'plot_name':'RRFS-A N. America'
            },
            'mrms': {
                'settings_key':'MRMS', 
                'plot_name':'MRMS'
            },
            'ccpa': {
                'settings_key':'CCPA', 
                'plot_name':'CCPA'
            },
            'wafs': {
                'settings_key':'WAFS', 
                'plot_name':'WAFS'
            }
        }

        '''
        model_settings defines the line/marker specifications according
        to the model being plotted.  See the online documentation for python's
        matplotlib library to learn the possible specifications.
        
        Some keys, however, represent generic model settings (model1, model2, etc..).  
        These generic settings are used if a model is requested in the configuration 
        file but not already included in this list, in which case generic settings 
        are chosen that don't match the settings for any other model already included 
        in the plot.
        '''
        self.model_settings = {
            'model1': {'color': '#000000',
                       'marker': 'o', 'markersize': 12,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model2': {'color': '#fb2020',
                       'marker': '^', 'markersize': 14,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model3': {'color': '#1e3cff',
                       'marker': 'X', 'markersize': 14,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model4': {'color': '#00dc00',
                       'marker': 'P', 'markersize': 14,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model5': {'color': '#e69f00',
                       'marker': 'o', 'markersize': 12,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model6': {'color': '#56b4e9',
                       'marker': 'o', 'markersize': 12,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model7': {'color': '#696969',
                       'marker': 's', 'markersize': 12,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model8': {'color': '#8400c8',
                       'marker': 'D', 'markersize': 12,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model9': {'color': '#d269c1',
                       'marker': 's', 'markersize': 12,
                       'linestyle': 'solid', 'linewidth': 3.},
            'model10': {'color': '#f0e492',
                        'marker': 'o', 'markersize': 12,
                        'linestyle': 'solid', 'linewidth': 3.},
            'obs': {'color': '#aaaaaa',
                    'marker': 'None', 'markersize': 0,
                    'linestyle': 'solid', 'linewidth': 4.},
            'LAM': {'color': '#00dc00',
                      'marker': 'o', 'markersize': 12,
                      'linestyle': 'solid', 'linewidth': 3.},
            'LAMDA': {'color': '#8400c8',
                      'marker': 'o', 'markersize': 12,
                      'linestyle': 'solid', 'linewidth': 3.},
            'LAMX': {'color': '#00dc00',
                       'marker': 'P', 'markersize': 14,
                       'linestyle': 'dashed', 'linewidth': 3.},
            'LAMDAX': {'color': '#8400c8',
                       'marker': 'P', 'markersize': 14,
                       'linestyle': 'dashed', 'linewidth': 3.},
            'HWRF': {'color': '#00dc00',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HMON': {'color': '#8400c8',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HRW_ARW': {'color': '#00dc00',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HRW_ARW2': {'color': '#e69f00',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HRW_FV3': {'color': '#56b4e9',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HREF_MEAN': {'color': '#000000',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HREF_AVRG': {'color': '#696969',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HREF_PMMN': {'color': '#8400c8',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HREF_LPMM': {'color': '#d269c1',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'HREFX_MEAN': {'color': '#000000',
                     'marker': 'P', 'markersize': 14,
                     'linestyle': 'dashed', 'linewidth': 3.},
            'HRRR': {'color': '#fb2020',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'NAM': {'color': '#1e3cff',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'NAM_NEST': {'color': '#1e3cff',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'RRFS_A': {'color': '#00dc00',
                      'marker': 'o', 'markersize': 12,
                      'linestyle': 'solid', 'linewidth': 3.},
            'RRFS_A_NA': {'color': '#00dc00',
                      'marker': 'P', 'markersize': 14,
                      'linestyle': 'dashed', 'linewidth': 3.},
            'GFS': {'color': '#000000',
                    'marker': 'o', 'markersize': 12,
                    'linestyle': 'solid', 'linewidth': 5.},
            'GFS_DASHED': {'color': '#000000',
                           'marker': 'o', 'markersize': 12,
                           'linestyle': 'dashed', 'linewidth': 5.},
            'GEFS': {'color': '#000000',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 5.},
            'NARRE_MEAN': {'color': '#000000',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 5.},
            'EC': {'color': '#fb2020',
                   'marker': 'o', 'markersize': 12,
                   'linestyle': 'solid', 'linewidth': 3.},
            'CMC': {'color': '#1e3cff',
                    'marker': 'o', 'markersize': 12,
                    'linestyle': 'solid', 'linewidth': 3.},
            'CTCX': {'color': '#56b4e9',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.},
            'OFCL': {'color': '#696969',
                     'marker': 'o', 'markersize': 12,
                     'linestyle': 'solid', 'linewidth': 3.}
        }    
      
    def get_color_dict(self, name):
        color_dict = self.model_settings[name]
        return color_dict

class Reference():
    def __init__(self):
        '''
        Plotting jobs for the variables in this list will attempt to replace
        threshold labels with category labels according to the sub-dictionary,
        if the key of the sub-dictionary matches the value of 'FCST_VAR_NAME'
        in the input stat file(s).  Currently only functional for mctc 
        performance diagrams.
        '''
        self.thresh_categ_translator = {
            'PTYPE': {
                '1': 'rain',
                '2': 'snow',
                '3': 'freezing rain',
                '4': 'ice pellets',
            }
        }

        '''
        The plotting scripts will convert MET units if they are listed below.
        The name of the unit must match one of the keys in the 
        unit_conversions dictionary.  The name of the new unit will become the
        value of the 'convert_to' key, and if necessary, the data and axis 
        labels will be converted according to the value of the 'formula' key.
        Formulas are defined as regular functions in the formulas() subclass 
        of the Reference() class (i.e., below...)
        '''
        self.unit_conversions = {
            'kg/m^2': {
                'convert_to': 'in',
                'formula': self.formulas.mm_to_in
            },
            'K': {
                'convert_to': 'F',
                'formula': self.formulas.K_to_F
            },
            'C': {
                'convert_to': 'F',
                'formula': self.formulas.C_to_F
            },
            'm/s': {
                'convert_to': 'kt',
                'formula': self.formulas.mps_to_kt
            },
            'gpm': {
                'convert_to': 'kft',
                'formula': self.formulas.gpm_to_kft
            },
            'm': {
                'convert_to': 'mi',
                'formula': self.formulas.m_to_mi
            },
        }

        '''
        Given a var_name, which is used to find the desired forecast field 
        in the MET .stat files, the plotting scripts will print the long name 
        of the associated forecast field according to this dictionary.  Add 
        keys and values, not forgetting to include a comma at the end of any 
        new lines.
        '''
        self.variable_translator = {'TMP': 'Temperature',
                                    'TMP_Z0_mean': 'Temperature',
                                    'HGT': 'Geopotential Height',
                                    'HGT_WV1_0-3': ('Geopotential Height:' 
                                                    + ' Waves 0-3'),
                                    'HGT_WV1_4-9': ('Geopotential Height:'
                                                    + ' Waves 4-9'),
                                    'HGT_WV1_10-20': ('Geopotential Height:'
                                                      + ' Waves 10-20'),
                                    'HGT_WV1_0-20': ('Geopotential Height:'
                                                     + ' Waves 0-20'),
                                    'RH': 'Relative Humidity',
                                    'SPFH': 'Specific Humidity',
                                    'DPT': 'Dewpoint Temperature',
                                    'TDO': 'Observed Dew Point',
                                    'UGRD': 'Zonal Wind Speed',
                                    'VGRD': 'Meridional Wind Speed',
                                    'UGRD_VGRD': 'Vector Wind',
                                    'WIND': 'Wind Speed',
                                    'GUST': 'Wind Gust',
                                    'GUSTsfc': 'Wind Gust',
                                    'CAPE': ('Convective Available Potential'
                                             + ' Energy'),
                                    'SBCAPE': ('Surface-Based Convective Available Potential'
                                             + ' Energy'),
                                    'MLCAPE': ('Mixed-Layer Convective Available Potential'
                                             + ' Energy'),
                                    'PRES': 'Pressure',
                                    'PRMSL': 'Pressure Reduced to MSL',
                                    'MSLMA': 'Mean Sea Level Pressure',
                                    'MSLET': 'Mean Sea Level Pressure',
                                    'MSLP': 'Mean Sea Level Pressure',
                                    'O3MR': 'Ozone Mixing Ratio',
                                    'TOZNE': 'Total Ozone',
                                    'OZCON1': 'OZCON1',
                                    'HPBL': 'Planetary Boundary Layer Height',
                                    'PBL': 'Planetary Boundary Layer Height',
                                    'TSOIL': 'Soil Temperature',
                                    'SOILW': ('Volumetric Soil Moisture'
                                              + ' Content'),
                                    'WEASD': 'Accum. Snow Depth Water Equiv.',
                                    'APCP': ('Accumulated'
                                                + ' Precipitation'),
                                    'APCP_01': ('Accumulated'
                                                + ' Precipitation'),
                                    'APCP_03': ('Accumulated'
                                                + ' Precipitation'),
                                    'APCP_06': ('Accumulated'
                                                + ' Precipitation'),
                                    'APCP_24': ('Accumulated'
                                                + ' Precipitation'),
                                    'PWAT': 'Precipitable Water',
                                    'PTYPE': 'Precipitation Type',
                                    'CWAT': 'Cloud Water',
                                    'TCDC': 'Cloud Area Fraction',
                                    'HGTCLDCEIL': 'Cloud Ceiling Height',
                                    'VIS': 'Visibility',
                                    'sst': 'Sea Surface Temperature',
                                    'ssh': 'Sea Surface Height',
                                    'ice_coverage': 'Sea Ice Concentration',
                                    'sss': 'Sea Surface Salinity',
                                    'ICEC_Z0_mean': 'Sea Ice Concentration',
                                    'ICESEV': 'Icing Severity',
                                    'REFC': 'Composite Reflectivity',
                                    'REFD': 'Above Ground Level Reflectivity',
                                    'RETOP': 'Echo Top Height'}

        '''
        Given a domain requested in the plotting configuration file, the
        plotting scripts will print the long name of that domain according
        to this dictionary.  Add keys and values, not forgetting to include
        a comma at the end of any new lines.
        '''
        self.domain_translator = {'NHX': {
                                      'long_name': 'Northern Hemisphere 20N-80N',
                                      'save_name': 'NHX',
                                  },
                                  'SHX': {
                                      'long_name': 'Southern Hemisphere 20S-80S',
                                      'save_name': 'SHX',
                                  },
                                  'TRO': {
                                      'long_name': 'Tropics 20S-20N',
                                      'save_name': 'TRO',
                                  },
                                  'PNA': {
                                      'long_name': 'Pacific North America',
                                      'save_name': 'PNA',
                                  },
                                  'N60': {
                                      'long_name': '60N-90N',
                                      'save_name': 'N60',
                                  },
                                  'S60': {
                                      'long_name': '60S-90S',
                                      'save_name': 'S60',
                                  },
                                  'North_Pacific': {
                                      'long_name': 'Northern Pacific Ocean',
                                      'save_name': 'North_Pacific',
                                  },
                                  'NPO': {
                                      'long_name': 'Northern Pacific Ocean',
                                      'save_name': 'NPO',
                                  },
                                  'South_Pacific': {
                                      'long_name': 'Southern Pacific Ocean',
                                      'save_name': 'South_Pacific',
                                  },
                                  'SPO': {
                                      'long_name': 'Southern Pacific Ocean',
                                      'save_name': 'SPO',
                                  },
                                  'Equatorial_Pacific': {
                                      'long_name': 'Equatorial Pacific Ocean',
                                      'save_name': 'Equatorial_Pacific',
                                  },
                                  'North_Atlantic': {
                                      'long_name': 'Northern Atlantic Ocean',
                                      'save_name': 'North_Atlantic',
                                  },
                                  'NAO': {
                                      'long_name': 'Northern Atlantic Ocean',
                                      'save_name': 'NAO',
                                  },
                                  'South_Atlantic': {
                                      'long_name': 'Southern Atlantic Ocean',
                                      'save_name': 'South_Atlantic',
                                  },
                                  'SAO': {
                                      'long_name': 'Southern Atlantic Ocean',
                                      'save_name': 'SAO',
                                  },
                                  'Equatorial_Atlantic': {
                                      'long_name': 'Equatorial Atlantic Ocean',
                                      'save_name': 'Equatorial_Atlantic',
                                  },
                                  'Indian': {
                                      'long_name': 'Indian Ocean',
                                      'save_name': 'Indian',
                                  },
                                  'Southern': {
                                      'long_name': 'Southern Ocean',
                                      'save_name': 'Southern',
                                  },
                                  'Mediterranean': {
                                      'long_name': 'Mediterranean Sea',
                                      'save_name': 'Mediterranean',
                                  },
                                  'NH': {
                                      'long_name': 'Northern Hemisphere 20N-90N',
                                      'save_name': 'NH',
                                  },
                                  'SH': {
                                      'long_name': 'Southern Hemisphere 20S-90S',
                                      'save_name': 'SH',
                                  },
                                  'AR2': {
                                      'long_name': 'AR2',
                                      'save_name': 'AR2',
                                  },
                                  'ASIA': {
                                      'long_name': 'Asia',
                                      'save_name': 'ASIA',
                                  },
                                  'AUNZ': {
                                      'long_name': 'Australia and New Zealand',
                                      'save_name': 'AUNZ',
                                  },
                                  'NAMR': {
                                      'long_name': 'North America',
                                      'save_name': 'NAMR',
                                  },
                                  'NHM': {
                                      'long_name': 'Northern Hemisphere',
                                      'save_name': 'NHM',
                                  },
                                  'NPCF': {
                                      'long_name': 'North Pacific Ocean',
                                      'save_name': 'NPCF',
                                  },
                                  'SHM': {
                                      'long_name': 'Southern Hemisphere',
                                      'save_name': 'SHM',
                                  },
                                  'TRP': {
                                      'long_name': 'TRP',
                                      'save_name': 'TRP',
                                  },
                                  'G002': {
                                      'long_name': 'Global',
                                      'save_name': 'G002',
                                  },
                                  'G003': {
                                      'long_name': 'Global',
                                      'save_name': 'G003',
                                  },
                                  'Global': {
                                      'long_name': 'Global',
                                      'save_name': 'Global',
                                  },
                                  'G130': {
                                      'long_name': 'CONUS - NCEP Grid 130',
                                      'save_name': 'G130',
                                  },
                                  'G211': {
                                      'long_name': 'CONUS - NCEP Grid 211',
                                      'save_name': 'G211',
                                  },
                                  'G221': {
                                      'long_name': 'CONUS - NCEP Grid 221',
                                      'save_name': 'G221',
                                  },
                                  'G236': {
                                      'long_name': 'CONUS - NCEP Grid 236',
                                      'save_name': 'G236',
                                  },
                                  'G223': {
                                      'long_name': 'CONUS - NCEP Grid 223',
                                      'save_name': 'G223',
                                  },
                                  'CONUS': {
                                      'long_name': 'CONUS',
                                      'save_name': 'buk_conus',
                                  },
                                  'POLAR': {
                                      'long_name': 'Polar 60-90 N/S',
                                      'save_name': 'POLAR',
                                  },
                                  'ARCTIC': {
                                      'long_name': 'Arctic',
                                      'save_name': 'ARCTIC',
                                  },
                                  'Arctic': {
                                      'long_name': 'Arctic Ocean',
                                      'save_name': 'Arctic',
                                  },
                                  'Antarctic': {
                                      'long_name': 'Antarctic Ocean',
                                      'save_name': 'Antarctic',
                                  },
                                  'EAST': {
                                      'long_name': 'Eastern US',
                                      'save_name': 'EAST',
                                  },
                                  'CONUS_East': {
                                      'long_name': 'Eastern US',
                                      'save_name': 'buk_conus_e',
                                  },
                                  'WEST': {
                                      'long_name': 'Western US',
                                      'save_name': 'WEST',
                                  },
                                  'CONUS_West': {
                                      'long_name': 'Western US',
                                      'save_name': 'buk_conus_w',
                                  },
                                  'CONUS_Central': {
                                      'long_name': 'Central US',
                                      'save_name': 'buk_conus_c',
                                  },
                                  'CONUS_South': {
                                      'long_name': 'Southern US',
                                      'save_name': 'buk_conus_s',
                                  },
                                  'NWC': {
                                      'long_name': 'Northwest Coast',
                                      'save_name': 'NWC',
                                  },
                                  'PacificNW': {
                                      'long_name': 'Pacific Northwest',
                                      'save_name': 'buk_pnw',
                                  },
                                  'SWC': {
                                      'long_name': 'Southwest Coast',
                                      'save_name': 'SWC',
                                  },
                                  'PacificSW': {
                                      'long_name': 'Pacific Southwest',
                                      'save_name': 'buk_psw',
                                  },
                                  'NMT': {
                                      'long_name': 'Northern Mountain Region',
                                      'save_name': 'NMT',
                                  },
                                  'NRockies': {
                                      'long_name': 'Northern Rocky Mountains', 
                                      'save_name': 'buk_nrk',
                                  },
                                  'GRB': {
                                      'long_name': 'Great Basin',
                                      'save_name': 'GRB',
                                  },
                                  'GreatBasin': {
                                      'long_name': 'Great Basin',
                                      'save_name': 'buk_grb',
                                  },
                                  'SMT': {
                                      'long_name': 'Southern Mountain Region',
                                      'save_name': 'SMT',
                                  },
                                  'SRockies': {
                                      'long_name': 'Southern Rocky Mountains',
                                      'save_name': 'buk_srk',
                                  },
                                  'SWD': {
                                      'long_name': 'Southwest Desert',
                                      'save_name': 'SWD',
                                  },
                                  'Mezquital': {
                                      'long_name': 'Mezquital',
                                      'save_name': 'buk_mez',
                                  },
                                  'NPL': {
                                      'long_name': 'Northern Plains',
                                      'save_name': 'NPL',
                                  },
                                  'NPlains': {
                                      'long_name': 'Northern Plains',
                                      'save_name': 'buk_npl',
                                  },
                                  'CPlains': {
                                      'long_name': 'Central Plains',
                                      'save_name': 'buk_cpl',
                                  },
                                  'SPL': {
                                      'long_name': 'Southern Plains',
                                      'save_name': 'SPL',
                                  },
                                  'SPlains': {
                                      'long_name': 'Southern Plains',
                                      'save_name': 'buk_spl',
                                  },
                                  'Prairie': {
                                      'long_name': 'Prairie',
                                      'save_name': 'buk_pra',
                                  },
                                  'GreatLakes': {
                                      'long_name': 'Great Lakes',
                                      'save_name': 'buk_grlk',
                                  },
                                  'MDW': {
                                      'long_name': 'Midwest',
                                      'save_name': 'MDW',
                                  },
                                  'LMV': {
                                      'long_name': 'Lower Mississippi Valley',
                                      'save_name': 'LMV',
                                  },
                                  'APL': {
                                      'long_name': 'Appalachians',
                                      'save_name': 'APL',
                                  },
                                  'Appalachia': {
                                      'long_name': 'Appalachia',
                                      'save_name': 'buk_apl',
                                  },
                                  'NorthAtlantic': {
                                      'long_name': 'Northeast',
                                      'save_name': 'buk_ne',
                                  },
                                  'MidAtlantic': {
                                      'long_name': 'Mid-Atlantic',
                                      'save_name': 'buk_matl',
                                  },
                                  'NEC': {
                                      'long_name': 'Northeast Coast',
                                      'save_name': 'NEC',
                                  },
                                  'SEC': {
                                      'long_name': 'Southeast Coast',
                                      'save_name': 'SEC',
                                  },
                                  'Southeast': {
                                      'long_name': 'Southeast',
                                      'save_name': 'buk_se',
                                  },
                                  'Southwest': {
                                      'long_name': 'Southwest',
                                      'save_name': 'buk_sw',
                                  },
                                  'GMC': {
                                      'long_name': 'Gulf of Mexico Coast',
                                      'save_name': 'GMC',
                                  },
                                  'DeepSouth': {
                                      'long_name': 'Deep South',
                                      'save_name': 'buk_ds',
                                  },
                                  'Alaska': {
                                      'long_name': 'Alaska',
                                      'save_name': 'alaska',
                                  },
                                  'NAK': {
                                      'long_name': 'Northern Alaska',
                                      'save_name': 'NAK',
                                  },
                                  'SAK': {
                                      'long_name': 'Southern Alaska',
                                      'save_name': 'NAK',
                                  },
                                  'Hawaii': {
                                      'long_name': 'Hawaii',
                                      'save_name': 'hawaii',
                                  },
                                  'PuertoRico': {
                                      'long_name': 'Puerto Rico',
                                      'save_name': 'prico',
                                  },
                                  'Guam': {
                                      'long_name': 'Guam',
                                      'save_name': 'guam',
                                  },
                                  'FireWx': {
                                      'long_name': 'Fire Weather Nest',
                                      'save_name': 'firewx',
                                  },
                                  'SEA_ICE': {
                                      'long_name': 'Global - Sea Ice',
                                      'save_name': 'SEA_ICE',
                                  },
                                  'SEA_ICE_FREE': {
                                      'long_name': 'Global - Sea Ice Free',
                                      'save_name': 'SEA_ICE_FREE',
                                  },
                                  'SEA_ICE_POLAR': {
                                      'long_name': 'Polar - Sea Ice',
                                      'save_name': 'SEA_ICE_POLAR',
                                  },
                                  'SEA_ICE_FREE_POLAR': {
                                      'long_name': 'Polar - Sea Ice Free',
                                      'save_name': 'SEA_ICE_FREE_POLAR',
                                  },
        }
        self.linetype_cols = {'FHO':['TOTAL','F_RATE','H_RATE','O_RATE'],
                              'CTC':['TOTAL','FY_OY','FY_ON','FN_OY','FN_ON'],
                              'CTS':['TOTAL','BASER','BASER_NCL','BASER_NCU',
                                     'BASER_BCL','BASER_BCU','FMEAN',
                                     'FMEAN_NCL','FMEAN_NCU','FMEAN_BCL',
                                     'FMEAN_BCU','ACC','ACC_NCL','ACC_NCU',
                                     'ACC_BCL','ACC_BCU','FBIAS','FBIAS_BCL',
                                     'FBIAS_BCU','PODY','PODY_NCL','PODY_NCU',
                                     'PODY_BCL','PODY_BCU','PODN','PODN_NCL',
                                     'PODN_NCU','PODN_BCL','PODN_BCU','POFD',
                                     'POFD_NCL','POFD_NCU','POFD_BCL',
                                     'POFD_BCU','FAR','FAR_NCL','FAR_NCU',
                                     'FAR_BCL','FAR_BCU','CSI','CSI_NCL',
                                     'CSI_NCU','CSI_BCL','CSI_BCU','GSS',
                                     'GSS_BCL','GSS_BCU','HK','HK_NCL',
                                     'HK_NCU','HK_BCL','HK_BCU','HSS',
                                     'HSS_BCL','HSS_BCU','ODDS','ODDS_NCL',
                                     'ODDS_NCU','ODDS_BCL','ODDS_BCU','LODDS',
                                     'LODDS_NCL','LODDS_NCU','LODDS_BCL',
                                     'LODDS_BCU','ORSS','ORSS_NCL','ORSS_NCU',
                                     'ORSS_BCL','ORSS_BCU','EDS','EDS_NCL',
                                     'EDS_NCU','EDS_BCL','EDS_BCU','SEDS',
                                     'SEDS_NCL','SEDS_NCU','SEDS_BCL',
                                     'SEDS_BCU','EDI','EDI_NCL','EDI_NCU',
                                     'EDI_BCL','EDI_BCU','SEDI','SEDI_NCL',
                                     'SEDI_NCU','SEDI_BCL','SEDI_BCU','BAGSS',
                                     'BAGSS_BCL','BAGSS_BCU'],
                              'CNT':['TOTAL','FBAR','FBAR_NCL','FBAR_NCU',
                                     'FBAR_BCL','FBAR_BCU','FSTDEV',
                                     'FSTDEV_NCL','FSTDEV_NCU','FSTDEV_BCL',
                                     'FSTDEV_BCU','OBAR','OBAR_NCL',
                                     'OBAR_NCU','OBAR_BCL','OBAR_BCU',
                                     'OSTDEV','OSTDEV_NCL','OSTDEV_NCU',
                                     'OSTDEV_BCL','OSTDEV_BCU','PR_CORR',
                                     'PR_CORR_NCL','PR_CORR_NCU',
                                     'PR_CORR_BCL','PR_CORR_BCU','SP_CORR', 
                                     'KT_CORR','RANKS','FRANK_TIES',
                                     'ORANK_TIES','ME','ME_NCL','ME_NCU',
                                     'ME_BCL','ME_BCU','ESTDEV','ESTDEV_NCL',
                                     'ESTDEV_NCU','ESTDEV_BCL','ESTDEV_BCU',
                                     'MBIAS','MBIAS_BCL','MBIAS_BCU',
                                     'MAE','MAE_BCL','MAE_BCU',
                                     'MSE','MSE_BCL','MSE_BCU',
                                     'BCMSE','BCMSE_BCL','BCMSE_BCU',
                                     'RMSE','RMSE_BCL','RMSE_BCU',
                                     'E10','E10_BCL','E10_BCU',
                                     'E25','E25_BCL','E25_BCU',
                                     'E50','E50_BCL','E50_BCU',
                                     'E75','E75_BCL','E75_BCU',
                                     'E90','E90_BCL','E90_BCU',
                                     'IQR','IQR_BCL','IQR_BCU',
                                     'MAD','MAD_BCL','MAD_BCU',
                                     'ANOM_CORR','ANOM_CORR_NCL',
                                     'ANOM_CORR_NCU','ANOM_CORR_BCL',
                                     'ANOM_CORR_BCU',
                                     'ME2','ME2_BCL','ME2_BCU',
                                     'MSESS','MSESS_BCL','MSESS_BCU',
                                     'RMSFA','RMSFA_BCL','RMSFA_BCU',
                                     'RMSOA','RMSOA_BCL','RMSOA_BCU',
                                     'ANOM_CORR_UNCNTR',
                                     'ANOM_CORR_UNCNTR_BCL',
                                     'ANOM_CORR_UNCNTR_BCU'],
                              'MCTC':['TOTAL','N_CAT','Fi_Oj'],
                              'MCTS':['TOTAL','N_CAT','ACC','ACC_NCL',
                                      'ACC_NCU','ACC_BCL','ACC_BCU',
                                      'HK','HK_BCL','HK_BCU',
                                      'GER','GER_BCL','GER_BCU'],
                              'PCT':['TOTAL','N_THRESH','THRESH_i','OY_i',
                                      'ON_i','THRESH_n'],
                              'PSTD':['TOTAL','N_THRESH','BASER','BASER_NCL',
                                      'BASER_NCU','RELIABILITY','RESOLUTION',
                                      'UNCERTAINTY','ROC_AUC','BRIER',
                                      'BRIER_NCL','BRIER_NCU','BRIERCL',
                                      'BRIERCL_NCL','BRIERCL_NCU',
                                      'BSS','BSS_SMPL','THRESH_i'],
                              'PJC':['TOTAL','N_THRESH','THRESH_i','OY_TP_i',
                                     'ON_TP_i','CALIBRATION_i','REFINEMENT_i',
                                     'LIKELIHOOD_i','BASER_i','THRESH_n'],
                              'PRC':['TOTAL','N_THRESH','THRESH_i','PODY_i',
                                      'POFD_i','THRESH_n'],
                              'ECLV':['TOTAL','BASER','VALUE_BASER','N_PNT',
                                      'CL_i','VALUE_i'],
                              'SL1L2':['TOTAL','FBAR','OBAR','FOBAR','FFBAR',
                                       'OOBAR','MAE'],
                              'SAL1L2':['TOTAL','FABAR','OABAR','FOABAR',
                                        'FFABAR','OOABAR','MAE'],
                              'VL1L2':['TOTAL','UFBAR','VFBAR','UOBAR',
                                       'VOBAR','UVFOBAR','UVFFBAR','UVOOBAR',
                                       'F_SPEED_BAR','O_SPEED_BAR'],
                              'VAL1L2':['TOTAL','UFABAR','VFABAR','UOABAR',
                                        'VOABAR','UVFOABAR','UVFFABAR',
                                        'UVOOABAR'],
                              'VCNT':['TOTAL','FBAR','OBAR','FS_RMS','OS_RMS',
                                      'MSVE','RMSVE','FSTDEV','OSTDEV',
                                      'FDIR','ODIR','FBAR_SPEED','OBAR_SPEED',
                                      'VDIFF_SPEED','VDIFF_DIR','SPEED_ERR',
                                      'SPEED_ABSERR','DIR_ERR','DIR_ABSERR'],
                              'MPR':['TOTAL','INDEX','OBS_SID','OBS_LAT',
                                     'OBS_LON','OBS_LVL','OBS_ELV','FCST',
                                     'OBS','OBS_QC','CLIMO_MEAN',
                                     'CLIMO_STDEV','CLIMO_CDF'],
                              'NBRCTC':['TOTAL','FY_OY','FY_ON','FN_OY',
                                        'FN_ON'],
                              'NBRCTS':['TOTAL','BASER','BASER_NCL',
                                        'BASER_NCU','BASER_BCL','BASER_BCU',
                                        'FMEAN','FMEAN_NCL','FMEAN_NCU',
                                        'FMEAN_BCL','FMEAN_BCU','ACC',
                                        'ACC_NCL','ACC_NCU','ACC_BCL',
                                        'ACC_BCU','FBIAS','FBIAS_BCL',
                                        'FBIAS_BCU','PODY','PODY_NCL',
                                        'PODY_NCU','PODY_BCL','PODY_BCU',
                                        'PODN','PODN_NCL','PODN_NCU',
                                        'PODN_BCL','PODN_BCU','POFD',
                                        'POFD_NCL','POFD_NCU','POFD_BCL',
                                        'POFD_BCU','FAR','FAR_NCL','FAR_NCU',
                                        'FAR_BCL','FAR_BCU','CSI','CSI_NCL',
                                        'CSI_NCU','CSI_BCL','CSI_BCU','GSS',
                                        'GSS_BCL','GSS_BCU','HK','HK_NCL',
                                        'HK_NCU','HK_BCL','HK_BCU','HSS',
                                        'HSS_BCL','HSS_BCU','ODDS','ODDS_NCL',
                                        'ODDS_NCU','ODDS_BCL','ODDS_BCU',
                                        'LODDS','LODDS_NCL','LODDS_NCU',
                                        'LODDS_BCL','LODDS_BCU','ORSS',
                                        'ORSS_NCL','ORSS_NCU','ORSS_BCL',
                                        'ORSS_BCU','EDS','EDS_NCL','EDS_NCU',
                                        'EDS_BCL','EDS_BCU','SEDS','SEDS_NCL',
                                        'SEDS_NCU','SEDS_BCL','SEDS_BCU',
                                        'EDI','EDI_NCL','EDI_NCU','EDI_BCL',
                                        'EDI_BCU','SEDI','SEDI_NCL',
                                        'SEDI_NCU','SEDI_BCL','SEDI_BCU',
                                        'BAGSS','BAGSS_BCL','BAGSS_BCU'],
                              'NBRCNT':['TOTAL','FBS','FBS_BCL','FBS_BCU',
                                        'FSS','FSS_BCL','FSS_BCU',
                                        'AFSS','AFSS_BCL','AFSS_BCU',
                                        'UFSS','UFSS_BCL','UFSS_BCU',
                                        'F_RATE','F_RATE_BCL','F_RATE_BCU',
                                        'O_RATE','O_RATE_BCL','O_RATE_BCU'],
                              'GRAD':['TOTAL','FGBAR','OGBAR','MGBAR','EGBAR',
                                      'S1','S1_OG','FGOG_RATIO','DX','DY'],
                              'DMAP':['TOTAL','FY','OY','FBIAS','BADDELEY',
                                      'HAUSDORFF','MED_FO','MED_OF','MED_MIN',
                                      'MED_MAX','MED_MEAN','FOM_FO','FOM_OF',
                                      'FOM_MIN','FROM_MAX','FOM_MEAN','ZHU_FO',
                                      'ZHU_OF','ZHU_MIN','ZHU_MAX','ZHU_MEAN'],
        }

        '''
        Define plotting jobs that are allowed in order to draw attention to 
        configuration typos, to delineate the bounds of expected user
        configurations, and to prevent unexpected behavior.  
        
        The case_type dictionary contains nested dictionaries, each named for
        a specific configuration, and nested based on the type of configuration.  
        The hierarchy is this: 
        self.case_type[VERIF_CASE_VERIF_TYPE][LINE_TYPE]['var_dict'][var_name]
        
        The var_name dictionary contains possible settings for the fcst/obs
        names, levels, thresholds, and options stored in the MET .stat files.
        It also includes the appropriate plotting group for that var_name
        (e.g., 'sfc_upper', 'radar', 'ceil_vis', 'cape', or 'precip').

        The LINE_TYPE dictionary includes the 'var_dict' dictionary and a few 
        additional variables. 'plot_stats_list' is a string containing a 
        comma-separated list of possible metrics that may be computed using 
        LINE_TYPE lines. 'interp' is a string containing a comma-separated list
        of possible interpolation methods that may be searched for if the 
        line type is LINE_TYPE. 'vx_mask_list' is a python list of strings,
        each string representing a possible domain name in the VX_MASK column
        in the MET .stat file.
        '''
        self.case_type = {
            'grid2grid_anom': {
                'SAL1L2': {
                    'plot_stats_list': 'acc',
                    'interp': 'NEAREST',
                    'vx_mask_list' : ['NHX', 'SHX', 'PNA', 'TRO'],
                    'var_dict': {
                        'HGT': {'fcst_var_names': ['HGT'],
                                'fcst_var_levels': [
                                    'P1000', 'P700', 'P500', 'P250'
                                ],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['HGT'],
                                'obs_var_levels': [
                                    'P1000', 'P700', 'P500', 'P250'
                                ],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'HGT_WV1_0-20': {'fcst_var_names': ['HGT'],
                                         'fcst_var_levels': [
                                             'P1000', 'P700', 'P500', 'P250'
                                         ],
                                         'fcst_var_thresholds': '',
                                         'fcst_var_options': '',
                                         'obs_var_names': ['HGT'],
                                         'obs_var_levels': [
                                             'P1000', 'P700', 'P500', 'P250'
                                         ],
                                         'obs_var_thresholds': '',
                                         'obs_var_options': '',
                                         'plot_group':'sfc_upper'},
                        'HGT_WV1_0-3': {'fcst_var_names': ['HGT'],
                                        'fcst_var_levels': [
                                            'P1000', 'P700', 'P500', 'P250'
                                        ],
                                        'fcst_var_thresholds': '',
                                        'fcst_var_options': '',
                                        'obs_var_names': ['HGT'],
                                        'obs_var_levels': [
                                            'P1000', 'P700', 'P500', 'P250'
                                        ],
                                        'obs_var_thresholds': '',
                                        'obs_var_options': '',
                                        'plot_group':'sfc_upper'},
                        'HGT_WV1_4-9': {'fcst_var_names': ['HGT'],
                                        'fcst_var_levels': [
                                            'P1000', 'P700', 'P500', 'P250'
                                        ],
                                        'fcst_var_thresholds': '',
                                        'fcst_var_options': '',
                                        'obs_var_names': ['HGT'],
                                        'obs_var_levels': [
                                            'P1000', 'P700', 'P500', 'P250'
                                        ],
                                        'obs_var_thresholds': '',
                                        'obs_var_options': '',
                                        'plot_group':'sfc_upper'},
                        'HGT_WV1_10-20': {'fcst_var_names': ['HGT'],
                                          'fcst_var_levels': [
                                              'P1000', 'P700', 'P500', 'P250'
                                          ],
                                          'fcst_var_thresholds': '',
                                          'fcst_var_options': '',
                                          'obs_var_names': ['HGT'],
                                          'obs_var_levels': [
                                              'P1000', 'P700', 'P500', 'P250'
                                          ],
                                          'obs_var_thresholds': '',
                                          'obs_var_options': '',
                                          'plot_group':'sfc_upper'},
                        'TMP': {'fcst_var_names': ['TMP'],
                                'fcst_var_levels': ['P850', 'P500', 'P250'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['TMP'],
                                'obs_var_levels': ['P850', 'P500', 'P250'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'UGRD': {'fcst_var_names': ['UGRD'],
                                 'fcst_var_levels': ['P850', 'P500', 'P250'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['UGRD'],
                                 'obs_var_levels': ['P850', 'P500', 'P250'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'VGRD': {'fcst_var_names': ['VGRD'],
                                 'fcst_var_levels': ['P850', 'P500', 'P250'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['VGRD'],
                                 'obs_var_levels': ['P850', 'P500', 'P250'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'PRMSL': {'fcst_var_names': ['PRMSL'],
                                  'fcst_var_levels': ['Z0'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['PRMSL'],
                                  'obs_var_levels': ['Z0'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'}
                    }
                },
                'VAL1L2': {
                    'plot_stats_list': 'acc',
                    'interp': 'NEAREST',
                    'vx_mask_list' : ['NHX', 'SHX', 'PNA', 'TRO'],
                    'var_dict': {
                        'UGRD_VGRD': {'fcst_var_names': ['UGRD_VGRD'],
                                      'fcst_var_levels': [
                                          'P850', 'P500', 'P250'
                                      ],
                                      'fcst_var_thresholds': '',
                                      'fcst_var_options': '',
                                      'obs_var_names': ['UGRD_VGRD'],
                                      'obs_var_levels': [
                                          'P850', 'P500', 'P250'
                                      ],
                                      'obs_var_thresholds': '',
                                      'obs_var_options': '',
                                      'plot_group':'sfc_upper'}
                    }
                }
            },
            'grid2grid_pres': {
                'SL1L2': {
                    'plot_stats_list': ('me, rmse, msess, rsd, rmse_md,'
                                        + ' rmse_pv'),
                    'interp': 'NEAREST',
                    'vx_mask_list' : ['NHX', 'SHX', 'PNA', 'TRO'],
                    'var_dict': {
                        'HGT': {'fcst_var_names': ['HGT'],
                                'fcst_var_levels': [
                                    'P1000', 'P850', 'P700', 'P500', 'P200', 
                                    'P100', 'P50', 'P20', 'P10', 'P5', 'P1'
                                ],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['HGT'],
                                'obs_var_levels': [
                                    'P1000', 'P850', 'P700', 'P500', 'P200', 
                                    'P100', 'P50', 'P20', 'P10', 'P5', 'P1'
                                ],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'TMP': {'fcst_var_names': ['TMP'],
                                'fcst_var_levels': [
                                    'P1000', 'P850', 'P700', 'P500', 'P200', 
                                    'P100', 'P50', 'P20', 'P10', 'P5', 'P1'
                                ],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['TMP'],
                                'obs_var_levels': [
                                    'P1000', 'P850', 'P700', 'P500', 'P200', 
                                    'P100', 'P50', 'P20', 'P10', 'P5', 'P1'
                                ],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'UGRD': {'fcst_var_names': ['UGRD'],
                                 'fcst_var_levels': [
                                     'P1000', 'P850', 'P700', 'P500', 'P200', 
                                     'P100', 'P50', 'P20', 'P10', 'P5', 'P1'
                                 ],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['UGRD'],
                                 'obs_var_levels': [
                                     'P1000', 'P850', 'P700', 'P500', 'P200', 
                                     'P100', 'P50', 'P20', 'P10', 'P5', 'P1'
                                 ],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'VGRD': {'fcst_var_names': ['VGRD'],
                                 'fcst_var_levels': [
                                     'P1000', 'P850', 'P700', 'P500', 'P200', 
                                     'P100', 'P50', 'P20', 'P10', 'P5', 'P1'
                                 ],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['VGRD'],
                                 'obs_var_levels': [
                                     'P1000', 'P850', 'P700', 'P500', 'P200', 
                                     'P100', 'P50', 'P20', 'P10', 'P5', 'P1'
                                 ],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'O3MR': {'fcst_var_names': ['O3MR'],
                                 'fcst_var_levels': [
                                     'P100', 'P70', 'P50', 'P30', 'P20', 
                                     'P10', 'P5', 'P1'
                                 ],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['O3MR'],
                                 'obs_var_levels': [
                                     'P100', 'P70', 'P50', 'P30', 'P20', 
                                     'P10', 'P5', 'P1'
                                 ],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'}
                    }
                },
                'VL1L2': {
                    'plot_stats_list': ('me, rmse, msess, rsd, rmse_md,'
                                        + ' rmse_pv'),
                    'interp': 'NEAREST',
                    'vx_mask_list' : ['NHX', 'SHX', 'PNA', 'TRO'],
                    'var_dict': {
                        'UGRD_VGRD': {'fcst_var_names': ['UGRD_VGRD'],
                                      'fcst_var_levels': [
                                          'P1000', 'P850', 'P700', 'P500', 
                                          'P200', 'P100', 'P50', 'P20', 'P10', 
                                          'P5', 'P1'
                                      ],
                                      'fcst_var_thresholds': '',
                                      'fcst_var_options': '',
                                      'obs_var_names': ['UGRD_VGRD'],
                                      'obs_var_levels': [
                                          'P1000', 'P850', 'P700', 'P500', 
                                          'P200', 'P100', 'P50', 'P20', 'P10', 
                                          'P5', 'P1'
                                      ],
                                      'obs_var_thresholds': '',
                                      'obs_var_options': '',
                                      'plot_group':'sfc_upper'}
                    }
                }
            },
            'grid2grid_sfc': {
                'SL1L2': {
                    'plot_stats_list': 'fbar',
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO', 'SPO', 
                        'NAO', 'SAO', 'G130', 'CONUS'
                    ],
                    'var_dict': {
                        'TMP2m': {'fcst_var_names': ['TMP'],
                                  'fcst_var_levels': ['Z2'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['TMP'],
                                  'obs_var_levels': ['Z2'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'TMPsfc': {'fcst_var_names': ['TMP'],
                                   'fcst_var_levels': ['Z0'],
                                   'fcst_var_thresholds': '',
                                   'fcst_var_options': '',
                                   'obs_var_names': ['TMP'],
                                   'obs_var_levels': ['Z0'],
                                   'obs_var_thresholds': '',
                                   'obs_var_options': '',
                                   'plot_group':'sfc_upper'},
                        'TMPtrops': {'fcst_var_names': ['TMP'],
                                     'fcst_var_levels': ['L0'],
                                     'fcst_var_thresholds': '',
                                     'fcst_var_options': 'GRIB_lvl_typ = 7;',
                                     'obs_var_names': ['TMP'],
                                     'obs_var_levels': ['L0'],
                                     'obs_var_thresholds': '',
                                     'obs_var_options': 'GRIB_lvl_typ = 7;',
                                     'plot_group':'sfc_upper'},
                        'RH2m': {'fcst_var_names': ['RH'],
                                 'fcst_var_levels': ['Z2'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['RH'],
                                 'obs_var_levels': ['Z2'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'SPFH2m': {'fcst_var_names': ['SPFH'],
                                   'fcst_var_levels': ['Z2'],
                                   'fcst_var_thresholds': '',
                                   'fcst_var_options': '',
                                   'obs_var_names': ['SPFH'],
                                   'obs_var_levels': ['Z2'],
                                   'obs_var_thresholds': '',
                                   'obs_var_options': '',
                                   'plot_group':'sfc_upper'},
                        'HPBL': {'fcst_var_names': ['HPBL'],
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['HPBL'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'PRESsfc': {'fcst_var_names': ['PRES'],
                                    'fcst_var_levels': ['Z0'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['PRES'],
                                    'obs_var_levels': ['Z0'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'PREStrops': {'fcst_var_names': ['PRES'],
                                      'fcst_var_levels': ['L0'],
                                      'fcst_var_thresholds': '',
                                      'fcst_var_options': 'GRIB_lvl_typ = 7;',
                                      'obs_var_names': ['PRES'],
                                      'obs_var_levels': ['L0'],
                                      'obs_var_thresholds': '',
                                      'obs_var_options': 'GRIB_lvl_typ = 7;',
                                      'plot_group':'sfc_upper'},
                        'PRMSL': {'fcst_var_names': ['PRMSL'],
                                  'fcst_var_levels': ['Z0'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['PRMSL'],
                                  'obs_var_levels': ['Z0'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'UGRD10m': {'fcst_var_names': ['UGRD'],
                                    'fcst_var_levels': ['Z10'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['UGRD'],
                                    'obs_var_levels': ['Z10'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'VGRD10m': {'fcst_var_names': ['VGRD'],
                                    'fcst_var_levels': ['Z10'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['VGRD'],
                                    'obs_var_levels': ['Z10'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'TSOILtop': {'fcst_var_names': ['TSOIL'],
                                     'fcst_var_levels': ['Z10-0'],
                                     'fcst_var_thresholds': '',
                                     'fcst_var_options': '',
                                     'obs_var_names': ['TSOIL'],
                                     'obs_var_levels': ['Z10-0'],
                                     'obs_var_thresholds': '',
                                     'obs_var_options': '',
                                     'plot_group':'sfc_upper'},
                        'SOILWtop': {'fcst_var_names': ['SOILW'],
                                     'fcst_var_levels': ['Z10-0'],
                                     'fcst_var_thresholds': '',
                                     'fcst_var_options': '',
                                     'obs_var_names': ['SOILW'],
                                     'obs_var_levels': ['Z10-0'],
                                     'obs_var_thresholds': '',
                                     'obs_var_options': '',
                                     'plot_group':'sfc_upper'},
                        'WEASD': {'fcst_var_names': ['WEASD'],
                                  'fcst_var_levels': ['Z0'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['WEASD'],
                                  'obs_var_levels': ['Z0'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'precip'},
                        'CAPE': {'fcst_var_names': ['CAPE'],
                                 'fcst_var_levels': ['Z0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['CAPE'],
                                 'obs_var_levels': ['Z0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'cape'},
                        'PWAT': {'fcst_var_names': ['PWAT'],
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['PWAT'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'CWAT': {'fcst_var_names': ['CWAT'],
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['CWAT'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'HGTtrops': {'fcst_var_names': ['HGT'],
                                     'fcst_var_levels': ['L0'],
                                     'fcst_var_thresholds': '',
                                     'fcst_var_options': 'GRIB_lvl_typ = 7;',
                                     'obs_var_names': ['HGT'],
                                     'obs_var_levels': ['L0'],
                                     'obs_var_thresholds': '',
                                     'obs_var_options': 'GRIB_lvl_typ = 7;',
                                     'plot_group':'sfc_upper'},
                        'TOZNEclm': {'fcst_var_names': ['TOZNE'],
                                     'fcst_var_levels': ['L0'],
                                     'fcst_var_thresholds': '',
                                     'fcst_var_options': '',
                                     'obs_var_names': ['TOZNE'],
                                     'obs_var_levels': ['L0'],
                                     'obs_var_thresholds': '',
                                     'obs_var_options': '',
                                     'plot_group':'sfc_upper'}
                    }
                }
            },
            'grid2grid_mrms':{
                'CTC': {
                    'plot_stats_list': ('fss, csi, fbias, pod, faratio,'
                                        + ' sratio'),
                    'interp': 'NEAREST, NBRHD_CIRCLE, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'G130', 'APL', 'GMC', 'GRB', 'LMV', 'MDW', 'NEC', 
                        'NMT', 'NPL', 'NWC', 'SEC', 'SMT', 'SPL', 'SWC', 
                        'SWD', 'DAY1_1200_TSTM', 'DAY2_1730_TSTM'
                    ],
                    'var_dict': {
                        'REFC': {'fcst_var_names': ['REFC'],
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': ('>=20, >=30, >=40,'
                                                         + ' >=50'),
                                 'fcst_var_options': '',
                                 'obs_var_names': [
                                     'MergedReflectivityQCComposite'
                                 ],
                                 'obs_var_levels': ['Z500'],
                                 'obs_var_thresholds': ('>=20, >=30, >=40,'
                                                        + ' >=50'),
                                 'obs_var_options': '',
                                 'plot_group':'radar'},
                        'RETOP': {'fcst_var_names': ['RETOP'],
                                 'fcst_var_levels': ['L0','Z1000'],
                                 'fcst_var_thresholds': ('>=20, >=30, >=40,'
                                                         + ' >=50'),
                                 'fcst_var_options': '',
                                 'obs_var_names': ['EchoTop18'],
                                 'obs_var_levels': ['L0','Z500'],
                                 'obs_var_thresholds': ('>=20, >=30, >=40,'
                                                        + ' >=50'),
                                 'obs_var_options': '',
                                 'plot_group':'radar'},
                        'REFD': {'fcst_var_names': ['REFD'],
                                 'fcst_var_levels': ['L0','Z1000'],
                                 'fcst_var_thresholds': ('>=20, >=30, >=40,'
                                                         + ' >=50'),
                                 'fcst_var_options': '',
                                 'obs_var_names': ['SeamlessHSR'],
                                 'obs_var_levels': ['L0','Z500'],
                                 'obs_var_thresholds': ('>=20, >=30, >=40,'
                                                        + ' >=50'),
                                 'obs_var_options': '',
                                 'plot_group':'radar'}
                    }
                }
            },
            'radar_mrms':{
                'CTC': {
                    'plot_stats_list': ('fss, csi, fbias, pod, faratio,'
                                        + ' sratio'),
                    'interp': 'NEAREST, NBRHD_CIRCLE, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'G130', 'APL', 'GMC', 'GRB', 'LMV', 'MDW', 'NEC', 
                        'NMT', 'NPL', 'NWC', 'SEC', 'SMT', 'SPL', 'SWC', 
                        'SWD', 'DAY1_1200_TSTM', 'DAY2_1730_TSTM'
                    ],
                    'var_dict': {
                        'REFC': {'fcst_var_names': ['REFC'],
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': ('>=20, >=30, >=40,'
                                                         + ' >=50'),
                                 'fcst_var_options': '',
                                 'obs_var_names': [
                                     'MergedReflectivityQCComposite'
                                 ],
                                 'obs_var_levels': ['Z500'],
                                 'obs_var_thresholds': ('>=20, >=30, >=40,'
                                                        + ' >=50'),
                                 'obs_var_options': '',
                                 'plot_group':'radar'},
                        'RETOP': {'fcst_var_names': ['RETOP'],
                                 'fcst_var_levels': ['L0','Z1000'],
                                 'fcst_var_thresholds': ('>=20, >=30, >=40,'
                                                         + ' >=50'),
                                 'fcst_var_options': '',
                                 'obs_var_names': ['EchoTop18'],
                                 'obs_var_levels': ['L0','Z500'],
                                 'obs_var_thresholds': ('>=20, >=30, >=40,'
                                                        + ' >=50'),
                                 'obs_var_options': '',
                                 'plot_group':'radar'},
                        'REFD': {'fcst_var_names': ['REFD'],
                                 'fcst_var_levels': ['L0','Z1000'],
                                 'fcst_var_thresholds': ('>=20, >=30, >=40,'
                                                         + ' >=50'),
                                 'fcst_var_options': '',
                                 'obs_var_names': ['SeamlessHSR'],
                                 'obs_var_levels': ['L0','Z500'],
                                 'obs_var_thresholds': ('>=20, >=30, >=40,'
                                                        + ' >=50'),
                                 'obs_var_options': '',
                                 'plot_group':'radar'}
                    }
                }
            },
            'grid2obs_upper_air': {
                'SL1L2': {
                    'plot_stats_list': ('me, rmse, bcrmse, fbar_obar, fbar,'
                                        + ' obar'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'G130', 'NH', 'SH', 'TRO', 'G236', 'POLAR', 'ARCTIC', 
                        'NAK', 'SAK'
                    ],
                    'var_dict': {
                        'TMP': {'fcst_var_names': ['TMP'],
                                'fcst_var_levels': ['P1000', 'P925', 'P850',
                                                    'P700', 'P500', 'P400',
                                                    'P300', 'P250', 'P200',
                                                    'P150', 'P100', 'P50',
                                                    'P10', 'P5', 'P1'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['TMP'],
                                'obs_var_levels': ['P1000', 'P925', 'P850',
                                                   'P700', 'P500', 'P400',
                                                   'P300', 'P250', 'P200',
                                                   'P150', 'P100', 'P50',
                                                   'P10', 'P5', 'P1'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'RH': {'fcst_var_names': ['RH'],
                               'fcst_var_levels': ['P1000', 'P925', 'P850',
                                                   'P700', 'P500', 'P400',
                                                   'P300', 'P250', 'P200',
                                                   'P150', 'P100', 'P50',
                                                   'P10', 'P5', 'P1'],
                               'fcst_var_thresholds': '',
                               'fcst_var_options': '',
                               'obs_var_names': ['RH'],
                               'obs_var_levels': ['P1000', 'P925', 'P850',
                                                  'P700', 'P500', 'P400',
                                                  'P300', 'P250', 'P200',
                                                  'P150', 'P100', 'P50',
                                                  'P10', 'P5', 'P1'],
                               'obs_var_thresholds': '',
                               'obs_var_options': '',
                               'plot_group':'sfc_upper'},
                        'SPFH': {'fcst_var_names': ['SPFH'],
                                 'fcst_var_levels': ['P1000', 'P925', 'P850',
                                                     'P700', 'P500', 'P400',
                                                     'P300', 'P250', 'P200',
                                                     'P150', 'P100', 'P50',
                                                     'P10', 'P5', 'P1'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['SPFH'],
                                 'obs_var_levels': ['P1000', 'P925', 'P850',
                                                    'P700', 'P500', 'P400',
                                                    'P300', 'P250', 'P200',
                                                    'P150', 'P100', 'P50',
                                                    'P10', 'P5', 'P1'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'HGT': {'fcst_var_names': ['HGT'],
                                'fcst_var_levels': ['P1000', 'P925', 'P850',
                                                    'P700', 'P500', 'P400',
                                                    'P300', 'P250', 'P200',
                                                    'P150', 'P100', 'P50',
                                                    'P10', 'P5', 'P1'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['HGT','ZOB'],
                                'obs_var_levels': ['P1000', 'P925', 'P850',
                                                   'P700', 'P500', 'P400',
                                                   'P300', 'P250', 'P200',
                                                   'P150', 'P100', 'P50',
                                                   'P10', 'P5', 'P1'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                    }
                },
                'VL1L2': {
                    'plot_stats_list': ('me, rmse, bcrmse, fbar_obar, fbar,'
                                        + ' obar'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'G130', 'NH', 'SH', 'TRO', 'G236', 'POLAR', 'ARCTIC', 
                        'NAK', 'SAK'
                    ],
                    'var_dict': {
                        'UGRD_VGRD': {'fcst_var_names': ['UGRD_VGRD'],
                                      'fcst_var_levels': [
                                          'P1000', 'P925', 'P850', 'P700', 
                                          'P500', 'P400','P300', 'P250', 
                                          'P200', 'P150', 'P100', 'P50', 
                                          'P10', 'P5', 'P1'
                                      ],
                                      'fcst_var_thresholds': '',
                                      'fcst_var_options': '',
                                      'obs_var_names': ['UGRD_VGRD'],
                                      'obs_var_levels': [
                                          'P1000', 'P925', 'P850', 'P700', 
                                          'P500', 'P400', 'P300', 'P250', 
                                          'P200', 'P150', 'P100', 'P50', 
                                          'P10', 'P5', 'P1'
                                      ],
                                      'obs_var_thresholds': '',
                                      'obs_var_options': '',
                                      'plot_group':'sfc_upper'}
                    }
                }
            },
            'grid2obs_raob': {
                'SL1L2': {
                    'plot_stats_list': ('bcrmse, me, fbar_obar, fbar,'
                                        + ' obar'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South',
                        'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 
                        'Mezquital', 'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies',
                        'PacificNW', 'PacificSW', 'Prairie', 'Southeast', 'SPlains', 'SRockies',
                        'Alaska', 'Hawaii', 'PuertoRico', 'Guam', 'FireWx', 'DAY1_1200_TSTM',
                        'DAY1_0100_TSTM'
                    ],
                    'var_dict': {
                        'HGT': {'fcst_var_names': ['HGT'],
                                'fcst_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                    'P900', 'P875', 'P850', 'P825',
                                                    'P800', 'P775', 'P750', 'P725',
                                                    'P700', 'P675', 'P650', 'P625',
                                                    'P600', 'P575', 'P550', 'P525',
                                                    'P500', 'P475', 'P450', 'P425',
                                                    'P400', 'P375', 'P350', 'P325',
                                                    'P300', 'P275', 'P250', 'P225', 
                                                    'P200', 'P175', 'P150', 'P125',
                                                    'P100', 'P75', 'P50', 'P30', 
                                                    'P20', 'P10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['HGT'],
                                'obs_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                    'P900', 'P875', 'P850', 'P825',
                                                    'P800', 'P775', 'P750', 'P725',
                                                    'P700', 'P675', 'P650', 'P625',
                                                    'P600', 'P575', 'P550', 'P525',
                                                    'P500', 'P475', 'P450', 'P425',
                                                    'P400', 'P375', 'P350', 'P325',
                                                    'P300', 'P275', 'P250', 'P225', 
                                                    'P200', 'P175', 'P150', 'P125',
                                                    'P100', 'P75', 'P50', 'P30', 
                                                    'P20', 'P10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'TMP': {'fcst_var_names': ['TMP'],
                                'fcst_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                    'P900', 'P875', 'P850', 'P825',
                                                    'P800', 'P775', 'P750', 'P725',
                                                    'P700', 'P675', 'P650', 'P625',
                                                    'P600', 'P575', 'P550', 'P525',
                                                    'P500', 'P475', 'P450', 'P425',
                                                    'P400', 'P375', 'P350', 'P325',
                                                    'P300', 'P275', 'P250', 'P225', 
                                                    'P200', 'P175', 'P150', 'P125',
                                                    'P100', 'P75', 'P50', 'P30', 
                                                    'P20', 'P10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['TMP'],
                                'obs_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                    'P900', 'P875', 'P850', 'P825',
                                                    'P800', 'P775', 'P750', 'P725',
                                                    'P700', 'P675', 'P650', 'P625',
                                                    'P600', 'P575', 'P550', 'P525',
                                                    'P500', 'P475', 'P450', 'P425',
                                                    'P400', 'P375', 'P350', 'P325',
                                                    'P300', 'P275', 'P250', 'P225', 
                                                    'P200', 'P175', 'P150', 'P125',
                                                    'P100', 'P75', 'P50', 'P30', 
                                                    'P20', 'P10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'UGRD': {'fcst_var_names': ['UGRD'],
                                'fcst_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                    'P900', 'P875', 'P850', 'P825',
                                                    'P800', 'P775', 'P750', 'P725',
                                                    'P700', 'P675', 'P650', 'P625',
                                                    'P600', 'P575', 'P550', 'P525',
                                                    'P500', 'P475', 'P450', 'P425',
                                                    'P400', 'P375', 'P350', 'P325',
                                                    'P300', 'P275', 'P250', 'P225', 
                                                    'P200', 'P175', 'P150', 'P125',
                                                    'P100', 'P75', 'P50', 'P30', 
                                                    'P20', 'P10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['UGRD'],
                                'obs_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                    'P900', 'P875', 'P850', 'P825',
                                                    'P800', 'P775', 'P750', 'P725',
                                                    'P700', 'P675', 'P650', 'P625',
                                                    'P600', 'P575', 'P550', 'P525',
                                                    'P500', 'P475', 'P450', 'P425',
                                                    'P400', 'P375', 'P350', 'P325',
                                                    'P300', 'P275', 'P250', 'P225', 
                                                    'P200', 'P175', 'P150', 'P125',
                                                    'P100', 'P75', 'P50', 'P30', 
                                                    'P20', 'P10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'VGRD': {'fcst_var_names': ['VGRD'],
                                'fcst_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                    'P900', 'P875', 'P850', 'P825',
                                                    'P800', 'P775', 'P750', 'P725',
                                                    'P700', 'P675', 'P650', 'P625',
                                                    'P600', 'P575', 'P550', 'P525',
                                                    'P500', 'P475', 'P450', 'P425',
                                                    'P400', 'P375', 'P350', 'P325',
                                                    'P300', 'P275', 'P250', 'P225', 
                                                    'P200', 'P175', 'P150', 'P125',
                                                    'P100', 'P75', 'P50', 'P30', 
                                                    'P20', 'P10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['VGRD'],
                                'obs_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                    'P900', 'P875', 'P850', 'P825',
                                                    'P800', 'P775', 'P750', 'P725',
                                                    'P700', 'P675', 'P650', 'P625',
                                                    'P600', 'P575', 'P550', 'P525',
                                                    'P500', 'P475', 'P450', 'P425',
                                                    'P400', 'P375', 'P350', 'P325',
                                                    'P300', 'P275', 'P250', 'P225', 
                                                    'P200', 'P175', 'P150', 'P125',
                                                    'P100', 'P75', 'P50', 'P30', 
                                                    'P20', 'P10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'SPFH': {'fcst_var_names': ['SPFH'],
                                 'fcst_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                     'P900', 'P875', 'P850', 'P825',
                                                     'P800', 'P775', 'P750', 'P725',
                                                     'P700', 'P675', 'P650', 'P625',
                                                     'P600', 'P575', 'P550', 'P525',
                                                     'P500', 'P475', 'P450', 'P425',
                                                     'P400', 'P375', 'P350', 'P325',
                                                     'P300', 'P275', 'P250', 'P225', 
                                                     'P200', 'P175', 'P150', 'P125',
                                                     'P100', 'P75', 'P50', 'P30', 
                                                     'P20', 'P10'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['SPFH'],
                                 'obs_var_levels': ['P1000', 'P975', 'P950', 'P925', 
                                                     'P900', 'P875', 'P850', 'P825',
                                                     'P800', 'P775', 'P750', 'P725',
                                                     'P700', 'P675', 'P650', 'P625',
                                                     'P600', 'P575', 'P550', 'P525',
                                                     'P500', 'P475', 'P450', 'P425',
                                                     'P400', 'P375', 'P350', 'P325',
                                                     'P300', 'P275', 'P250', 'P225', 
                                                     'P200', 'P175', 'P150', 'P125',
                                                     'P100', 'P75', 'P50', 'P30', 
                                                     'P20', 'P10'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'SBCAPE': {'fcst_var_names': ['CAPE'],
                                    'fcst_var_levels': ['L0'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['CAPE'],
                                    'obs_var_levels': ['L100000-0'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'cape'},
                        'MLCAPE': {'fcst_var_names': ['CAPE'],
                                    'fcst_var_levels': ['P90-0'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['MLCAPE'],
                                    'obs_var_levels': ['L90000-0'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'cape'},
                        'HPBL': {'fcst_var_names': ['HGT','HPBL'],
                                 'fcst_var_levels': ['L0','PBL'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['HPBL'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                    }
                },
                'VL1L2': {
                    'plot_stats_list': ('me, rmse, bcrmse, fbar_obar, fbar,'
                                        + ' obar'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South',
                        'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 
                        'Mezquital', 'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies',
                        'PacificNW', 'PacificSW', 'Prairie', 'Southeast', 'SPlains', 'SRockies',
                        'Alaska', 'Hawaii', 'PuertoRico', 'Guam', 'FireWx', 'DAY1_1200_TSTM',
                        'DAY1_0100_TSTM'
                    ],
                    'var_dict': {
                        'UGRD_VGRD': {'fcst_var_names': ['UGRD_VGRD'],
                                      'fcst_var_levels': [
                                          'P1000', 'P975', 'P950', 'P925', 
                                          'P900', 'P875', 'P850', 'P825',
                                          'P800', 'P775', 'P750', 'P725',
                                          'P700', 'P675', 'P650', 'P625',
                                          'P600', 'P575', 'P550', 'P525',
                                          'P500', 'P475', 'P450', 'P425',
                                          'P400', 'P375', 'P350', 'P325',
                                          'P300', 'P275', 'P250', 'P225', 
                                          'P200', 'P175', 'P150', 'P125',
                                          'P100', 'P75', 'P50', 'P30', 
                                          'P20', 'P10'
                                      ],
                                      'fcst_var_thresholds': '',
                                      'fcst_var_options': '',
                                      'obs_var_names': ['UGRD_VGRD'],
                                      'obs_var_levels': [
                                          'P1000', 'P975', 'P950', 'P925', 
                                          'P900', 'P875', 'P850', 'P825',
                                          'P800', 'P775', 'P750', 'P725',
                                          'P700', 'P675', 'P650', 'P625',
                                          'P600', 'P575', 'P550', 'P525',
                                          'P500', 'P475', 'P450', 'P425',
                                          'P400', 'P375', 'P350', 'P325',
                                          'P300', 'P275', 'P250', 'P225', 
                                          'P200', 'P175', 'P150', 'P125',
                                          'P100', 'P75', 'P50', 'P30', 
                                          'P20', 'P10'
                                      ],
                                      'obs_var_thresholds': '',
                                      'obs_var_options': '',
                                      'plot_group':'sfc_upper'}
                    }
                },
                'CTC': {
                    'plot_stats_list': ('csi, fbias, pod,'
                                        + ' faratio, sratio'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South',
                        'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 
                        'Mezquital', 'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies',
                        'PacificNW', 'PacificSW', 'Prairie', 'Southeast', 'SPlains', 'SRockies',
                        'Alaska', 'Hawaii', 'PuertoRico', 'Guam', 'FireWx', 'DAY1_1200_TSTM',
                        'DAY1_0100_TSTM'
                    ],
                    'var_dict': {
                        'SBCAPE': {'fcst_var_names': ['CAPE'],
                                    'fcst_var_levels': ['L0'],
                                    'fcst_var_thresholds': ('>=250, >=500, >=1000,'
                                                            + ' >=1500, >=2000,'
                                                            + ' >=3000,'
                                                            + ' >=4000'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['CAPE'],
                                    'obs_var_levels': ['L100000-0'],
                                    'obs_var_thresholds': ('>=250, >=500, >=1000,'
                                                          + ' >=1500, >=2000,'
                                                          + ' >=3000,'
                                                          + ' >=4000'),
                                    'obs_var_options': '',
                                    'plot_group':'cape'},
                        'MLCAPE': {'fcst_var_names': ['CAPE'],
                                    'fcst_var_levels': ['P90-0'],
                                    'fcst_var_thresholds': ('>=250, >=500, >=1000,'
                                                            + ' >=1500, >=2000,'
                                                            + ' >=3000,'
                                                            + ' >=4000'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['MLCAPE'],
                                    'obs_var_levels': ['L90000-0'],
                                    'obs_var_thresholds': ('>=250, >=500, >=1000,'
                                                          + ' >=1500, >=2000,'
                                                          + ' >=3000,'
                                                          + ' >=4000'),
                                    'obs_var_options': '',
                                    'plot_group':'cape'},
                        'HPBL': {'fcst_var_names': ['HGT','HPBL'],
                                 'fcst_var_levels': ['L0','PBL'],
                                 'fcst_var_thresholds': '<=500, >=2000',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['HPBL'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '<=500, >=2000',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                    }
                }
            },
            'grid2obs_metar': {
                'SL1L2': {
                    'plot_stats_list': ('bcrmse, me'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South',
                        'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 
                        'Mezquital', 'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies',
                        'PacificNW', 'PacificSW', 'Prairie', 'Southeast', 'SPlains', 'SRockies',
                        'Alaska', 'Hawaii', 'PuertoRico', 'Guam', 'FireWx', 'DAY1_1200_TSTM',
                        'DAY1_0100_TSTM'
                    ],
                    'var_dict': {
                        'TMP2m': {'fcst_var_names': ['TMP'],
                                  'fcst_var_levels': ['Z2'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['TMP'],
                                  'obs_var_levels': ['Z2'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'DPT2m': {'fcst_var_names': ['DPT'],
                                  'fcst_var_levels': ['Z2'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['DPT'],
                                  'obs_var_levels': ['Z2'],
                                  'obs_var_thresholds': '>=277.594,>=283.15,>=288.706,>=294.261',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'RH2m': {'fcst_var_names': ['RH'],
                                 'fcst_var_levels': ['Z2'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['RH'],
                                 'obs_var_levels': ['Z2'],
                                 'obs_var_thresholds': '<=15,<=20,<=25,<=30',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'MSLP': {'fcst_var_names': ['MSLET','MSLMA'],
                                  'fcst_var_levels': ['Z0'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['PRMSL'],
                                  'obs_var_levels': ['Z0'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'UGRD10m': {'fcst_var_names': ['UGRD'],
                                    'fcst_var_levels': ['Z10'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['UGRD'],
                                    'obs_var_levels': ['Z10'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'VGRD10m': {'fcst_var_names': ['VGRD'],
                                    'fcst_var_levels': ['Z10'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['VGRD'],
                                    'obs_var_levels': ['Z10'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'WIND10m': {'fcst_var_names': ['WIND'],
                                    'fcst_var_levels': ['Z10'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['WIND'],
                                    'obs_var_levels': ['Z10'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'GUSTsfc': {'fcst_var_names': ['GUST'],
                                    'fcst_var_levels': ['Z0'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['GUST'],
                                    'obs_var_levels': ['Z0'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                    }
                },
                'VL1L2': {
                    'plot_stats_list': ('bcrmse, me'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South',
                        'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 
                        'Mezquital', 'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies',
                        'PacificNW', 'PacificSW', 'Prairie', 'Southeast', 'SPlains', 'SRockies',
                        'Alaska', 'Hawaii', 'PuertoRico', 'Guam', 'FireWx', 'DAY1_1200_TSTM',
                        'DAY1_0100_TSTM'
                    ],
                    'var_dict': {
                        'UGRD_VGRD10m': {'fcst_var_names': ['UGRD_VGRD'],
                                         'fcst_var_levels': ['Z10'],
                                         'fcst_var_thresholds': '',
                                         'fcst_var_options': '',
                                         'obs_var_names': ['UGRD_VGRD'],
                                         'obs_var_levels': ['Z10'],
                                         'obs_var_thresholds': '',
                                         'obs_var_options': '',
                                         'plot_group':'sfc_upper'},
                    }
                },
                'CTC': {
                    'plot_stats_list': ('csi, ets, fbias, pod,'
                                        + ' faratio, sratio'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South',
                        'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 
                        'Mezquital', 'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies',
                        'PacificNW', 'PacificSW', 'Prairie', 'Southeast', 'SPlains', 'SRockies',
                        'Alaska', 'Hawaii', 'PuertoRico', 'Guam', 'FireWx', 'DAY1_1200_TSTM',
                        'DAY1_0100_TSTM'
                    ],
                    'var_dict': {
                       'DPT2m': {'fcst_var_names': ['DPT'],
                                 'fcst_var_levels': ['Z2'],
                                 'fcst_var_thresholds': (' >=277.594, >=283.15,'
                                                         + ' >=288.706, >=294.261'),
                                 'fcst_var_options': '',
                                 'obs_var_names': ['DPT'],
                                 'obs_var_levels': ['Z2'],
                                 'obs_var_thresholds': (' >=277.594, >=283.15,'
                                                        + ' >=288.706, >=294.261'),
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                       'RH2m': {'fcst_var_names': ['RH'],
                                 'fcst_var_levels': ['Z2'],
                                 'fcst_var_thresholds': (' <=15, >=15, <=20, >=20, '
                                                         + ' <=25, >=25, <=30, >=30'),
                                 'fcst_var_options': '',
                                 'obs_var_names': ['RH'],
                                 'obs_var_levels': ['Z2'],
                                 'obs_var_thresholds': (' <=15, >=15, <=20, >=20, '
                                                        + ' <=25, >=25, <=30, >=30'),
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'VIS': {'fcst_var_names': ['VIS'],
                                   'fcst_var_levels': ['Z0'],
                                   'fcst_var_thresholds': ('<=805, <=1609,'
                                                           + ' <=4828, <=8045,'
                                                           + ' >=8045,'
                                                           + ' <=16090'),
                                   'fcst_var_options': '',
                                   'obs_var_names': ['VIS'],
                                   'obs_var_levels': ['Z0'],
                                   'obs_var_thresholds': ('<=805, <=1609,'
                                                          + ' <=4828, <=8045,'
                                                          + ' >=8045,'
                                                          + ' <=16090'),
                                   'obs_var_options': '',
                                   'plot_group':'ceil_vis'},
                        'CEILING': {'fcst_var_names': ['HGT'],
                                       'fcst_var_levels': ['L0','CEILING'],
                                       'fcst_var_thresholds': ('<=152,'
                                                               + ' <=305,'
                                                               + ' >=914, <=914,'
                                                               + ' <=1524, '
                                                               + ' <=3048'),
                                       'fcst_var_options': ('GRIB_lvl_typ ='
                                                            + ' 215;'),
                                       'obs_var_names': ['CEILING','HGT'],
                                       'obs_var_levels': ['L0'],
                                       'obs_var_thresholds': ('<=152,'
                                                              + ' <=305,'
                                                              + ' >=914, <=914,'
                                                              + ' <=1524, '
                                                              + ' <=3048'),
                                       'obs_var_options': '',
                                       'plot_group':'ceil_vis'},
                        'TCDC': {'fcst_var_names': ['TCDC'],
                                 'fcst_var_levels': ['L0','TOTAL'],
                                 'fcst_var_thresholds': '<10, >10, >50, >90',
                                 'fcst_var_options': 'GRIB_lvl_typ = 200;',
                                 'obs_var_names': ['TCDC'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '<10, >10, >50, >90',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                    }
                },
                'CNT': {
                    'plot_stats_list': ('fss'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South',
                        'Appalachia', 'CPlains', 'DeepSouth', 'GreatBasin', 'GreatLakes', 
                        'Mezquital', 'MidAtlantic', 'NorthAtlantic', 'NPlains', 'NRockies',
                        'PacificNW', 'PacificSW', 'Prairie', 'Southeast', 'SPlains', 'SRockies',
                        'Alaska', 'Hawaii', 'PuertoRico', 'Guam', 'FireWx', 'DAY1_1200_TSTM',
                        'DAY1_0100_TSTM'
                    ],
                    'var_dict': {
                        'TCDC': {'fcst_var_names': ['TCDC'],
                                 'fcst_var_levels': ['L0','TOTAL'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['TCDC'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                    }
                },
            },
            'grid2obs_ptype': {
                'MCTC': {
                    'plot_stats_list': ('csi, ets, fbias, pod,'
                                        + ' faratio, sratio'),
                    'interp': 'BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 'CONUS_South',
                        'Alaska',
                    ],
                    'var_dict': {
                        'PTYPE': {'fcst_var_names': ['PTYPE'],
                                 'fcst_var_levels': ['Z0'],
                                 'fcst_var_thresholds': '>=1.0,>=2.0,>=3.0,>=4.0',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['PTYPE','PRWE'],
                                 'obs_var_levels': ['Z0'],
                                 'obs_var_thresholds': '>=1.0,>=2.0,>=3.0,>=4.0',
                                 'obs_var_options': '',
                                 'plot_group':'precip'},
                    }
                },
            },
            'grid2obs_conus_sfc': {
                'SL1L2': {
                    'plot_stats_list': ('me, rmse, bcrmse, fbar_obar, fbar,'
                                        + ' obar'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'G130', 'G214', 'WEST', 'EAST', 'MDW', 'NPL', 'SPL', 'NEC', 
                        'SEC', 'NWC', 'SWC', 'NMT', 'SMT', 'SWD', 'GRB', 
                        'LMV', 'GMC', 'APL', 'NAK', 'SAK', 'FireWx'
                    ],
                    'var_dict': {
                        'TMP2m': {'fcst_var_names': ['TMP'],
                                  'fcst_var_levels': ['Z2'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['TMP'],
                                  'obs_var_levels': ['Z2'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'RH2m': {'fcst_var_names': ['RH'],
                                 'fcst_var_levels': ['Z2'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['RH'],
                                 'obs_var_levels': ['Z2'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'DPT2m': {'fcst_var_names': ['DPT'],
                                  'fcst_var_levels': ['Z2'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['TDO'],
                                  'obs_var_levels': ['Z2'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'TCDC': {'fcst_var_names': ['TCDC'],
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': 'GRIB_lvl_typ = 200;',
                                 'obs_var_names': ['TCDC'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'PRMSL': {'fcst_var_names': ['PRMSL'],
                                  'fcst_var_levels': ['Z0'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['PRMSL'],
                                  'obs_var_levels': ['Z0'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'VISsfc': {'fcst_var_names': ['VIS'],
                                   'fcst_var_levels': ['L0'],
                                   'fcst_var_thresholds': '',
                                   'fcst_var_options': '',
                                   'obs_var_names': ['VIS'],
                                   'obs_var_levels': ['L0'],
                                   'obs_var_thresholds': '',
                                   'obs_var_options': '',
                                   'plot_group':'ceil_vis'},
                        'HGTcldceil': {'fcst_var_names': ['HGT'],
                                       'fcst_var_levels': ['L0'],
                                       'fcst_var_thresholds': '',
                                       'fcst_var_options': ('GRIB_lvl_typ ='
                                                            + ' 215;'),
                                       'obs_var_names': ['CEILING','HGT'],
                                       'obs_var_levels': ['L0'],
                                       'obs_var_thresholds': '',
                                       'obs_var_options': '',
                                       'plot_group':'ceil_vis'},
                        'CAPEsfc': {'fcst_var_names': ['CAPE'],
                                    'fcst_var_levels': ['L0'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['CAPE'],
                                    'obs_var_levels': ['L100000-0'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'cape'},
                        'GUSTsfc': {'fcst_var_names': ['GUST'],
                                    'fcst_var_levels': ['Z0'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['MXGS'],
                                    'obs_var_levels': ['Z0'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'HPBL': {'fcst_var_names': ['HPBL'],
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['HPBL'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'PBL': {'fcst_var_names': ['HGT'],
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['PBL'],
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'},
                        'UGRD10m': {'fcst_var_names': ['UGRD'],
                                    'fcst_var_levels': ['Z10'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['UGRD'],
                                    'obs_var_levels': ['Z10'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'VGRD10m': {'fcst_var_names': ['VGRD'],
                                    'fcst_var_levels': ['Z10'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['VGRD'],
                                    'obs_var_levels': ['Z10'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                        'WIND10m': {'fcst_var_names': ['WIND'],
                                    'fcst_var_levels': ['Z10'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['WIND'],
                                    'obs_var_levels': ['Z10'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'},
                    }
                },
                'VL1L2': {
                    'plot_stats_list': ('me, rmse, bcrmse, fbar_obar, fbar,'
                                        + ' obar'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'G130', 'G214', 'WEST', 'EAST', 'MDW', 'NPL', 'SPL', 'NEC', 
                        'SEC', 'NWC', 'SWC', 'NMT', 'SMT', 'SWD', 'GRB', 
                        'LMV', 'GMC', 'APL', 'NAK', 'SAK', 'FireWx'
                    ],
                    'var_dict': {
                        'UGRD_VGRD10m': {'fcst_var_names': ['UGRD_VGRD'],
                                         'fcst_var_levels': ['Z10'],
                                         'fcst_var_thresholds': '',
                                         'fcst_var_options': '',
                                         'obs_var_names': ['UGRD_VGRD'],
                                         'obs_var_levels': ['Z10'],
                                         'obs_var_thresholds': '',
                                         'obs_var_options': '',
                                         'plot_group':'sfc_upper'},
                    }
                },
                'CTC': {
                    'plot_stats_list': ('csi, fbias, fss, pod,'
                                        + ' faratio, sratio'),
                    'interp': 'NEAREST, BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'G130', 'G214', 'G221', 'WEST', 'EAST', 'MDW', 'NPL', 'SPL', 'NEC', 
                        'SEC', 'NWC', 'SWC', 'NMT', 'SMT', 'SWD', 'GRB', 
                        'LMV', 'GMC', 'APL', 'NAK', 'SAK', 'FireWx'
                    ],
                    'var_dict': {
                         'RH2m': {'fcst_var_names': ['RH'],
                                  'fcst_var_levels': ['Z2'],
                                  'fcst_var_thresholds': (' <=15, <=20,'
                                                          + ' <=25, <=30'),
                                  'fcst_var_options': '',
                                  'obs_var_names': ['RH'],
                                  'obs_var_levels': ['Z2'],
                                  'obs_var_thresholds': (' <=15, <=20,'
                                                         + ' <=25, <=30'),
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                         'DPT2m': {'fcst_var_names': ['DPT'],
                                  'fcst_var_levels': ['Z2'],
                                  'fcst_var_thresholds': '>=277.59,>=283.15,>=288.7,>=294.26',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['TDO'],
                                  'obs_var_levels': ['Z2'],
                                  'obs_var_thresholds': '>=277.59,>=283.15,>=288.7,>=294.26',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'VISsfc': {'fcst_var_names': ['VIS'],
                                   'fcst_var_levels': ['L0'],
                                   'fcst_var_thresholds': ('<=800, <805, <=1600, <1609,'
                                                           + ' <=4800, <4828, <=8000, <8045,'
                                                           + ' >=8045,'
                                                           + ' <=16000, <16090'),
                                   'fcst_var_options': '',
                                   'obs_var_names': ['VIS'],
                                   'obs_var_levels': ['L0'],
                                   'obs_var_thresholds': ('<=800, <805, <=1600, <1609,'
                                                          + ' <=4800, <4828, <=8000, <8045,'
                                                          + ' >=8045,'
                                                          + ' <=16000, <16090'),
                                   'obs_var_options': '',
                                   'plot_group':'ceil_vis'},
                        'HGTcldceil': {'fcst_var_names': ['HGT'],
                                       'fcst_var_levels': ['L0'],
                                       'fcst_var_thresholds': ('<152, <=152, <305,'
                                                               + ' <=305, <914,'
                                                               + ' >=914, <=916,'
                                                               + ' <1520, <=1524, '
                                                               + ' <3040, <=3048'),
                                       'fcst_var_options': ('GRIB_lvl_typ ='
                                                            + ' 215;'),
                                       'obs_var_names': ['CEILING','HGT'],
                                       'obs_var_levels': ['L0'],
                                       'obs_var_thresholds': ('<152, <=152, <305,'
                                                              + ' <=305, <914, '
                                                              + '>=914, <=916, '
                                                              + '<1520, <=1524, '
                                                              + '<3040, <=3048'),
                                       'obs_var_options': '',
                                       'plot_group':'ceil_vis'},
                        'CAPEsfc': {'fcst_var_names': ['CAPE'],
                                    'fcst_var_levels': ['L0'],
                                    'fcst_var_thresholds': ('>500, >1000,'
                                                            + ' >1500, >2000,'
                                                            + ' >3000,'
                                                            + ' >4000'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['CAPE'],
                                    'obs_var_levels': ['L100000-0'],
                                    'obs_var_thresholds': ('>500, >1000,'
                                                           + ' >1500, >2000,'
                                                           + ' >3000,'
                                                           + ' >4000'),
                                    'obs_var_options': '',
                                    'plot_group':'cape'},
                    }
                }
            },
            'grid2obs_aq': {
                'CTC': {
                    'plot_stats_list': ('csi, fbias, fss, pod,'
                                        + ' faratio, sratio'),
                    'interp': 'BILIN',
                    'vx_mask_list' : [
                        'CONUS', 'G130', 'G214', 'WEST', 'EAST', 'MDW', 'NPL', 'SPL', 'NEC', 
                        'SEC', 'NWC', 'SWC', 'NMT', 'SMT', 'SWD', 'GRB', 
                        'LMV', 'GMC', 'APL', 'NAK', 'SAK'
                    ],
                    'var_dict': {
                        'OZCON1': {'fcst_var_names': ['OZCON1'],
                                  'fcst_var_levels': ['A1'],
                                  'fcst_var_thresholds': ('>50, >60, >65, >70,'
                                                          + '>75, >85, >105,'
                                                          + '>125, >150'),
                                  'fcst_var_options': '',
                                  'obs_var_names': ['COPO'],
                                  'obs_var_levels': ['A1'],
                                  'obs_var_thresholds': ('>50, >60, >65, >70,'
                                                         + '>75, >85, >105,'
                                                         + '>125, >150'),
                                  'obs_var_options': '',
                                  'plot_group':'aq'},
                        'OZCON8': {'fcst_var_names': ['OZCON8'],
                                  'fcst_var_levels': ['A8'],
                                  'fcst_var_thresholds': ('>50, >60, >65, >70,'
                                                          + '>75, >85, >105,'
                                                          + '>125, >150'),
                                  'fcst_var_options': '',
                                  'obs_var_names': ['COPO'],
                                  'obs_var_levels': ['A8'],
                                  'obs_var_thresholds': ('>50, >60, >65, >70,'
                                                         + '>75, >85, >105,'
                                                         + '>125, >150'),
                                  'obs_var_options': '',
                                  'plot_group':'aq'},
                    }
                }
            },
            'grid2obs_polar_sfc': {
                'SL1L2': {
                    'plot_stats_list': 'me, rmse, fbar_obar',
                    'interp': 'NEAREST',
                    'vx_mask_list' : ['ARCTIC'],
                    'var_dict': {
                        'TMP2m': {'fcst_var_names': ['TMP'],
                                  'fcst_var_levels': ['Z2'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['TMP'],
                                  'obs_var_levels': ['Z2'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'sfc_upper'},
                        'TMPsfc': {'fcst_var_names': ['TMP'],
                                   'fcst_var_levels': ['Z0'],
                                   'fcst_var_thresholds': '',
                                   'fcst_var_options': '',
                                   'obs_var_names': ['TMP'],
                                   'obs_var_levels': ['Z0'],
                                   'obs_var_thresholds': '',
                                   'obs_var_options': '',
                                   'plot_group':'sfc_upper'},
                        'PRESsfc': {'fcst_var_names': ['PRES'],
                                    'fcst_var_levels': ['Z0'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['PRES'],
                                    'obs_var_levels': ['Z0'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'sfc_upper'}
                    }
                }
            },
            'grid2grid_rtofs_sfc': {
                'SL1L2': {
                    'plot_stats_list': 'me, rmse, fbar_obar, estdev',
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'Global','North_Atlantic','South_Atlantic','Equatorial_Atlantic',
                        'North_Pacific','South_Pacific','Equatorial_Pacific','Indian',
                        'Southern','Arctic','Mediterranean','Antarctic'
                    ],
                    'var_dict': {
                        'SST': {'fcst_var_names': ['sst'],
                                  'fcst_var_levels': ['0,*,*'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['analysed_sst'],
                                  'obs_var_levels': ['0,*,*'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'rtofs_sfc'},
                        'SSS': {'fcst_var_names': ['sss'],
                                  'fcst_var_levels': ['0,*,*'],
                                  'fcst_var_thresholds':'',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['sss'],
                                  'obs_var_levels': ['0,0,*,*'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group': 'rtofs_sfc'},
                        'SSH': {'fcst_var_names': ['ssh'],
                                   'fcst_var_levels': ['0,*,*'],
                                   'fcst_var_thresholds': '',
                                   'fcst_var_options': '',
                                   'obs_var_names': ['adt'],
                                   'obs_var_levels': ['0,*,*'],
                                   'obs_var_thresholds': '',
                                   'obs_var_options': '',
                                   'plot_group':'rtofs_sfc'},
                        'SIC': {'fcst_var_names': ['ice_coverage'],
                                    'fcst_var_levels': ['0,*,*'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['ice_conc'],
                                    'obs_var_levels': ['0,*,*'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'rtofs_sfc'}
                    }
                },
                'SAL1L2': {
                    'plot_stats_list': 'acc',
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'Global','North_Atlantic','South_Atlantic','Equatorial_Atlantic',
                        'North_Pacific','South_Pacific','Equatorial_Pacific','Indian',
                        'Southern','Arctic','Mediterranean'
                    ],
                    'var_dict': {
                        'SST': {'fcst_var_names': ['sst'],
                                  'fcst_var_levels': ['0,*,*'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['analysed_sst'],
                                  'obs_var_levels': ['0,*,*'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group':'rtofs_sfc'},
                        'SSS': {'fcst_var_names': ['sss'],
                                  'fcst_var_levels': ['0,*,*'],
                                  'fcst_var_thresholds':'',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['sss'],
                                  'obs_var_levels': ['0,0,*,*'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': '',
                                  'plot_group': 'rtofs_sfc'},
                        'SSH': {'fcst_var_names': ['ssh'],
                                   'fcst_var_levels': ['0,*,*'],
                                   'fcst_var_thresholds': '',
                                   'fcst_var_options': '',
                                   'obs_var_names': ['adt'],
                                   'obs_var_levels': ['0,*,*'],
                                   'obs_var_thresholds': '',
                                   'obs_var_options': '',
                                   'plot_group':'rtofs_sfc'},
                        'SIC': {'fcst_var_names': ['ice_coverage'],
                                    'fcst_var_levels': ['0,*,*'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['ice_conc'],
                                    'obs_var_levels': ['0,*,*'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'rtofs_sfc'}
                    }
                },
                'CTC': {
                    'plot_stats_list': 'sratio, pod, csi, hss',
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'Global','North_Atlantic','South_Atlantic','Equatorial_Atlantic',
                        'North_Pacific','South_Pacific','Equatorial_Pacific','Indian',
                        'Southern','Arctic','Mediterranean','Antarctic'
                    ],
                    'var_dict': {
                        'SST': {'fcst_var_names': ['sst'],
                                  'fcst_var_levels': ['0,*,*'],
                                  'fcst_var_thresholds': '>=0, >=26.5',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['analysed_sst'],
                                  'obs_var_levels': ['0,*,*'],
                                  'obs_var_thresholds': '>=0, >=26.5',
                                  'obs_var_options': '',
                                  'plot_group':'rtofs_sfc'},
                        'SIC': {'fcst_var_names': ['ice_coverage'],
                                    'fcst_var_levels': ['0,*,*'],
                                    'fcst_var_thresholds': '>=15, >=40, >=80',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['ice_conc'],
                                    'obs_var_levels': ['0,*,*'],
                                    'obs_var_thresholds': '>=15, >=40, >=80',
                                    'obs_var_options': '',
                                    'plot_group':'rtofs_sfc'}
                    }
                }
            },
            'precip_ccpa': {
                'SL1L2': {
                    'plot_stats_list': ('me, rmse, bcrmse, fbar_obar, fbar,'
                                        + ' obar'),
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 
                        'CONUS_South', 
                    ],
                    'var_dict': {
                        'APCP_01': {'fcst_var_names': ['APCP_01'],
                                    'fcst_var_levels': ['A01','A1'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_01', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A01','A1'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_03': {'fcst_var_names': ['APCP_03'],
                                    'fcst_var_levels': ['A03','A3'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_03', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A03','A3'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_06': {'fcst_var_names': ['APCP_06'],
                                    'fcst_var_levels': ['A06','A6'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_06', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A06','A6'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_24': {'fcst_var_names': ['APCP_24'],
                                    'fcst_var_levels': ['A24'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_24', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A24'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'precip'}
                    }
                },
                'NBRCNT': {
                    'plot_stats_list': ('fss, afss, ufss, frate, orate'),
                    'interp': 'NBRHD_SQUARE, NBRHD_CIRCLE',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 
                        'CONUS_South', 'Alaska', 
                    ],
                    'var_dict': {
                        'APCP_01': {'fcst_var_names': ['APCP_01'],
                                    'fcst_var_levels': ['A01','A1'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_01', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A01','A1'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_03': {'fcst_var_names': ['APCP_03'],
                                    'fcst_var_levels': ['A03','A3'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_03', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A03','A3'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_06': {'fcst_var_names': ['APCP_06'],
                                    'fcst_var_levels': ['A06','A6'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_06', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A06','A6'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_24': {'fcst_var_names': ['APCP_24'],
                                    'fcst_var_levels': ['A24'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_24', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A24'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'}
                    }
                },
                'CTC': {
                    'plot_stats_list': ('me, ets, fss, csi, fbias, fbar,'
                                        + ' obar, pod, faratio, farate, sratio'),
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'CONUS', 'CONUS_East', 'CONUS_West', 'CONUS_Central', 
                        'CONUS_South', 'G130', 'G214', 'WEST', 'EAST', 'MDW', 'NPL', 'SPL', 'NEC', 
                        'SEC', 'NWC', 'SWC', 'NMT', 'SMT', 'SWD', 'GRB', 
                        'LMV', 'GMC', 'APL', 'NAK', 'SAK'
                    ],
                    'var_dict': {
                        'APCP_01': {'fcst_var_names': ['APCP_01'],
                                    'fcst_var_levels': ['A01','A1'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_01', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A01','A1'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_03': {'fcst_var_names': ['APCP_03'],
                                    'fcst_var_levels': ['A03','A3'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'
                                                            + ' >=50.8,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_03', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A03','A3'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'
                                                           + ' >=50.8,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_06': {'fcst_var_names': ['APCP_06'],
                                    'fcst_var_levels': ['A06','A6'],
                                    'fcst_var_thresholds': ('>=0.254, >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'
                                                            + ' >=38.1,'
                                                            + ' >=50.8,'
                                                            + ' >=76.2,'
                                                            + ' >=101.6'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_06', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A06','A6'],
                                    'obs_var_thresholds': ('>=0.254, >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'
                                                           + ' >=38.1,'
                                                           + ' >=50.8,'
                                                           + ' >=76.2,'
                                                           + ' >=101.6'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_24': {'fcst_var_names': ['APCP_24'],
                                    'fcst_var_levels': ['A24'],
                                    'fcst_var_thresholds': ('>=0.254, >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=25.4,'
                                                            + ' >=38.1,'
                                                            + ' >=50.8,'
                                                            + ' >=76.2,'
                                                            + ' >=101.6'
                                                            + ' >=152.4'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_24', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A24'],
                                    'obs_var_thresholds': ('>=0.254, >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=25.4,'
                                                           + ' >=38.1,'
                                                           + ' >=50.8,'
                                                           + ' >=76.2,'
                                                           + ' >=101.6'
                                                           + ' >=152.4'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'}
                    }
                }
            },
            'precip_mrms': {
                'SL1L2': {
                    'plot_stats_list': ('me, rmse, bcrmse, fbar_obar, fbar,'
                                        + ' obar'),
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'Alaska', 'PuertoRico', 'Hawaii'
                    ],
                    'var_dict': {
                        'APCP_01': {'fcst_var_names': ['APCP_01'],
                                    'fcst_var_levels': ['A01','A1'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_01', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A01','A1'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_03': {'fcst_var_names': ['APCP_03'],
                                    'fcst_var_levels': ['A03','A3'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_03', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A03','A3'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_06': {'fcst_var_names': ['APCP_06'],
                                    'fcst_var_levels': ['A06','A6'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_06', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A06','A6'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_24': {'fcst_var_names': ['APCP_24'],
                                    'fcst_var_levels': ['A24'],
                                    'fcst_var_thresholds': '',
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_24', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A24'],
                                    'obs_var_thresholds': '',
                                    'obs_var_options': '',
                                    'plot_group':'precip'}
                    }
                },
                'NBRCNT': {
                    'plot_stats_list': ('fss, afss, ufss, frate, orate'),
                    'interp': 'NBRHD_SQUARE, NBRHD_CIRCLE',
                    'vx_mask_list' : [
                        'Alaska', 'Hawaii', 'PuertoRico'
                    ],
                    'var_dict': {
                        'APCP_01': {'fcst_var_names': ['APCP_01'],
                                    'fcst_var_levels': ['A01','A1'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_01', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A01','A1'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_03': {'fcst_var_names': ['APCP_03'],
                                    'fcst_var_levels': ['A03','A3'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_03', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A03','A3'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_06': {'fcst_var_names': ['APCP_06'],
                                    'fcst_var_levels': ['A06','A6'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_06', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A06','A6'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_24': {'fcst_var_names': ['APCP_24'],
                                    'fcst_var_levels': ['A24'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_24', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A24'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'}
                    }
                },
                'CTC': {
                    'plot_stats_list': ('me, ets, fss, csi, fbias, fbar,'
                                        + ' obar, pod, faratio, farate, sratio'),
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'Alaska'
                    ],
                    'var_dict': {
                        'APCP_01': {'fcst_var_names': ['APCP_01'],
                                    'fcst_var_levels': ['A01','A1'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_01', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A01','A1'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_03': {'fcst_var_names': ['APCP_03'],
                                    'fcst_var_levels': ['A03','A3'],
                                    'fcst_var_thresholds': ('>=0.254, >=1.27,'
                                                            + ' >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'
                                                            + ' >=50.8,'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_03', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A03','A3'],
                                    'obs_var_thresholds': ('>=0.254, >=1.27,'
                                                           + ' >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'
                                                           + ' >=50.8,'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_06': {'fcst_var_names': ['APCP_06'],
                                    'fcst_var_levels': ['A06','A6'],
                                    'fcst_var_thresholds': ('>=0.254, >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=19.05,'
                                                            + ' >=25.4,'
                                                            + ' >=38.1,'
                                                            + ' >=50.8,'
                                                            + ' >=76.2,'
                                                            + ' >=101.6'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_06', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A06','A6'],
                                    'obs_var_thresholds': ('>=0.254, >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=19.05,'
                                                           + ' >=25.4,'
                                                           + ' >=38.1,'
                                                           + ' >=50.8,'
                                                           + ' >=76.2,'
                                                           + ' >=101.6'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'},
                        'APCP_24': {'fcst_var_names': ['APCP_24'],
                                    'fcst_var_levels': ['A24'],
                                    'fcst_var_thresholds': ('>=0.254, >=2.54,'
                                                            + ' >=6.35,'
                                                            + ' >=12.7,'
                                                            + ' >=25.4,'
                                                            + ' >=38.1,'
                                                            + ' >=50.8,'
                                                            + ' >=76.2,'
                                                            + ' >=101.6'
                                                            + ' >=152.4'),
                                    'fcst_var_options': '',
                                    'obs_var_names': ['APCP', 'APCP_24', 'APCP_01_Z0'],
                                    'obs_var_levels': ['A24'],
                                    'obs_var_thresholds': ('>=0.254, >=2.54,'
                                                           + ' >=6.35,'
                                                           + ' >=12.7,'
                                                           + ' >=25.4,'
                                                           + ' >=38.1,'
                                                           + ' >=50.8,'
                                                           + ' >=76.2,'
                                                           + ' >=101.6'
                                                           + ' >=152.4'),
                                    'obs_var_options': '',
                                    'plot_group':'precip'}
                    }
                }
            },
            'satellite_ghrsst_ncei_avhrr_anl': {
                'SL1L2': {
                    'plot_stats_list': 'me, rmse',
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'NH', 'SH', 'POLAR', 'ARCTIC', 'SEA_ICE', 
                        'SEA_ICE_FREE', 'SEA_ICE_POLAR', 'SEA_ICE_FREE_POLAR'
                    ],
                    'var_dict': {
                        'SST': {'fcst_var_names': ['TMP_Z0_mean'],
                                'fcst_var_levels': ['Z0'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['analysed_sst'],
                                'obs_var_levels': ['Z0'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'ICEC': {'fcst_var_names': ['ICEC_Z0_mean'],
                                 'fcst_var_levels': ['Z0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options':  '',
                                 'obs_var_names': ['sea_ice_fraction'],
                                 'obs_var_levels': ['Z0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'}
                    }
                }
            },
            'satellite_ghrsst_ospo_geopolar_anl': {
                'SL1L2': {
                    'plot_stats_list': 'me, rmse',
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'NH', 'SH', 'POLAR', 'ARCTIC', 'SEA_ICE', 
                        'SEA_ICE_FREE', 'SEA_ICE_POLAR', 'SEA_ICE_FREE_POLAR'
                    ],
                    'var_dict': {
                        'SST': {'fcst_var_names': ['TMP_Z0_mean'],
                                'fcst_var_levels': ['Z0'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_names': ['analysed_sst'],
                                'obs_var_levels': ['Z0'],
                                'obs_var_thresholds': '',
                                'obs_var_options': '',
                                'plot_group':'sfc_upper'},
                        'ICEC': {'fcst_var_names': ['ICEC_Z0_mean'],
                                 'fcst_var_levels': ['Z0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_names': ['sea_ice_fraction'],
                                 'obs_var_levels': ['Z0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': '',
                                 'plot_group':'sfc_upper'}
                    }
                }
            },
            'aviation_analysis': {
                'CTC': {
                    'plot_stats_list': ('me, ets, fss, csi, fbias, fbar,'
                                        + ' obar, pod, farate, faratio, sratio'),
                    'interp': 'NEAREST',
                    'vx_mask_list' : [
                        'AR2','ASIA','AUNZ','EAST','NAMR','NHM','NPCF','SHM','TRP'
                    ],
                    'var_dict': {
                        'ICESEV': {'fcst_var_names': ['ICESEV'],
                                  'fcst_var_levels': ['P812','P696.8','P595.2','P506','P392.7'],
                                  'fcst_var_thresholds': '>=1, >=2, >=3, >=4',
                                  'fcst_var_options': '',
                                  'obs_var_names': ['ICESEV'],
                                  'obs_var_levels': ['P800','P700','P600','P500','P400'],
                                  'obs_var_thresholds': '>=1, >=2, >=3, >=4',
                                  'obs_var_options': '',
                                  'plot_group':'aviation'},
                    }
                }
            },
        }

    '''
    Each formula in the formulas class needs to have the capability of providing three things.
    1) Simply, the complete conversion of the input quantity into the output units
    2) The rounded conversion of the input to the output (e.g., for displaying some thresholds)
    3) The coefficient and the constant that composes the formula (for converting base stats)
    '''
    class formulas():
        def mm_to_in(mm_vals, rounding=False, return_terms=False):
            if return_terms:
                M = np.divide(1., 25.4)
                C = 0.
                return M, C
            else:
                if rounding:
                    inch_vals = np.divide(mm_vals, 25.4).round(decimals=2)
                else:
                    inch_vals = np.divide(mm_vals, 25.4)
                return inch_vals
        def K_to_F(K_vals, rounding=False, return_terms=False):
            if return_terms:
                M = np.divide(9., 5.)
                C = ((-273.15)*9./5.)+32.
                return M, C
            else:
                if rounding:
                    F_vals = (((np.array(K_vals)-273.15)*9./5.)+32.).round()
                else:
                    F_vals = ((np.array(K_vals)-273.15)*9./5)+32.
                return F_vals
        def C_to_F(C_vals, rounding=False, return_terms=False):
            if return_terms:
                M = np.divide(9., 5.)
                C = 32.
                return M, C
            else:
                if rounding:
                    F_vals = ((np.array(C_vals)*9./5.)+32.).round()
                else:
                    F_vals = (np.array(C_vals)*9./5.)+32.
                return F_vals
        def mps_to_kt(mps_vals, rounding=False, return_terms=False):
            if return_terms:
                M = 1.94384449412
                C = 0.
                return M, C
            else:
                if rounding:
                    kt_vals = (np.multiply(mps_vals, 1.94384449412)).round()
                else:
                    kt_vals = np.multiply(mps_vals, 1.94384449412)
                return kt_vals
        def gpm_to_kft(gpm_vals, rounding=False, return_terms=False):
            if return_terms:
                M = np.divide(1., 304.8)
                C = 0.
                return M, C
            else:
                if rounding:
                    kft_vals = (np.divide(gpm_vals, 304.8)).round(decimals=2)
                else:
                    kft_vals = np.divide(gpm_vals, 304.8)
                return kft_vals
        def m_to_mi(m_vals, rounding=False, return_terms=False):
            if return_terms:
                M = np.divide(1., 1609.34)
                C = 0.
                return M, C
            else:
                if rounding:
                    mi_vals = (np.divide(m_vals, 1609.34)).round(decimals=2)
                else:
                    mi_vals = np.divide(m_vals, 1609.34)
                return mi_vals
