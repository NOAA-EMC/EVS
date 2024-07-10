#!/usr/bin/env python3
'''
Name: global_det_atmos_long_term_util.py
Contact(s): Mallory Row (mallory.row@noaa.gov)
Abstract: This contains functions used for global_det atmos long-term
          stats and plots. These are not run in ops/production.
'''

import os
import datetime
import numpy as np
import pandas as pd
import copy

def merge_grid2grid_long_term_stats_datasets(logger, stat_base_dir,
                                             time_range, date_dt_list,
                                             model_group, model_list,
                                             evs_var_name, evs_var_level,
                                             evs_var_thresh, evs_vx_grid,
                                             evs_vx_mask, evs_stat, evs_nbrhd):
    """! Build the data frame for all model stats,
         Read the model parse file, if doesn't exist
         parse the model file for need information, and write file

         Args:
             logger         - logger object
             stat_base_dir  - full path to stats base directory (string)
             time_range     - time range: monthly or yearly (string)
             date_dt_list   - list datetime objects
             model_group    - model group name (string)
             model_list     - list of models (strings)
             evs_var_name   - variable name in EVS (string)
             evs_var_level  - variable level in EVS (string)
             evs_var_thresh - variable threshold in EVS (string)
             evs_vx_grid    - verification grid in EVS (string)
             evs_vx_mask    - verification region in EVS (string)
             evs_stat       - statistic in EVS (string)
             evs_nbrhd      - neighborhood information in EVS

         Returns:
             merged_df - dataframe of stats from all
                         verification systems
    """
    logger.info("Reading data and creating merged dataset")
    expected_file_columns = [
        'SYS', 'YEAR', 'MONTH', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
        'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
        'DAY13', 'DAY14', 'DAY15', 'DAY16'
    ]
    if time_range == 'yearly':
        expected_file_columns.remove('MONTH')
    verif_sys_start_date_dict = {
        'caplan_zhu': date_dt_list[0].strftime('%Y%m'),
        'vsdb': '200801',
        'emc_verif_global': '202101',
        'evs': '202401'
    }
    if evs_var_name == 'UGRD_VGRD':
        if evs_stat == 'ME':
            caplan_zhu_var = 'SPD'
        else:
            caplan_zhu_var = 'UV'
        vsdb_var = 'WIND'
        emc_verif_global_var = evs_var_name
    else:
        caplan_zhu_var = evs_var_name
        vsdb_var = evs_var_name
        emc_verif_global_var = evs_var_name
    if evs_var_name == 'HGT':
        caplan_zhu_level = evs_var_level.replace('P', '')+'hpa'
    else:
        caplan_zhu_level = evs_var_level.replace('P', '')+'hPa'
    vsdb_level = evs_var_level
    emc_verif_global_level = evs_var_level
    if evs_vx_mask in ['NHEM', 'SHEM']:
        caplan_zhu_vx_mask = evs_vx_mask[0:2]
        vsdb_vx_mask = 'G2'+evs_vx_mask[0:2]+'X'
        emc_verif_global_vx_mask = evs_vx_mask[0:2]+'X'
    elif evs_vx_mask == 'TROPICS':
        caplan_zhu_vx_mask = evs_vx_mask.title()
        vsdb_vx_mask = 'G2'+evs_vx_mask[0:3]
        emc_verif_global_vx_mask = evs_vx_mask[0:3]
    elif evs_vx_mask == 'GLOBAL':
        caplan_zhu_vx_mask = evs_vx_mask.title()
        vsdb_vx_mask = 'G2'
        emc_verif_global_vx_mask = 'G002'
    else:
        caplan_zhu_vx_mask = evs_vx_mask
        vsdb_vx_mask = evs_vx_mask
        emc_verif_global_vx_mask = evs_vx_mask
    if evs_stat == 'ACC':
        caplan_zhu_stat = evs_stat.upper()[0:2]+'Wave1-20'
        vsdb_stat = evs_stat.upper()[0:2]
        emc_verif_global_stat = evs_stat.upper()
    elif evs_stat == 'ME':
        caplan_zhu_stat = 'Error'
        vsdb_stat = 'BIAS'
        emc_verif_global_stat = 'BIAS'
    elif evs_stat == 'RMSE':
        caplan_zhu_stat = evs_stat
        vsdb_stat = evs_stat
        emc_verif_global_stat = evs_stat
    else:
        caplan_zhu_stat = evs_stat
        vsdb_stat = evs_stat
        emc_verif_global_stat = evs_stat
    for model in model_list:
        if model_group == 'gfs_4cycles':
            valid_hour = model.replace('gfs', '')
        else:
            valid_hour = '00Z'
        model_caplan_zhu_file_name = os.path.join(
             stat_base_dir, model.replace(valid_hour, ''),
            'caplan_zhu_'+caplan_zhu_var+caplan_zhu_stat
            +'_'+caplan_zhu_level+'_'+caplan_zhu_vx_mask+'_valid'
            +valid_hour+'.txt'
        )
        model_vsdb_file_name = os.path.join(
             stat_base_dir, model.replace(valid_hour, ''),
            'vsdb_'+vsdb_stat+'_'+vsdb_var+'_'+vsdb_level+'_'
            +vsdb_vx_mask+'_valid'+valid_hour+'.txt'
        )
        model_emc_verif_global_file_name = os.path.join(
             stat_base_dir, model.replace(valid_hour, ''),
            'emc_verif_global_'+emc_verif_global_stat+'_'
            +emc_verif_global_var+'_'+emc_verif_global_level
            +'_'+emc_verif_global_vx_mask+'_valid'+valid_hour+'.txt'
        )
        model_evs_file_name = os.path.join(
             stat_base_dir, model.replace(valid_hour, ''),
            'evs_'+evs_stat+'_'+evs_var_name+'_'+evs_var_level+'_'
            +evs_vx_mask+'_valid'+valid_hour+'.txt'
        )
        logger.debug(f"{model} Caplan-Zhu File: {model_caplan_zhu_file_name}")
        logger.debug(f"{model} VSDB File: {model_vsdb_file_name}")
        logger.debug(f"{model} EMC_verif-global File: "
                     +f"{model_emc_verif_global_file_name}")
        logger.debug(f"{model} EVS File: {model_evs_file_name}")
        model_verif_sys_file_name_list = [model_caplan_zhu_file_name,
                                          model_vsdb_file_name,
                                          model_emc_verif_global_file_name,
                                          model_evs_file_name]
        if evs_stat == 'ACC' and evs_var_name == 'HGT' \
                and evs_var_level == 'P500' and valid_hour == '00Z' \
                and evs_vx_mask in ['NHEM', 'SHEM'] \
                and time_range == 'yearly':
            model_excel_file_name = os.path.join(
                stat_base_dir, model.replace(valid_hour, ''),
                'excel_'+evs_stat+'_'+evs_var_name+'_'+evs_var_level+'_'
                +emc_verif_global_vx_mask+'_valid'+valid_hour+'.txt'
            )
            logger.debug(f"{model} Excel File: {model_excel_file_name}")
            if date_dt_list[0] < datetime.datetime.strptime('199601', '%Y%m'):
                verif_sys_start_date_dict['caplan_zhu'] = '199601'
            if model == 'ukmet':
                verif_sys_start_date_dict['caplan_zhu'] = '199701'
            elif model == 'fnmoc':
                verif_sys_start_date_dict['caplan_zhu'] = '199801'
            elif model == 'cfs':
                verif_sys_start_date_dict['caplan_zhu'] = '999901'
            model_verif_sys_file_name_list.append(model_excel_file_name)
        set_new_df = True
        for model_verif_sys_file_name in model_verif_sys_file_name_list:
            if os.path.exists(model_verif_sys_file_name):
                model_verif_sys_df = pd.read_table(model_verif_sys_file_name,
                                                   delimiter=' ', dtype='str',
                                                   skipinitialspace=True)
                if set_new_df:
                    model_all_verif_sys_df = model_verif_sys_df.copy()
                    set_new_df = False
                else:
                    model_all_verif_sys_df = pd.concat(
                        [model_all_verif_sys_df, model_verif_sys_df],
                        ignore_index=True
                    )
            else:
                logger.debug(f"{model_verif_sys_file_name} does not exist")
        if time_range == 'monthly':
            model_merged_df = pd.DataFrame(
                index=pd.MultiIndex.from_product(
                    [[model], [f"{dt:%Y%m}" for dt in date_dt_list]],
                    names=['model', 'YYYYmm']
                ),
                columns=expected_file_columns
            )
        elif time_range == 'yearly':
            model_merged_df = pd.DataFrame(
                index=pd.MultiIndex.from_product(
                    [[model], [f"{dt:%Y}" for dt in date_dt_list]],
                    names=['model', 'YYYY']
                ),
                columns=expected_file_columns
            )
        for date_dt in date_dt_list:
            if date_dt \
                    >= datetime.datetime.strptime(
                        verif_sys_start_date_dict['caplan_zhu'], '%Y%m'
                    ) \
                    and date_dt < datetime.datetime.strptime(
                        verif_sys_start_date_dict['vsdb'], '%Y%m'
                    ):
                date_dt_verif_sys = 'CZ'
            elif date_dt \
                    >= datetime.datetime.strptime(
                        verif_sys_start_date_dict['vsdb'], '%Y%m'
                    ) \
                    and date_dt < datetime.datetime.strptime(
                        verif_sys_start_date_dict['emc_verif_global'], '%Y%m'
                    ):
                date_dt_verif_sys = 'VSDB'
            elif date_dt \
                    >= datetime.datetime.strptime(
                        verif_sys_start_date_dict['emc_verif_global'], '%Y%m'
                    ) \
                    and date_dt < datetime.datetime.strptime(
                        verif_sys_start_date_dict['evs'], '%Y%m'
                    ):
                date_dt_verif_sys = 'EVG'
            elif date_dt \
                    >= datetime.datetime.strptime(
                        verif_sys_start_date_dict['evs'], '%Y%m'
                    ):
                date_dt_verif_sys = 'EVS'
            else:
                date_dt_verif_sys = 'EXCEL'
            if time_range == 'monthly':
                model_verif_sys_date_dt_df = model_all_verif_sys_df.loc[
                    (model_all_verif_sys_df['SYS'] == date_dt_verif_sys)
                    & (model_all_verif_sys_df['YEAR'] == f"{date_dt:%Y}")
                    & (model_all_verif_sys_df['MONTH'] == f"{date_dt:%m}")
                ]
            elif time_range == 'yearly':
                model_verif_sys_date_dt_df = model_all_verif_sys_df.loc[
                    (model_all_verif_sys_df['SYS'] == date_dt_verif_sys)
                    & (model_all_verif_sys_df['YEAR'] == f"{date_dt:%Y}")
                ]
            if len(model_verif_sys_date_dt_df) == 0:
                model_merged_verif_sys_date_dt_values = []
                for col in expected_file_columns:
                    if col == 'SYS':
                        model_merged_verif_sys_date_dt_values.append(
                            date_dt_verif_sys
                        )
                    elif col == 'YEAR':
                        model_merged_verif_sys_date_dt_values.append(
                            f"{date_dt:%Y}"
                        )
                    elif col == 'MONTH':
                        model_merged_verif_sys_date_dt_values.append(
                            f"{date_dt:%m}"
                        )
                    else:
                         model_merged_verif_sys_date_dt_values.append(np.nan)
            else:
                model_merged_verif_sys_date_dt_values = (
                    model_verif_sys_date_dt_df.values[0]
                )
            if time_range == 'monthly':
                model_merged_df.loc[(model,f"{date_dt:%Y%m}")] = (
                    model_merged_verif_sys_date_dt_values
                )
            elif time_range == 'yearly':
                model_merged_df.loc[(model,f"{date_dt:%Y}")] = (
                     model_merged_verif_sys_date_dt_values
                )
        if model_list.index(model) == 0:
            merged_df = model_merged_df
        else:
            merged_df = pd.concat([merged_df, model_merged_df])
    return merged_df

def merge_precip_long_term_stats_datasets(logger, stat_base_dir,
                                          time_range, date_dt_list,
                                          model_group, model_list,
                                          evs_var_name, evs_var_level,
                                          evs_var_thresh, evs_vx_grid,
                                          evs_vx_mask, evs_stat,
                                          evs_nbrhd):
    """! Build the data frame for all model stats,
         Read the model parse file, if doesn't exist
         parse the model file for need information, and write file

         Args:
             logger         - logger object
             stat_base_dir  - full path to stats base directory (string)
             time_range     - time range: monthly or yearly (string)
             date_dt_list   - list datetime objects
             model_group    - model group name (string)
             model_list     - list of models (strings)
             evs_var_name   - variable name in EVS (string)
             evs_var_level  - variable level in EVS (string)
             evs_var_thresh - variable threshold in EVS (string)
             evs_vx_grid    - verification grid in EVS (string)
             evs_vx_mask    - verification region in EVS (string)
             evs_stat       - statistic in EVS (string)
             evs_nbrhd      - neighborhood information in EVS

         Returns:
             merged_df - dataframe of stats from all
                         verification systems
    """
    logger.info("Reading data and creating merged dataset")
    expected_file_columns = [
        'SYS', 'YEAR', 'MONTH', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
        'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10'
    ]
    if time_range == 'yearly':
        expected_file_columns.remove('MONTH')
    verif_sys_start_date_dict = {
        'verf_precip': date_dt_list[0].strftime('%Y%m'),
        'evs': '202401'
    }
    for model in model_list:
        if evs_stat == 'FSS':
            nbrhd_width_pts = np.sqrt(int(evs_nbrhd.split('/')[1]))
            if evs_vx_grid == 'G240':
                dx = 4.7625
            nbrhd_width_km = round(nbrhd_width_pts * dx)
            model_verf_precip_file_name = os.path.join(
                stat_base_dir, model,
                'verf_precip_'+evs_stat+'_'
                +evs_var_thresh[2:].replace('.','p')+'_'
                +'NBRHD'+str(nbrhd_width_km)+'km_'
                +evs_var_name+'_'+evs_var_level+'_'
                +evs_vx_grid+'_'+'valid12Z.txt'
            )
            model_evs_file_name = os.path.join(
                stat_base_dir, model,
                'evs_'+evs_stat+'_'
                +evs_var_thresh[2:].replace('.','p')+'_'
                +evs_nbrhd.replace('/', '')+'_'
                +evs_var_name+'_'+evs_var_level+'_'
                +evs_vx_grid+'_'+evs_vx_mask+'_valid12Z.txt'
            )
        else:
            model_verf_precip_file_name = os.path.join(
                stat_base_dir, model,
                'verf_precip_'+evs_stat+'_'
                +evs_var_thresh[2:].replace('.','p')+'_'
                +evs_var_name+'_'+evs_var_level+'_'
                +evs_vx_grid+'_'+'valid12Z.txt'
            )
            model_evs_file_name = os.path.join(
                stat_base_dir, model,
                'evs_'+evs_stat+'_'
                +evs_var_thresh[2:].replace('.','p')+'_'
                +evs_var_name+'_'+evs_var_level+'_'
                +evs_vx_grid+'_'+evs_vx_mask+'_valid12Z.txt'
            )
        logger.debug(f"{model} Verf-precip File: "
                     +f"{model_verf_precip_file_name}")
        logger.debug(f"{model} EVS File: {model_evs_file_name}")
        model_verif_sys_file_name_list = [model_verf_precip_file_name,
                                          model_evs_file_name]
        set_new_df = True
        for model_verif_sys_file_name in model_verif_sys_file_name_list:
            if os.path.exists(model_verif_sys_file_name):
                model_verif_sys_df = pd.read_table(model_verif_sys_file_name,
                                                   delimiter=' ', dtype='str',
                                                   skipinitialspace=True)
                if set_new_df:
                    model_all_verif_sys_df = model_verif_sys_df.copy()
                    set_new_df = False
                else:
                    model_all_verif_sys_df = pd.concat(
                        [model_all_verif_sys_df, model_verif_sys_df],
                        ignore_index=True
                    )
            else:
                logger.debug(f"{model_verif_sys_file_name} does not exist")
        if time_range == 'monthly':
            model_merged_df = pd.DataFrame(
                index=pd.MultiIndex.from_product(
                    [[model], [f"{dt:%Y%m}" for dt in date_dt_list]],
                    names=['model', 'YYYYmm']
                ),
                columns=expected_file_columns
            )
        elif time_range == 'yearly':
            model_merged_df = pd.DataFrame(
                index=pd.MultiIndex.from_product(
                    [[model], [f"{dt:%Y}" for dt in date_dt_list]],
                    names=['model', 'YYYY']
                ),
                columns=expected_file_columns
            )
        for date_dt in date_dt_list:
            if date_dt \
                    >= datetime.datetime.strptime(
                        verif_sys_start_date_dict['verf_precip'], '%Y%m'
                    ) \
                    and date_dt < datetime.datetime.strptime(
                        verif_sys_start_date_dict['evs'], '%Y%m'
                    ):
                date_dt_verif_sys = 'VP'
            else:
                date_dt_verif_sys = 'EVS'
            if time_range == 'monthly':
                model_verif_sys_date_dt_df = model_all_verif_sys_df.loc[
                    (model_all_verif_sys_df['SYS'] == date_dt_verif_sys)
                    & (model_all_verif_sys_df['YEAR'] == f"{date_dt:%Y}")
                    & (model_all_verif_sys_df['MONTH'] == f"{date_dt:%m}")
                ]
            elif time_range == 'yearly':
                model_verif_sys_date_dt_df = model_all_verif_sys_df.loc[
                    (model_all_verif_sys_df['SYS'] == date_dt_verif_sys)
                    & (model_all_verif_sys_df['YEAR'] == f"{date_dt:%Y}")
                ]
            if len(model_verif_sys_date_dt_df) == 0:
                model_merged_verif_sys_date_dt_values = []
                for col in expected_file_columns:
                    if col == 'SYS':
                        model_merged_verif_sys_date_dt_values.append(
                            date_dt_verif_sys
                        )
                    elif col == 'YEAR':
                        model_merged_verif_sys_date_dt_values.append(
                            f"{date_dt:%Y}"
                        )
                    elif col == 'MONTH':
                        model_merged_verif_sys_date_dt_values.append(
                            f"{date_dt:%m}"
                        )
                    else:
                         model_merged_verif_sys_date_dt_values.append(np.nan)
            else:
                model_merged_verif_sys_date_dt_values = (
                    model_verif_sys_date_dt_df.values[0]
                )
            if time_range == 'monthly':
                model_merged_df.loc[(model,f"{date_dt:%Y%m}")] = (
                    model_merged_verif_sys_date_dt_values
                )
            elif time_range == 'yearly':
                model_merged_df.loc[(model,f"{date_dt:%Y}")] = (
                     model_merged_verif_sys_date_dt_values
                )
        if model_list.index(model) == 0:
            merged_df = model_merged_df
        else:
            merged_df = pd.concat([merged_df, model_merged_df])
    return merged_df
