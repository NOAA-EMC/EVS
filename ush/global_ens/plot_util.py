#!/usr/bin/env python3
import pickle
import os
import sys
import datetime as datetime
import time
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
"""!@namespace plot_util
   @brief Provides utility functions for METplus plotting use case
"""

def get_date_arrays(date_type, date_beg, date_end,
                    fcst_valid_hour, fcst_init_hour,
                    obs_valid_hour, obs_init_hour,
                    lead):
   '''! Create arrays of requested dates plotting and 
        dates expected to be in MET .stat files

        Args:
           date_type                - string of describing the treatment
                                      of dates, either VALID or INIT
           date_beg                 - string of beginning date,
                                      either blank or %Y%m%d format
           date_end                 - string of end date,
                                      either blank or %Y%m%d format
           fcst_valid_hour          - string of forecast valid hour(s)
                                      information, blank or in %H%M%S
           fcst_init_hour           - string of forecast init hour(s)
                                      information, blank or in %H%M%S
           obs_valid_hour           - string of observation valid hour(s)
                                      information, blank or in %H%M%S
           obs_init_hour            - string of observation hour(s)
                                      information, blank or in %H%M%S
           lead                     - string of forecast lead, in %H%M%S
                                      format
        Returns
           plot_time_dates          - array of ordinal dates based on user 
                                      provided information
           expected_stat_file_dates - array of dates that are expected to
                                      be found in the MET .stat files
                                      based on user provided information,
                                      formatted as %Y%m%d_%H%M%S
   '''
   lead_hour_seconds = int(int(lead[:-4])%24) * 3600
   lead_min_seconds = int(lead[-4:-2]) * 60
   lead_seconds = int(lead[-2:])
   valid_init_time_info = {
      'fcst_valid_time': list(filter(None, fcst_valid_hour.split(', '))),
      'fcst_init_time': list(filter(None, fcst_init_hour.split(', '))),
      'obs_valid_time': list(filter(None, obs_valid_hour.split(', '))),
      'obs_init_time': list(filter(None, obs_init_hour.split(', '))),
   }
   # Extract missing information, if possible
   for type in ['fcst', 'obs']:
      valid_time_list = valid_init_time_info[type+'_valid_time']
      init_time_list = valid_init_time_info[type+'_init_time']
      if (len(valid_time_list) == 0
            and len(init_time_list) > 0):
         for itime in init_time_list:
            itime_hour_seconds = int(int(itime[0:2])%24) * 3600
            itime_min_seconds = int(itime[2:4]) * 60
            itime_seconds = int(itime[4:])
            offset = datetime.timedelta(seconds=lead_hour_seconds
                                                + lead_min_seconds
                                                + lead_seconds
                                                + itime_hour_seconds
                                                + itime_min_seconds
                                                + itime_seconds)
            tot_sec = offset.total_seconds()
            valid_hour = int(tot_sec//3600)
            valid_min = int((tot_sec%3600) // 60)
            valid_sec = int((tot_sec%3600)%60)
            valid_time = (
               str(valid_hour).zfill(2)
               +str(valid_min).zfill(2)
               +str(valid_sec).zfill(2)
            )
            valid_init_time_info[type+'_valid_time'].append(valid_time)
      if (len(init_time_list) == 0
            and len(valid_time_list) > 0):
         for vtime in valid_time_list:
            vtime_hour_seconds = int(int(vtime[0:2])%24) * 3600
            vtime_min_seconds = int(vtime[2:4]) * 60
            vtime_seconds = int(vtime[4:])
            offset = datetime.timedelta(seconds=lead_hour_seconds
                                                + lead_min_seconds
                                                + lead_seconds
                                                - vtime_hour_seconds
                                                - vtime_min_seconds
                                                - vtime_seconds)
            tot_sec = offset.total_seconds()
            init_hour = int(tot_sec//3600)
            init_min = int((tot_sec%3600) // 60)
            init_sec = int((tot_sec%3600)%60)
            init_time = (
               str(init_hour).zfill(2)
               +str(init_min).zfill(2)
               +str(init_sec).zfill(2)
            )
            valid_init_time_info[type+'_init_time'].append(init_time)
   for type in ['valid', 'init']:
      fcst_time_list = valid_init_time_info['fcst_'+type+'_time']
      obs_time_list = valid_init_time_info['obs_'+type+'_time']
      if len(fcst_time_list) == 0:
         if len(obs_time_list) > 0:
            valid_init_time_info['fcst_'+type+'_time'] = (
               valid_init_time_info['obs_'+type+'_time']
            )
      if len(obs_time_list) == 0:
         if len(fcst_time_list) > 0:
            valid_init_time_info['obs_'+type+'_time'] = (
               valid_init_time_info['fcst_'+type+'_time']
            )
   date_info = {}
   for type in ['fcst_'+date_type.lower(),
                'obs_'+date_type.lower()]:
      time_list = valid_init_time_info[type+'_time']
      if len(time_list) != 0:
         time_beg = min(time_list)
         time_end = max(time_list)
         if time_beg == time_end or len(time_list) == 1:
            delta_t = datetime.timedelta(seconds=86400)
         else:
            delta_t_list = []
            for t in range(len(time_list)):
               if time_list[t] == time_end:
                  delta_t_list.append(
                     (
                        datetime.datetime.strptime('235959','%H%M%S')
                        - (datetime.datetime.strptime(time_list[t],
                                                      '%H%M%S'))
                     )
                     + datetime.timedelta(seconds=1)
                  )
               else:
                  delta_t_list.append(
                     datetime.datetime.strptime(time_list[t+1],
                                                '%H%M%S')
                     - datetime.datetime.strptime(time_list[t],
                                                  '%H%M%S')
                  )
            delta_t_array = np.array(delta_t_list)
            if np.all(delta_t_array == delta_t_array[0]):
               delta_t = delta_t_array[0]
            else:
               delta_t = np.min(delta_t_array)
         beg = datetime.datetime.strptime(
            date_beg+time_beg, '%Y%m%d%H%M%S'
         )
         end = datetime.datetime.strptime(
            date_end+time_end, '%Y%m%d%H%M%S'
         )
         dates = np.arange(
            beg, end+delta_t,
            delta_t
         ).astype(datetime.datetime)
      else:
         dates = []
      date_info[type+'_dates'] = dates
   # Build opposite dates
   if date_type == 'VALID':
      oppo_date_type = 'INIT'
   elif date_type == 'INIT':
      oppo_date_type = 'VALID'
   lead_timedelta = datetime.timedelta(
      seconds=(int(int(lead[:-4])) * 3600 + lead_min_seconds
               + lead_seconds)
   )
   if oppo_date_type == 'INIT':
      lead_timedelta = -1 * lead_timedelta
   for type in ['fcst', 'obs']:
      date_info[type+'_'+oppo_date_type.lower()+'_dates'] = (
         date_info[type+'_'+date_type.lower()+'_dates'] + lead_timedelta
      )
   # Use fcst_*_dates for dates
   # this makes the assumption that
   # fcst_*_dates and obs_*_dates
   # are the same, and they should be for
   # most cases
   dates = date_info['fcst_'+date_type.lower()+'_dates']
   fv_dates = date_info['fcst_valid_dates']
   plot_time_dates = []
   expected_stat_file_dates = []
   for date in dates:
      dt = date.time()
      seconds = (dt.hour * 60 + dt.minute) * 60 + dt.second
      plot_time_dates.append(dates.toordinal() + seconds/86400.)
   # MET .stat files saves valid_dates in file
   fv_dates = date_info['fcst_valid_dates']
   expected_stat_file_dates = []
   for fv_date in fv_dates:
      expected_stat_file_dates.append(fv_date.strftime('%Y%m%d_%H%M%S'))
   return plot_time_dates, expected_stat_file_dates

def format_thresh(thresh):
   """! Format thresholds for file naming
      Args:
         thresh         - string of the threshold(s)

      Return:
         thresh_symbol  - string of the threshold(s)
                          with symbols
         thresh_letters - string of the threshold(s)
                          with letters
   """
   thresh_list = thresh.split(' ')
   thresh_symbol = ''
   thresh_letter = ''
   for thresh in thresh_list:
      if thresh == '':
         continue
      thresh_value = thresh
      for opt in ['>=', '>', '==', '!=', '<=', '<',
                  'ge', 'gt', 'eq', 'ne', 'le', 'lt']:
         if opt in thresh_value:
            thresh_opt = opt
            thresh_value = thresh_value.replace(opt, '')
      if thresh_opt in ['>', 'gt']:
         thresh_symbol+='>'+thresh_value
         thresh_letter+='gt'+thresh_value
      elif thresh_opt in ['>=', 'ge']:
         thresh_symbol+='>='+thresh_value
         thresh_letter+='ge'+thresh_value
      elif thresh_opt in ['<', 'lt']:
         thresh_symbol+='<'+thresh_value
         thresh_letter+='lt'+thresh_value
      elif thresh_opt in ['<=', 'le']:
         thresh_symbol+='<='+thresh_value
         thresh_letter+='le'+thresh_value
      elif thresh_opt in ['==', 'eq']:
         thresh_symbol+='=='+thresh_value
         thresh_letter+='eq'+thresh_value
      elif thresh_opt in ['!=', 'ne']:
         thresh_symbol+='!='+thresh_value
         thresh_letter+='ne'+thresh_value
   return thresh_symbol, thresh_letter

def get_stat_file_base_columns(met_version):
   """! Get the standard MET .stat file columns based on
        version number

           Args:
              met_version            - string of MET version
                                       number being used to
                                       run stat_analysis

           Returns:
              stat_file_base_columns - list of the standard
                                       columns shared among the 
                                       different line types
   """
   met_version = float(met_version)
   if met_version < 8.1:
      stat_file_base_columns = [
         'VERSION', 'MODEL', 'DESC', 'FCST_LEAD', 'FCST_VALID_BEG',
         'FCST_VALID_END', 'OBS_LEAD', 'OBS_VALID_BEG', 'OBS_VALID_END',
         'FCST_VAR', 'FCST_LEV', 'OBS_VAR', 'OBS_LEV', 'OBTYPE', 'VX_MASK',
         'INTERP_MTHD', 'INTERP_PNTS', 'FCST_THRESH', 'OBS_THRESH', 
         'COV_THRESH', 'ALPHA', 'LINE_TYPE'
      ]
   else:
      stat_file_base_columns = [
         'VERSION', 'MODEL', 'DESC', 'FCST_LEAD', 'FCST_VALID_BEG', 
         'FCST_VALID_END', 'OBS_LEAD', 'OBS_VALID_BEG', 'OBS_VALID_END', 
         'FCST_VAR', 'FCST_UNITS', 'FCST_LEV', 'OBS_VAR', 'OBS_UNITS', 
         'OBS_LEV', 'OBTYPE', 'VX_MASK', 'INTERP_MTHD', 'INTERP_PNTS',
         'FCST_THRESH', 'OBS_THRESH', 'COV_THRESH', 'ALPHA', 'LINE_TYPE'
      ]
   return stat_file_base_columns

def get_stat_file_line_type_columns(logger, met_version, line_type):
   """! Get the MET .stat file columns for line type based on 
      version number
         Args:
            met_version - string of MET version number 
                          being used to run stat_analysis
            line_type   - string of the line type of the MET
                          .stat file being read
         Returns:
            stat_file_line_type_columns - list of the line
                                          type columns
   """
   met_version = float(met_version)
   if line_type == 'SL1L2':
      if met_version >= 6.0:
         stat_file_line_type_columns = [
            'TOTAL', 'FBAR', 'OBAR', 'FOBAR', 'FFBAR', 'OOBAR', 'MAE'
         ]
   elif line_type == 'SAL1L2':
      if met_version >= 6.0:
         stat_file_line_type_columns = [
            'TOTAL', 'FABAR', 'OABAR', 'FOABAR', 'FFABAR', 'OOABAR', 'MAE'
         ]
   elif line_type == 'VL1L2':
      if met_version >= 12.0:
         stat_file_line_type_columns = [
            'TOTAL', 'UFBAR', 'VFBAR', 'UOBAR', 'VOBAR', 'UVFOBAR',
            'UVFFBAR', 'UVOOBAR', 'F_SPEED_BAR', 'O_SPEED_BAR', 'DIR_ME', 
            'DIR_MAE', 'DIR_MSE'
         ]
      elif met_version >= 7.0:
         stat_file_line_type_columns = [
            'TOTAL', 'UFBAR', 'VFBAR', 'UOBAR', 'VOBAR', 'UVFOBAR',
            'UVFFBAR', 'UVOOBAR', 'F_SPEED_BAR', 'O_SPEED_BAR'
         ]
      elif met_version <= 6.1:
         stat_file_line_type_columns = [
            'TOTAL', 'UFBAR', 'VFBAR', 'UOBAR', 'VOBAR', 'UVFOBAR',
            'UVFFBAR', 'UVOOBAR'
         ]
   elif line_type == 'VAL1L2':
      if met_version >= 6.0:
         stat_file_line_type_columns = [
            'TOTAL', 'UFABAR', 'VFABAR', 'UOABAR', 'VOABAR', 'UVFOABAR', 
            'UVFFABAR', 'UVOOABAR'
         ]
   elif line_type == 'VCNT':
      if met_version >= 7.0:
         stat_file_line_type_columns = [
            'TOTAL', 'FBAR', 'FBAR_NCL', 'FBAR_NCU', 'OBAR', 'OBAR_NCL', 
            'OBAR_NCU', 'FS_RMS', 'FS_RMS_NCL', 'FS_RMS_NCU', 'OS_RMS',
            'OS_RMS_NCL', 'OS_RMS_NCU', 'MSVE', 'MSVE_NCL', 'MSVE_NCU',
            'RMSVE', 'RMSVE_NCL', 'RMSVE_NCU', 'FSTDEV', 'FSTDEV_NCL',
            'FSTDEV_NCU', 'OSTDEV', 'OSTDEV_NCL', 'OSTDEV_NCU', 'FDIR', 
            'FDIR_NCL', 'FDIR_NCU', 'ODIR', 'ODIR_NCL', 'ODIR_NCU', 
            'FBAR_SPEED', 'FBAR_SPEED_NCL', 'FBAR_SPEED_NCU', 'OBAR_SPEED', 
            'OBAR_SPEED_NCL', 'OBAR_SPEED_NCU', 'VDIFF_SPEED', 
            'VDIFF_SPEED_NCL', 'VDIFF_SPEED_NCU', 'VDIFF_DIR',
            'VDIFF_DIR_NCL', 'VDIFF_DIR_NCU', 'SPEED_ERR', 'SPEED_ERR_NCL',
            'SPEED_ERR_NCU', 'SPEED_ABSERR', 'SPEED_ABSERR_NCL',
            'SPEED_ABSERR_NCU', 'DIR_ERR', 'DIR_ERR_NCL', 'DIR_ERR_NCU',
            'DIR_ABSERR', 'DIR_ABSERR_NCL', 'DIR_ABSERR_NCU'
         ]
      else:
         logger.error("FATAL ERROR: VCNT is not a valid LINE_TYPE in METV"+met_version)
         sys.exit(1)
   elif line_type == 'CTC':
      if met_version >= 6.0:
         stat_file_line_type_columns = [
            'TOTAL', 'FY_OY', 'FY_ON', 'FN_OY', 'FN_ON'
         ]
   return stat_file_line_type_columns

def get_clevels(data, spacing):
   """! Get contour levels for plotting differences
        or bias (centered on 0)
           Args:
              data    - array of data to be contoured
              spacing - float for spacing for power function,
                        value of 1.0 gives evenly spaced
                        contour intervals
           Returns:
              clevels - array of contour levels
   """
   if np.abs(np.nanmin(data)) > np.nanmax(data):
      cmax = np.abs(np.nanmin(data))
      cmin = np.nanmin(data)
   else:
      cmax = np.nanmax(data)
      cmin = -1 * np.nanmax(data)
   if cmax > 100:
      cmax = cmax - (cmax * 0.2)
      cmin = cmin + (cmin * 0.2)
   elif cmax > 10:
      cmax = cmax - (cmax * 0.1)
      cmin = cmin + (cmin * 0.1)
   if cmax > 1:
      cmin = round(cmin-1,0)
      cmax = round(cmax+1,0)
   else:
      cmin = round(cmin-.1,1)
      cmax = round(cmax+.1,1)
   steps = 6
   span = cmax
   dx = 1. / (steps-1)
   pos = np.array([0 + (i*dx)**spacing*span for i in range(steps)],
                   dtype=float)
   neg = np.array(pos[1:], dtype=float) * -1
   clevels = np.append(neg[::-1], pos)
   return clevels

def calculate_average(logger, average_method, stat, model_dataframe,
                      model_stat_values):
   """! Calculate average of dataset
      Args:
         logger               - logging file
         average_method       - string of the method to
                                use to calculate the average
         stat                 - string of the statistic the
                                average is being taken for
         model_dataframe      - dataframe of model .stat
                                columns
         model_stat_values    - array of statistic values
      Returns:
         average_array        - array of average value(s)
   """
   average_array = np.empty_like(model_stat_values[:,0])
   if average_method == 'MEAN':
      for l in range(len(model_stat_values[:, 0])):
         average_array[l] = np.ma.mean(model_stat_values[l,:])
   elif average_method == 'MEDIAN':
      for l in range(len(model_stat_values[:,0])):
         logger.info(np.ma.median(model_stat_values[l,:]))
         average_array[l] = np.ma.median(model_stat_values[l,:])
   elif average_method == 'AGGREGATION':
      ndays = model_dataframe.shape[0]
      model_dataframe_aggsum = (
         model_dataframe.groupby('model_plot_name').agg(['sum'])
      )
      model_dataframe_aggsum.columns = (
         calculate_stat(logger, model_dataframe_aggsum/ndays, stat)
      )
      for l in range(len(avg_array[:,0])):
         average_array[l] = avg_array[l]
   else:
      logger.error("FATAL ERROR: Invalid entry for MEAN_METHOD, "
                   +"use MEAN, MEDIAN, or AGGREGATION")
      sys.exit(1)
   return average_array

def calculate_ci(logger, ci_method, modelB_values, modelA_values, total_days,
                 stat, average_method, randx):
   """! Calculate confidence intervals between two sets of data
      Args:
         logger         - logging file
         ci_method      - string of the method to use to
                          calculate the confidence intervals
         modelB_values  - array of values
         modelA_values  - array of values
         total_days     - float of total number of days 
                          being considered, sample size
         stat           - string of the statistic the
                          confidence intervals are being
                          calculated for
         average_method - string of the method to 
                          use to calculate the average
         randx          - 2D array of random numbers [0,1)

      Returns:
         intvl          - float of the confidence interval
   """
   if ci_method == 'EMC':
      modelB_modelA_diff = modelB_values - modelA_values
      ndays = total_days - np.ma.count_masked(modelB_modelA_diff)
      modelB_modelA_diff_mean = modelB_modelA_diff.mean()
      modelB_modelA_std = np.sqrt(
         ((modelB_modelA_diff - modelB_modelA_diff_mean)**2).mean()
      )
      if ndays >= 80:
         intvl = 1.960*modelB_modelA_std/np.sqrt(ndays-1)
      elif ndays >= 40 and ndays < 80:
         intvl = 2.000*modelB_modelA_std/np.sqrt(ndays-1)
      elif ndays >= 20 and ndays < 40:
         intvl = 2.042*modelB_modelA_std/np.sqrt(ndays-1)
      elif ndays < 20 and ndays > 0:
         intvl = 2.228*modelB_modelA_std/np.sqrt(ndays-1)
      elif ndays == 0:
         intvl = '--'
   elif ci_method == 'EMC_MONTE_CARLO':
      ntest, ntests = 1, 10000
      dates = []
      for idx_val in modelB_values.index.values:
         dates.append(idx_val[1])
      ndays = len(dates)
      rand1_data_index = pd.MultiIndex.from_product(
         [['rand1'], np.arange(1, ntests+1, dtype=int), dates],
         names=['model_plot_name', 'ntest', 'dates']
      )
      rand2_data_index = pd.MultiIndex.from_product(
         [['rand2'], np.arange(1, ntests+1, dtype=int), dates],
         names=['model_plot_name', 'ntest', 'dates']
      )
      rand1_data = pd.DataFrame(
         np.nan, index = rand1_data_index, 
         columns=modelB_values.columns
      )
      rand2_data = pd.DataFrame(
         np.nan, index=rand2_data_index,
         columns=modelB_values.columns
      )
      ncolumns = len(modelB_values.columns)
      rand1_data_values = np.empty([ntests, ndays, ncolumns])
      rand2_data_values = np.empty([ntests, ndays, ncolumns])
      randx_ge0_idx = np.where(randx - 0.5 >= 0)
      randx_lt0_idx = np.where(randx - 0.5 < 0)
      rand1_data_values[randx_ge0_idx[0], randx_ge0_idx[1],:] = (
         modelA_values.iloc[randx_ge0_idx[1],:]
      )
      rand2_data_values[randx_ge0_idx[0], randx_ge0_idx[1],:] = (
         modelB_values.iloc[randx_ge0_idx[1],:]
      )
      rand1_data_values[randx_lt0_idx[0], randx_lt0_idx[1],:] = (
         modelB_values.iloc[randx_lt0_idx[1],:]
      )
      rand2_data_values[randx_lt0_idx[0], randx_lt0_idx[1],:] = (
         modelA_values.iloc[randx_lt0_idx[1],:]
      )
      ntest = 1
      while ntest <= ntests:
         rand1_data.loc[('rand1', ntest)] = rand1_data_values[ntest-1,:,:]
         rand2_data.loc[('rand2', ntest)] = rand2_data_values[ntest-1,:,:]
         ntest+=1
      intvl = np.nan
      rand1_stat_values, rand1_stat_values_array, stat_plot_name = (
         calculate_stat(logger, rand1_data, stat)
      )
      rand2_stat_values, rand2_stat_values_array, stat_plot_name = (
         calculate_stat(logger, rand2_data, stat)
      )
      rand1_average_array = (
         calculate_average(logger, average_method, stat, rand1_data, 
                           rand1_stat_values_array[0,0,:,:])
      )
      rand2_average_array = (
         calculate_average(logger, average_method, stat, rand2_data,
                           rand2_stat_values_array[0,0,:,:])
      )
      scores_diff = rand2_average_array - rand1_average_array
      scores_diff_mean = np.sum(scores_diff)/ntests
      scores_diff_var = np.sum((scores_diff-scores_diff_mean)**2)
      scores_diff_std = np.sqrt(scores_diff_var/(ntests-1))
      intvl = 1.96*scores_diff_std
      
   else:
      logger.error("FATAL ERROR: Invalid entry for MAKE_CI_METHOD, "
                   +"use EMC, EMC_MONTE_CARLO")
      sys.exit(1)
   return intvl

def get_stat_plot_name(logger, stat):
   """! Get the formalized name of the statistic being plotted
      Args:
         stat           - string of the simple statistic
                          name being plotted
      Returns:
         stat_plot_name - string of the formal statistic
                          name being plotted
   """
   if stat in ['bias','me']:
      stat_plot_name = 'Mean Error (Bias)'
   elif stat == 'esd':
      stat_plot_name = 'Standard Deviation of the Error'
   elif stat == 'rmse':
      stat_plot_name = 'Root Mean Square Error'
   elif stat == 'bcrmse':
      stat_plot_name = 'Bias-Corrected Root Mean Square Error'
   elif stat == 'msess':
      stat_plot_name = "Murphy's Mean Square Error Skill Score"
   elif stat == 'rsd':
      stat_plot_name = 'Ratio of the Standard Deviation'
   elif stat == 'rmse_md':
      stat_plot_name = 'Root Mean Square Error from Mean Error'
   elif stat == 'rmse_pv':
      stat_plot_name = 'Root Mean Square Error from Pattern Variation'
   elif stat == 'pcor':
      stat_plot_name = 'Pattern Correlation'
   elif stat == 'acc':
      stat_plot_name = 'Anomaly Correlation Coefficient'
   elif stat == 'fbar':
      stat_plot_name = 'Forecast Averages'
   elif stat == 'obar':
      stat_plot_name = 'Observation Averages'
   elif stat == 'fbar_obar':
      stat_plot_name = 'Forecast and Observation Averages'
   elif stat == 'speed_err':
      stat_plot_name = (
         'Difference in Average FCST and OBS Wind Vector Speeds'
      )
   elif stat == 'dir_err':
      stat_plot_name = (
         'Difference in Average FCST and OBS Wind Vector Direction'
      )
   elif stat == 'rmsve':
      stat_plot_name = 'Root Mean Square Difference Vector Error'
   elif stat == 'vdiff_speed':
      stat_plot_name = 'Difference Vector Speed'
   elif stat == 'vdiff_dir':
      stat_plot_name = 'Difference Vector Direction'
   elif stat == 'fbar_obar_speed':
      stat_plot_name = 'Average Wind Vector Speed'
   elif stat == 'fbar_obar_dir':
      stat_plot_name = 'Average Wind Vector Direction'
   elif stat == 'fbar_speed':
      stat_plot_name = 'Average Forecast Wind Vector Speed'
   elif stat == 'fbar_dir':
      stat_plot_name = 'Average Forecast Wind Vector Direction'
   elif stat == 'orate':
      stat_plot_name = 'Observation Rate'
   elif stat == 'baser':
      stat_plot_name = 'Base Rate'
   elif stat == 'frate':
      stat_plot_name = 'Forecast Rate'
   elif stat == 'orate_frate':
      stat_plot_name = 'Observation and Forecast Rates'
   elif stat == 'baser_frate':
      stat_plot_name = 'Base and Forecast Rates'
   elif stat == 'accuracy':
      stat_plot_name = 'Accuracy'
   elif stat == 'fbias':
      stat_plot_name = 'Frequency Bias'
   elif stat == 'pod':
      stat_plot_name = 'Probability of Detection'
   elif stat == 'hrate':
      stat_plot_name = 'Hit Rate'
   elif stat == 'pofd':
      stat_plot_name = 'Probability of False Detection'
   elif stat == 'farate':
      stat_plot_name = 'False Alarm Rate'
   elif stat == 'podn':
      stat_plot_name = 'Probability of Detection of the Non-Event'
   elif stat == 'faratio':
      stat_plot_name = 'False Alarm Ratio'
   elif stat == 'sratio':
      stat_plot_name = 'Success Ratio (1-FAR)'
   elif stat == 'csi':
      stat_plot_name = 'Critical Success Index'
   elif stat == 'ts':
      stat_plot_name = 'Threat Score'
   elif stat == 'gss':
      stat_plot_name = 'Gilbert Skill Score'
   elif stat == 'ets':
      stat_plot_name = 'Equitable Threat Score'
   elif stat == 'hk':
      stat_plot_name = 'Hanssen-Kuipers Discriminant'
   elif stat == 'tss':
      stat_plot_name = 'True Skill Score'
   elif stat == 'pss':
      stat_plot_name = 'Peirce Skill Score'
   elif stat == 'hss':
      stat_plot_name = 'Heidke Skill Score'
   elif stat == 'si':
      stat_plot_name = 'Scatter Index'
   elif stat == 'p95':
      stat_plot_name = '95th Percentile'
   else:
      logger.error("FATAL ERROR: "+stat+" is not a valid option")
      sys.exit(1)
   return stat_plot_name

def calculate_bootstrap_ci(logger, bs_method, model_data, stat, nrepl, level, 
                           bs_min_samp):
   """! Calculate the upper and lower bound bootstrap statistic from the 
        data from the read in MET .stat file(s)

        Args:
           bs_method         - string of the method to use to
                               calculate the bootstrap confidence intervals
           model_data        - Dataframe containing the model(s)
                               information from the MET .stat
                               files
           stat              - string of the simple statistic
                               name being plotted
           nrepl             - integer of resamples that create the bootstrap
                               distribution
           level             - float confidence level (0.-1.) of the 
                               confidence interval
           bs_min_samp       - minimum number of samples allowed for 
                               confidence intervals to be computed

        Returns:
           stat_values       - Dataframe of the statistic values lower and
                               upper bounds
           status            - integer to provide the parent script with 
                               information about the outcome of the bootstrap 
                               resampling
   """
   status=0
   model_data.reset_index(inplace=True)
   model_data_columns = model_data.columns.values.tolist()
   if model_data_columns == [ 'TOTAL' ]:
      logger.warning("Empty model_data dataframe")
      line_type = 'NULL'
      if (stat == 'fbar_obar' or stat == 'orate_frate'
            or stat == 'baser_frate'):
         stat_values = model_data.loc[:][['TOTAL']]
         stat_values_fbar = model_data.loc[:]['TOTAL']
         stat_values_obar = model_data.loc[:]['TOTAL']
      else:
         stat_values = model_data.loc[:]['TOTAL']
   else:
      if all(elem in model_data_columns for elem in
            ['FBAR', 'OBAR', 'MAE']):
         line_type = 'SL1L2'
         total = model_data.loc[:]['TOTAL']
         fbar = model_data.loc[:]['FBAR']
         obar = model_data.loc[:]['OBAR']
         fobar = model_data.loc[:]['FOBAR']
         ffbar = model_data.loc[:]['FFBAR']
         oobar = model_data.loc[:]['OOBAR']
      elif all(elem in model_data_columns for elem in 
            ['FABAR', 'OABAR', 'MAE']):
         line_type = 'SAL1L2'
         total = model_data.loc[:]['TOTAL']
         fabar = model_data.loc[:]['FABAR']
         oabar = model_data.loc[:]['OABAR']
         foabar = model_data.loc[:]['FOABAR']
         ffabar = model_data.loc[:]['FFABAR']
         ooabar = model_data.loc[:]['OOABAR']
      elif all(elem in model_data_columns for elem in
            ['UFBAR', 'VFBAR']):
         line_type = 'VL1L2'
         total = model_data.loc[:]['TOTAL']
         ufbar = model_data.loc[:]['UFBAR']
         vfbar = model_data.loc[:]['VFBAR']
         uobar = model_data.loc[:]['UOBAR']
         vobar = model_data.loc[:]['VOBAR']
         uvfobar = model_data.loc[:]['UVFOBAR']
         uvffbar = model_data.loc[:]['UVFFBAR']
         uvoobar = model_data.loc[:]['UVOOBAR']
      elif all(elem in model_data_columns for elem in 
            ['UFABAR', 'VFABAR']):
         line_type = 'VAL1L2'
         total = model_data.loc[:]['TOTAL']
         ufabar = model_data.loc[:]['UFABAR']
         vfabar = model_data.loc[:]['VFABAR']
         uoabar = model_data.loc[:]['UOABAR']
         voabar = model_data.loc[:]['VOABAR']
         uvfoabar = model_data.loc[:]['UVFOABAR']
         uvffabar = model_data.loc[:]['UVFFABAR']
         uvooabar = model_data.loc[:]['UVOOABAR']
      elif all(elem in model_data_columns for elem in
            ['VDIFF_SPEED', 'VDIFF_DIR']):
         line_type = 'VCNT'
         total = model_data.loc[:]['TOTAL']
         fbar = model_data.loc[:]['FBAR']
         obar = model_data.loc[:]['OBAR']
         fs_rms = model_data.loc[:]['FS_RMS']
         os_rms = model_data.loc[:]['OS_RMS']
         msve = model_data.loc[:]['MSVE']
         rmsve = model_data.loc[:]['RMSVE']
         fstdev = model_data.loc[:]['FSTDEV']
         ostdev = model_data.loc[:]['OSTDEV']
         fdir = model_data.loc[:]['FDIR']
         odir = model_data.loc[:]['ODIR']
         fbar_speed = model_data.loc[:]['FBAR_SPEED']
         obar_speed = model_data.loc[:]['OBAR_SPEED']
         vdiff_speed = model_data.loc[:]['VDIFF_SPEED']
         vdiff_dir = model_data.loc[:]['VDIFF_DIR']
         speed_err = model_data.loc[:]['SPEED_ERR']
         dir_err = model_data.loc[:]['DIR_ERR']
      elif all(elem in model_data_columns for elem in
            ['FY_OY', 'FN_ON']):
         line_type = 'CTC'
         total = model_data.loc[:]['TOTAL']
         fy_oy = model_data.loc[:]['FY_OY']
         fy_on = model_data.loc[:]['FY_ON']
         fn_oy = model_data.loc[:]['FN_OY']
         fn_on = model_data.loc[:]['FN_ON']
      else:
         logger.error("FATAL ERROR: Could not recognize line type from columns")
         sys.exit(1)
   if str(bs_method).upper() == 'MATCHED_PAIRS':
      if total.sum() < bs_min_samp:
         logger.warning(f"Sample too small for bootstrapping. (Matched pairs"
                        + f" sample size: {total.sum()}; minimum sample"
                        + f" size: {bs_min_samp}")
         status = 1
         return pd.DataFrame(
            dict(CI_LOWER=[np.nan], CI_UPPER=[np.nan], STATUS=[status])
         )
      lower_pctile = 100.*((1.-level)/2.)
      upper_pctile = 100.-lower_pctile
      if line_type == 'CTC':
         fy_oy_all = fy_oy.sum()
         fy_on_all = fy_on.sum()
         fn_oy_all = fn_oy.sum()
         fn_on_all = fn_on.sum()
         total_all = total.sum()
         ctc_all = np.array([fy_oy_all, fy_on_all, fn_oy_all, fn_on_all])
         prob_ctc_all = ctc_all/total_all.astype(float)
         # sample over events in the aggregated contingency table
         fy_oy_samp,fy_on_samp,fn_oy_samp,fn_on_samp = np.random.multinomial(
            total_all, 
            prob_ctc_all, 
            size=nrepl
         ).T
      elif line_type == 'SL1L2':
         fo_matched_est = []
         fvar = ffbar-fbar*fbar
         ovar = oobar-obar*obar
         focovar = fobar-fbar*obar
         for i, _ in enumerate(total):
            fo_matched_est_i = np.random.multivariate_normal(
               [fbar[i], obar[i]], 
               [[fvar[i],focovar[i]],[focovar[i],ovar[i]]], 
               size=int(total[i])
            )
            fo_matched_est.append(fo_matched_est_i)
         fo_matched_est = np.vstack(fo_matched_est)
         fbar_est_mean = fo_matched_est[:,0].mean()
         obar_est_mean = fo_matched_est[:,1].mean()
         fobar_est_mean = np.mean(np.prod(fo_matched_est, axis=1))
         ffbar_est_mean = np.mean(fo_matched_est[:,0]*fo_matched_est[:,0])
         oobar_est_mean = np.mean(fo_matched_est[:,1]*fo_matched_est[:,1])
         max_mem_per_array = 32 # MB
         max_array_size = max_mem_per_array*1E6/8
         batch_size = int(max_array_size/len(fo_matched_est))
         fbar_est_samples = []
         obar_est_samples = []
         fobar_est_samples = []
         ffbar_est_samples = []
         oobar_est_samples = []
         # attempt to bootstrap in batches to save time
         # if sampling array is too large for batches, traditional bootstrap
         if batch_size <= 1:
            for _ in range(nrepl):
               fo_matched_indices = np.random.choice(
                  len(fo_matched_est), 
                  size=fo_matched_est.size, 
                  replace=True
               )
               f_est_bs, o_est_bs = fo_matched_est[fo_matched_indices].T
               fbar_est_samples.append(f_est_bs.mean())
               obar_est_samples.append(o_est_bs.mean())
               fobar_est_samples.append(np.mean(f_est_bs*o_est_bs))
               ffbar_est_samples.append(np.mean(f_est_bs*f_est_bs))
               oobar_est_samples.append(np.mean(o_est_bs*o_est_bs))
            fbar_est_samp = np.array(fbar_est_samples)
            obar_est_samp = np.array(obar_est_samples)
            fobar_est_samp = np.array(fobar_est_samples)
            ffbar_est_samp = np.array(ffbar_est_samples)
            oobar_est_samp = np.array(oobar_est_samples)
         else:
            rep_arr = np.arange(0,nrepl)
            for b in range(0, nrepl, batch_size):
               curr_batch_size = len(rep_arr[b:b+batch_size])
               idxs = [
                  np.random.choice(
                     len(fo_matched_est), 
                     size=fo_matched_est.size, 
                     replace=True
                  ) 
                  for _ in range(curr_batch_size)
               ]
               f_est_bs, o_est_bs = [
                  np.take(fo_matched_est.T[i], idxs) for i in [0,1]
               ]
               fbar_est_samples.append(f_est_bs.mean(axis=1))
               obar_est_samples.append(o_est_bs.mean(axis=1))
               fobar_est_samples.append((f_est_bs*o_est_bs).mean(axis=1))
               ffbar_est_samples.append((f_est_bs*f_est_bs).mean(axis=1))
               oobar_est_samples.append((o_est_bs*o_est_bs).mean(axis=1))
            fbar_est_samp = np.concatenate((fbar_est_samples))
            obar_est_samp = np.concatenate((obar_est_samples))
            fobar_est_samp = np.concatenate((fobar_est_samples))
            ffbar_est_samp = np.concatenate((ffbar_est_samples))
            oobar_est_samp = np.concatenate((oobar_est_samples))
      else:
         logger.error("FATAL ERROR: "+line_type+" is not currently a valid option")
         sys.exit(1)
   elif str(bs_method).upper() == 'FORECASTS':
      if total.size < bs_min_samp:
         logger.warning(f"Sample too small for bootstrapping. (Forecasts"
                        + f" sample size: {total.size}; minimum sample"
                        + f" size: {bs_min_samp}")
         status = 1
         return pd.DataFrame(
            dict(CI_LOWER=[np.nan], CI_UPPER=[np.nan], STATUS=[status])
         )
      lower_pctile = 100.*((1.-level)/2.)
      upper_pctile = 100.-lower_pctile
      if line_type == 'CTC':
         ctc = np.array([fy_oy, fy_on, fn_oy, fn_on])
         fy_oy_samp, fy_on_samp, fn_oy_samp, fn_on_samp = [
            [] for item in range(4)
         ]
         for _ in range(nrepl):
            ctc_bs = ctc.T[
               np.random.choice(
                  range(len(ctc.T)), 
                  size=len(ctc.T), 
                  replace=True
               )
            ].sum(axis=0)
            fy_oy_samp.append(ctc_bs[0])
            fy_on_samp.append(ctc_bs[1])
            fn_oy_samp.append(ctc_bs[2])
            fn_on_samp.append(ctc_bs[3])
         fy_oy_samp = np.array(fy_oy_samp)
         fy_on_samp = np.array(fy_on_samp)
         fn_oy_samp = np.array(fn_oy_samp)
         fn_on_samp = np.array(fn_on_samp)
      elif line_type == 'SL1L2':
         fbar_est_mean = fbar.mean()
         obar_est_mean = obar.mean()
         fobar_est_mean = fobar.mean()
         ffbar_est_mean = ffbar.mean()
         oobar_est_mean = oobar.mean()
         max_mem_per_array = 32 # MB
         max_array_size = max_mem_per_array*1E6/8
         batch_size = int(max_array_size/len(fbar))
         fbar_samples = []
         obar_samples = []
         fobar_samples = []
         ffbar_samples = []
         oobar_samples = []
         # attempt to bootstrap in batches to save time
         # if sampling array is too large for batches, traditional bootstrap
         if batch_size <= 1:
            for _ in range(nrepl):
               idx = np.random.choice(
                  len(fbar), 
                  size=fbar.size, 
                  replace=True
               )
               fbar_bs, obar_bs, fobar_bs, ffbar_bs, oobar_bs = [
                  summary_stat[idx].T 
                  for summary_stat in [fbar, obar, fobar, ffbar, oobar]
               ]
               fbar_samples.append(fbar_bs.mean())
               obar_samples.append(obar_bs.mean())
               fobar_samples.append(fobar_bs.mean())
               ffbar_samples.append(ffbar_bs.mean())
               oobar_samples.append(oobar_bs.mean())
            fbar_est_samp = np.array(fbar_samples)
            obar_est_samp = np.array(obar_samples)
            fobar_est_samp = np.array(fobar_samples)
            ffbar_est_samp = np.array(ffbar_samples)
            oobar_est_samp = np.array(oobar_samples)
         else:
            rep_arr = np.arange(0,nrepl)
            for b in range(0, nrepl, batch_size):
               curr_batch_size = len(rep_arr[b:b+batch_size])
               idxs = [
                  np.random.choice(
                     len(fbar), 
                     size=fbar.size, 
                     replace=True
                  ) 
                  for _ in range(curr_batch_size)
               ]
               fbar_bs, obar_bs, fobar_bs, ffbar_bs, oobar_bs = [
                  np.take(np.array(summary_stat), idxs) 
                  for s, summary_stat in enumerate([fbar, obar, fobar, ffbar, oobar])
               ]
               fbar_samples.append(fbar_bs.mean(axis=1))
               obar_samples.append(obar_bs.mean(axis=1))
               fobar_samples.append(fobar_bs.mean(axis=1))
               ffbar_samples.append(ffbar_bs.mean(axis=1))
               oobar_samples.append(oobar_bs.mean(axis=1))
            fbar_est_samp = np.concatenate((fbar_samples))
            obar_est_samp = np.concatenate((obar_samples))
            fobar_est_samp = np.concatenate((fobar_samples))
            ffbar_est_samp = np.concatenate((ffbar_samples))
            oobar_est_samp = np.concatenate((oobar_samples))
      else:
         logger.error("FATAL ERROR: "+line_type+" is not currently a valid option")
         sys.exit(1)
   else:
      logger.error("FATAL ERROR: "+bs_method+" is not a valid option")
      sys.exit(1)
   if stat in ['bias','me']:
        if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
            if line_type == 'SL1L2':
                stat_values_mean = np.mean(fbar_est_mean) - np.mean(obar_est_mean)
                stat_values = fbar_est_samp - obar_est_samp
            elif line_type == 'CTC':
                stat_values = (fy_oy_samp + fy_on_samp)/(fy_oy_samp + fn_oy_samp)
   elif stat == 'esd':
       if line_type == 'SL1L2':
           var_e = ffbar + oobar - fbar*fbar - obar*obar - 2*fobar + 2*fbar*obar
           stat_values = np.sqrt(var_e)
   elif stat == 'rmse':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            stat_values_pre_mean = np.sqrt(
               ffbar_est_mean + oobar_est_mean - 2*fobar_est_mean
            )
            stat_values_mean = np.mean(stat_values_pre_mean)
            stat_values = np.sqrt(
               ffbar_est_samp + oobar_est_samp - 2*fobar_est_samp
            )
   elif stat == 'bcrmse':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            var_f_mean = (
               np.mean(ffbar_est_mean) 
               - np.mean(fbar_est_mean)*np.mean(fbar_est_mean)
            )
            var_o_mean = (
               np.mean(oobar_est_mean) 
               - np.mean(obar_est_mean)*np.mean(obar_est_mean)
            )
            covar_mean = (
               np.mean(fobar_est_mean) 
               - np.mean(fbar_est_mean)*np.mean(obar_est_mean)
            )
            stat_values_mean = np.sqrt(var_f_mean+var_o_mean-2*covar_mean)
            var_f = ffbar_est_samp - fbar_est_samp*fbar_est_samp
            var_o = oobar_est_samp - obar_est_samp*obar_est_samp
            covar = fobar_est_samp - fbar_est_samp*obar_est_samp
            stat_values = np.sqrt(var_f+var_o-2*covar)
   elif stat == 'msess':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            mse_mean = ffbar_est_mean + oobar_est_mean - 2*fobar_est_mean
            var_o_mean = oobar_est_mean - obar_est_mean*obar_est_mean
            stat_values_pre_mean = 1 - mse_mean/var_o_mean
            stat_values_mean = np.mean(stat_values_pre_mean)
            mse = ffbar_est_samp + oobar_est_samp - 2*fobar_est_samp
            var_o = oobar_est_samp - obar_est_samp*obar_est_samp
            stat_values = 1 - mse/var_o
   elif stat == 'rsd':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            var_f_mean = ffbar_est_mean - fbar_est_mean*fbar_est_mean
            var_o_mean = oobar_est_mean - obar_est_mean*obar_est_mean
            stat_values_pre_mean = np.sqrt(var_f_mean)/np.sqrt(var_o_mean)
            stat_values_mean = np.mean(stat_values_pre_mean)
            var_f = ffbar_est_samp - fbar_est_samp*fbar_est_samp
            var_o = oobar_est_samp - obar_est_samp*obar_est_samp
            stat_values = np.sqrt(var_f)/np.sqrt(var_o)
   elif stat == 'rmse_md':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            stat_values_pre_mean = np.sqrt((fbar_est_mean-obar_est_mean)**2)
            stat_values_mean = np.mean(stat_values_pre_mean)
            stat_values = np.sqrt((fbar_est_samp-obar_est_samp)**2)
   elif stat == 'rmse_pv':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            var_f_mean = ffbar_est_mean - fbar_est_mean**2
            var_o_mean = oobar_est_mean - obar_est_mean**2
            covar_mean = fobar_est_mean - fbar_est_mean*obar_est_mean
            R_mean = covar_mean/np.sqrt(var_f_mean*var_o_mean)
            stat_values_pre_mean = np.sqrt(
               var_f_mean 
               + var_o_mean 
               - 2*np.sqrt(var_f_mean*var_o_mean)*R_mean
            )
            stat_values_mean = np.mean(stat_values_pre_mean)
            var_f = ffbar_est_samp - fbar_est_samp**2
            var_o = oobar_est_samp - obar_est_samp**2
            covar = fobar_est_samp - fbar_est_samp*obar_est_samp
            R = covar/np.sqrt(var_f*var_o)
            stat_values = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
   elif stat == 'pcor':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            #var_f_mean = ffbar_est_mean - fbar_est_mean*obar_est_mean
            var_f_mean = ffbar_est_mean - fbar_est_mean*fbar_est_mean
            var_o_mean = oobar_est_mean - obar_est_mean*obar_est_mean
            covar_mean = fobar_est_mean - fbar_est_mean*obar_est_mean
            stat_values_pre_mean = covar_mean/np.sqrt(var_f_mean*var_o_mean)
            stat_values_mean = np.mean(stat_values_pre_mean)
            #var_f = ffbar_est_samp - fbar_est_samp*obar_est_samp
            var_f = ffbar_est_samp - fbar_est_samp*fbar_est_samp
            var_o = oobar_est_samp - obar_est_samp*obar_est_samp
            covar = fobar_est_samp - fbar_est_samp*obar_est_samp
            stat_values = covar/np.sqrt(var_f*var_o)
   elif stat == 'acc':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SAL1L2':
            var_f_mean = ffabar_est_mean - fabar_est_mean*fabar_est_mean
            var_o_mean = ooabar_est_mean - oabar_est_mean*oabar_est_mean
            covar_mean = foabar_est_mean - fabar_est_mean*oabar_est_mean
            stat_values_pre_mean = covar_mean/np.sqrt(var_f_mean*var_o_mean)
            stat_values_mean = np.mean(stat_values_pre_mean)
            var_f = ffabar_est_samp - fabar_est_samp*fabar_est_samp
            var_o = ooabar_est_samp - oabar_est_samp*oabar_est_samp
            covar = foabar_est_samp - fabar_est_samp*oabar_est_samp
            stat_values = covar_samp/np.sqrt(var_f_samp*var_o_samp)
   elif stat == 'fbar':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            stat_values_pre_mean = fbar_est_mean
            stat_values_mean = np.mean(stat_values_pre_mean)
            stat_values = fbar_est_samp
   elif stat == 'obar':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            stat_values_pre_mean = obar_est_mean
            stat_values_mean = np.mean(stat_values_pre_mean)
            stat_values = obar_est_samp
   elif stat == 'orate' or stat == 'baser':
      if line_type == 'CTC':
         total_mean = (
            np.sum(fy_oy)+np.sum(fy_on)+np.sum(fn_oy)+np.sum(fn_on)
         )
         stat_values_mean = (np.sum(fy_oy)+np.sum(fn_oy))/total_mean
         total = (fy_oy_samp + fy_on_samp + fn_oy_samp + fn_on_samp)
         stat_values = (fy_oy_samp + fn_oy_samp)/total
   elif stat == 'frate':
      if line_type == 'CTC':
         total_mean = (
            np.sum(fy_oy)+np.sum(fy_on)+np.sum(fn_oy)+np.sum(fn_on)
         )
         stat_values_mean = (np.sum(fy_oy)+np.sum(fy_on))/total_mean
         total = (fy_oy_samp + fy_on_samp + fn_oy_samp + fn_on_samp)
         stat_values = (fy_oy_samp + fy_on_samp)/total
   elif stat == 'orate_frate' or stat == 'baser_frate':
      if line_type == 'CTC':
         total_mean = (
            np.sum(fy_oy)+np.sum(fy_on)+np.sum(fn_oy)+np.sum(fn_on)
         )
         stat_values_fbar_mean = (
            np.sum(fy_oy)+np.sum(fy_on)
         )/total_mean
         stat_values_obar_mean = (
            np.sum(fy_oy)+np.sum(fn_oy)
         )/total_mean
         stat_values_mean = pd.concat(
            [stat_values_fbar_mean, stat_values_obar_mean]
         )
         total = (fy_oy_samp + fy_on_samp + fn_oy_samp + fn_on_samp)
         stat_values_fbar = (fy_oy_samp + fy_on_samp)/total
         stat_values_obar = (fy_oy_samp + fn_oy_samp)/total
         stat_values = pd.concat(
            [stat_values_fbar, stat_values_obar], axis=1
         )
   elif stat == 'accuracy':
      if line_type == 'CTC':
         total_mean = (
            np.sum(fy_oy)+np.sum(fy_on)+np.sum(fn_oy)+np.sum(fn_on)
         )
         stat_values_mean = (
            np.sum(fy_oy)+np.sum(fn_on)
         )/total_mean
         total = (fy_oy_samp + fy_on_samp + fn_oy_samp + fn_on_samp)
         stat_values = (fy_oy_samp + fn_on_samp)/total
   elif stat == 'fbias':
      if line_type == 'CTC':
         stat_values_mean = (
            (np.sum(fy_oy)+np.sum(fy_on))
            /(np.sum(fy_oy)+np.sum(fn_oy))
         )
         stat_values = (fy_oy_samp + fy_on_samp)/(fy_oy_samp + fn_oy_samp)
   elif stat == 'pod' or stat == 'hrate':
      if line_type == 'CTC':
         stat_values_mean = np.sum(fy_oy)/(np.sum(fy_oy)+np.sum(fn_oy))
         stat_values = fy_oy_samp/(fy_oy_samp + fn_oy_samp)
   elif stat == 'pofd' or stat == 'farate':
      if line_type == 'CTC':
         stat_values_mean = np.sum(fy_on)/(np.sum(fy_on)+np.sum(fn_on))
         stat_values = fy_on_samp/(fy_on_samp + fn_on_samp)
   elif stat == 'podn':
      if line_type == 'CTC':
         stat_values_mean = np.sum(fn_on)/(np.sum(fy_on)+np.sum(fn_on))
         stat_values = fn_on_samp/(fy_on_samp + fn_on_samp)
   elif stat == 'faratio':
      if line_type == 'CTC':
         stat_values_mean = np.sum(fy_on)/(np.sum(fy_on)+np.sum(fy_oy))
         stat_values = fy_on_samp/(fy_on_samp + fy_oy_samp)
   elif stat == 'sratio':
      if line_type == 'CTC':
         stat_values_mean = (
            1. - (np.sum(fy_on)/(np.sum(fy_on)+np.sum(fy_oy)))
         )
         stat_values = 1. - (fy_on_samp/(fy_on_samp + fy_oy_samp))
   elif stat == 'csi' or stat == 'ts':
      if line_type == 'CTC':
         stat_values_mean = (
            np.sum(fy_oy)
            /(np.sum(fy_oy)+np.sum(fy_on)+np.sum(fn_oy))
         )
         stat_values = fy_oy_samp/(fy_oy_samp + fy_on_samp + fn_oy_samp)
   elif stat == 'gss' or stat == 'ets':
      if line_type == 'CTC':
         total_mean = (
            np.sum(fy_oy)+np.sum(fy_on)+np.sum(fn_oy)+np.sum(fn_on)
         )
         C_mean = (
            (np.sum(fy_oy)+np.sum(fy_on))
            *(np.sum(fy_oy)+np.sum(fn_oy))
         )/total_mean
         stat_values_mean = (
            (np.sum(fy_oy)-C_mean)
            /(np.sum(fy_oy)+np.sum(fy_on)+np.sum(fn_oy)-C_mean)
         )
         total = (fy_oy_samp + fy_on_samp + fn_oy_samp + fn_on_samp)
         C = ((fy_oy_samp + fy_on_samp)*(fy_oy_samp + fn_oy_samp))/total
         stat_values = (
            (fy_oy_samp - C)/(fy_oy_samp + fy_on_samp + fn_oy_samp - C)
         )
   elif stat == 'hk' or stat == 'tss' or stat == 'pss':
      if line_type == 'CTC':
         stat_values_mean = (
            (np.sum(fy_oy)*np.sum(fn_on)-np.sum(fy_on)*np.sum(fn_oy))
            /(
               (np.sum(fy_oy)+np.sum(fn_oy))
               *(np.sum(fy_on)+np.sum(fn_on))
            )
         )
         stat_values = (
            ((fy_oy_samp*fn_on_samp)-(fy_on_samp*fn_oy_samp))
            /((fy_oy_samp+fn_oy_samp)*(fy_on_samp+fn_on_samp))
         )
   elif stat == 'hss':
      if line_type == 'CTC':
         total_mean = (
            np.sum(fy_oy)+np.sum(fy_on)+np.sum(fn_oy)+np.sum(fn_on)
         )
         Ca_mean = (
            (np.sum(fy_oy)+np.sum(fy_on))
            *(np.sum(fy_oy)+np.sum(fn_oy))
         )
         Cb_mean = (
            (np.sum(fn_oy)+np.sum(fn_on))
            *(np.sum(fy_on)+np.sum(fn_on))
         )
         C_mean = (Ca_mean + Cb_mean)/total_mean
         stat_values_mean = (
            (np.sum(fy_oy)+np.sum(fn_on)-C_mean)
            /(total_mean-C_mean)
         )
         total = (fy_oy_samp + fy_on_samp + fn_oy_samp + fn_on_samp)
         Ca = (fy_oy_samp+fy_on_samp)*(fy_oy_samp+fn_oy_samp)
         Cb = (fn_oy_samp+fn_on_samp)*(fy_on_samp+fn_on_samp)
         C = (Ca + Cb)/total
         stat_values = (fy_oy_samp + fn_on_samp - C)/(total - C)
   elif stat == 'si':
      if str(bs_method).upper() in ['MATCHED_PAIRS','FORECASTS']:
         if line_type == 'SL1L2':
            stat_values_pre_mean = np.sqrt(
               ffbar_est_mean + oobar_est_mean - 2*fobar_est_mean
            )
            stat_values_mean = np.mean(stat_values_pre_mean)
            stat_values_rmse = np.sqrt(
               ffbar_est_samp + oobar_est_samp - 2*fobar_est_samp
            )
            stat_values = 100 * stat_values_rmse / obar_est_mean
            stat_values = stat_values[stat_values<=200]  #get rid of infinite values
   else:
      logger.error("FATAL ERROR: "+stat+" is not a valid option")
      sys.exit(1)
   stat_deltas = stat_values-stat_values_mean
   stat_ci_lower = np.nanpercentile(stat_deltas, lower_pctile)
   stat_ci_upper = np.nanpercentile(stat_deltas, upper_pctile)
   return pd.DataFrame(
      dict(CI_LOWER=[stat_ci_lower], CI_UPPER=[stat_ci_upper], STATUS=[status])
   )

def calculate_stat(logger, model_data, stat):
   """! Calculate the statistic from the data from the
        read in MET .stat file(s)

        Args:
           model_data        - Dataframe containing the model(s)
                               information from the MET .stat
                               files
           stat              - string of the simple statistic
                               name being plotted

        Returns:
           stat_values       - Dataframe of the statistic values
           stat_values_array - array of the statistic values
           stat_plot_name    - string of the formal statistic
                               name being plotted
   """
   model_data_columns = model_data.columns.values.tolist()
   if model_data_columns == [ 'TOTAL' ]:
      logger.warning("Empty model_data dataframe")
      line_type = 'NULL'
      if (stat == 'fbar_obar' or stat == 'orate_frate'
            or stat == 'baser_frate'):
         stat_values = model_data.loc[:][['TOTAL']]
         stat_values_fbar = model_data.loc[:]['TOTAL']
         stat_values_obar = model_data.loc[:]['TOTAL']
      else:
         stat_values = model_data.loc[:]['TOTAL']
   else:
      if all(elem in model_data_columns for elem in
            ['FBAR', 'OBAR', 'MAE']):
         line_type = 'SL1L2'
         fbar = model_data.loc[:]['FBAR']
         obar = model_data.loc[:]['OBAR']
         fobar = model_data.loc[:]['FOBAR']
         ffbar = model_data.loc[:]['FFBAR']
         oobar = model_data.loc[:]['OOBAR']
      elif all(elem in model_data_columns for elem in 
            ['FABAR', 'OABAR', 'MAE']):
         line_type = 'SAL1L2'
         fabar = model_data.loc[:]['FABAR']
         oabar = model_data.loc[:]['OABAR']
         foabar = model_data.loc[:]['FOABAR']
         ffabar = model_data.loc[:]['FFABAR']
         ooabar = model_data.loc[:]['OOABAR']
      elif all(elem in model_data_columns for elem in
            ['UFBAR', 'VFBAR']):
         line_type = 'VL1L2'
         ufbar = model_data.loc[:]['UFBAR']
         vfbar = model_data.loc[:]['VFBAR']
         uobar = model_data.loc[:]['UOBAR']
         vobar = model_data.loc[:]['VOBAR']
         uvfobar = model_data.loc[:]['UVFOBAR']
         uvffbar = model_data.loc[:]['UVFFBAR']
         uvoobar = model_data.loc[:]['UVOOBAR']
      elif all(elem in model_data_columns for elem in 
            ['UFABAR', 'VFABAR']):
         line_type = 'VAL1L2'
         ufabar = model_data.loc[:]['UFABAR']
         vfabar = model_data.loc[:]['VFABAR']
         uoabar = model_data.loc[:]['UOABAR']
         voabar = model_data.loc[:]['VOABAR']
         uvfoabar = model_data.loc[:]['UVFOABAR']
         uvffabar = model_data.loc[:]['UVFFABAR']
         uvooabar = model_data.loc[:]['UVOOABAR']
      elif all(elem in model_data_columns for elem in
            ['VDIFF_SPEED', 'VDIFF_DIR']):
         line_type = 'VCNT'
         fbar = model_data.loc[:]['FBAR']
         obar = model_data.loc[:]['OBAR']
         fs_rms = model_data.loc[:]['FS_RMS']
         os_rms = model_data.loc[:]['OS_RMS']
         msve = model_data.loc[:]['MSVE']
         rmsve = model_data.loc[:]['RMSVE']
         fstdev = model_data.loc[:]['FSTDEV']
         ostdev = model_data.loc[:]['OSTDEV']
         fdir = model_data.loc[:]['FDIR']
         odir = model_data.loc[:]['ODIR']
         fbar_speed = model_data.loc[:]['FBAR_SPEED']
         obar_speed = model_data.loc[:]['OBAR_SPEED']
         vdiff_speed = model_data.loc[:]['VDIFF_SPEED']
         vdiff_dir = model_data.loc[:]['VDIFF_DIR']
         speed_err = model_data.loc[:]['SPEED_ERR']
         dir_err = model_data.loc[:]['DIR_ERR']
      elif all(elem in model_data_columns for elem in
            ['FY_OY', 'FN_ON']):
         line_type = 'CTC'
         total = model_data.loc[:]['TOTAL']
         fy_oy = model_data.loc[:]['FY_OY']
         fy_on = model_data.loc[:]['FY_ON']
         fn_oy = model_data.loc[:]['FN_OY']
         fn_on = model_data.loc[:]['FN_ON']
      else:
         logger.error("FATAL ERROR: Could not recognize line type from columns")
         sys.exit(1)
   stat_plot_name = get_stat_plot_name(logger, stat)
   if stat in ['bias','me']:
      if line_type == 'SL1L2':
         stat_values = fbar - obar
      elif line_type == 'VL1L2':
         stat_values = np.sqrt(uvffbar) - np.sqrt(uvoobar)
      elif line_type == 'VCNT':
         stat_values = fbar - obar
      elif line_type == 'CTC':
         stat_values = (fy_oy + fy_on)/(fy_oy + fn_oy)
   elif stat == 'esd':
      if line_type == 'SL1L2':
         stat_values = np.sqrt(ffbar + oobar - fbar*fbar - obar*obar - 2*fobar + 2*fbar*obar)
   elif stat == 'rmse':
      if line_type == 'SL1L2':
         stat_values = np.sqrt(ffbar + oobar - 2*fobar)
      elif line_type == 'VL1L2':
         stat_values = np.sqrt(uvffbar + uvoobar - 2*uvfobar)
   elif stat == 'bcrmse':
      if line_type == 'SL1L2':
         var_f = ffbar - fbar*fbar
         var_o = oobar - obar*obar
         covar = fobar - fbar*obar
         stat_values = np.sqrt(var_f + var_o - 2*covar)
      elif line_type == 'VL1L2':
         var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
         var_o = uvoobar - uobar*uobar - vobar*vobar
         covar = uvfobar - ufbar*uobar - vfbar*vobar
         stat_values = np.sqrt(var_f + var_o - 2*covar)
   elif stat == 'msess':
      if line_type == 'SL1L2':
         mse = ffbar + oobar - 2*fobar
         var_o = oobar - obar*obar
         stat_values = 1 - mse/var_o
      elif line_type == 'VL1L2':
         mse = uvffbar + uvoobar - 2*uvfobar
         var_o = uvoobar - uobar*uobar - vobar*vobar
         stat_values = 1 - mse/var_o
   elif stat == 'rsd':
      if line_type == 'SL1L2':
         var_f = ffbar - fbar*fbar
         var_o = oobar - obar*obar
         stat_values = np.sqrt(var_f)/np.sqrt(var_o)
      elif line_type == 'VL1L2':
         var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
         var_o = uvoobar - uobar*uobar - vobar*vobar
         stat_values = np.sqrt(var_f)/np.sqrt(var_o)
      elif line_type == 'VCNT':
         stat_values = fstdev/ostdev
   elif stat == 'rmse_md':
      if line_type == 'SL1L2':
         stat_values = np.sqrt((fbar-obar)**2)
      elif line_type == 'VL1L2':
         stat_values = np.sqrt((ufbar - uobar)**2 + (vfbar - vobar)**2)
   elif stat == 'rmse_pv':
      if line_type == 'SL1L2':
         var_f = ffbar - fbar**2
         var_o = oobar - obar**2
         covar = fobar - fbar*obar
         R = covar/np.sqrt(var_f*var_o)
         stat_values = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
      elif line_type == 'VL1L2':
         var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
         var_o = uvoobar - uobar*uobar - vobar*vobar
         covar = uvfobar - ufbar*uobar - vfbar*vobar
         R = covar/np.sqrt(var_f*var_o)
         stat_values = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
   elif stat == 'pcor':
      if line_type == 'SL1L2':
         #var_f = ffbar - fbar*obar
         var_f = ffbar - fbar*fbar
         var_o = oobar - obar*obar
         covar = fobar - fbar*obar
         stat_values = covar/np.sqrt(var_f*var_o)
      elif line_type == 'VL1L2':
         var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
         var_o = uvoobar - uobar*uobar - vobar*vobar
         covar = uvfobar - ufbar*uobar - vfbar*vobar
         stat_values = covar/np.sqrt(var_f*var_o)
   elif stat == 'acc':
      if line_type == 'SAL1L2':
         var_f = ffabar - fabar*fabar
         var_o = ooabar - oabar*oabar
         covar = foabar - fabar*oabar
         stat_values = covar/np.sqrt(var_f*var_o)
      if line_type == 'VAL1L2':
         stat_values = uvfoabar/np.sqrt(uvffabar*uvooabar)
   elif stat == 'fbar':
      if line_type == 'SL1L2':
         stat_values = fbar
      elif line_type == 'VL1L2':
         stat_values = np.sqrt(uvffbar)
      elif line_type == 'VCNT':
         stat_values = fbar
   elif stat == 'obar':
      if line_type == 'SL1L2':
         stat_values = obar
      elif line_type == 'VL1L2':
         stat_values = np.sqrt(uvoobar)
      elif line_type == 'VCNT':
         stat_values = obar
   elif stat == 'fbar_obar':
      if line_type == 'SL1L2':
         stat_values = model_data.loc[:][['FBAR', 'OBAR']]
         stat_values_fbar = model_data.loc[:]['FBAR']
         stat_values_obar = model_data.loc[:]['OBAR']
      elif line_type == 'VL1L2':
         stat_values = model_data.loc[:][['UVFFBAR', 'UVOOBAR']]
         stat_values_fbar = np.sqrt(model_data.loc[:]['UVFFBAR'])
         stat_values_obar = np.sqrt(model_data.loc[:]['UVOOBAR'])
      elif line_type == 'VCNT':
         stat_values = model_data.loc[:][['FBAR', 'OBAR']]
         stat_values_fbar = model_data.loc[:]['FBAR']
         stat_values_obar = model_data.loc[:]['OBAR']
   elif stat == 'speed_err':
      if line_type == 'VCNT':
         stat_values = speed_err
   elif stat == 'dir_err':
      if line_type == 'VCNT':
         stat_values = dir_err
   elif stat == 'rmsve':
      if line_type == 'VCNT':
         stat_values = rmsve
   elif stat == 'vdiff_speed':
      if line_type == 'VCNT':
         stat_values = vdiff_speed
   elif stat == 'vdiff_dir':
      if line_type == 'VCNT':
         stat_values = vdiff_dir
   elif stat == 'fbar_obar_speed':
      if line_type == 'VCNT':
         stat_values = model_data.loc[:][('FBAR_SPEED', 'OBAR_SPEED')]
   elif stat == 'fbar_obar_dir':
      if line_type == 'VCNT':
         stat_values = model_data.loc[:][('FDIR', 'ODIR')]
   elif stat == 'fbar_speed':
      if line_type == 'VCNT':
         stat_values = fbar_speed
   elif stat == 'fbar_dir':
      if line_type == 'VCNT':
         stat_values = fdir
   elif stat == 'orate' or stat == 'baser':
      if line_type == 'CTC':
         stat_values = (fy_oy + fn_oy)/total
   elif stat == 'frate':
      if line_type == 'CTC':
         stat_values = (fy_oy + fy_on)/total
   elif stat == 'orate_frate' or stat == 'baser_frate':
      if line_type == 'CTC':
         stat_values_fbar = (fy_oy + fy_on)/total
         stat_values_obar = (fy_oy + fn_oy)/total
         stat_values = pd.concat(
            [stat_values_fbar, stat_values_obar], axis=1
         )
   elif stat == 'accuracy':
      if line_type == 'CTC':
         stat_values = (fy_oy + fn_on)/total
   elif stat == 'fbias':
      if line_type == 'CTC':
         stat_values = (fy_oy + fy_on)/(fy_oy + fn_oy)
   elif stat == 'pod' or stat == 'hrate':
      if line_type == 'CTC':
         stat_values = fy_oy/(fy_oy + fn_oy)
   elif stat == 'pofd' or stat == 'farate':
      if line_type == 'CTC':
         stat_values = fy_on/(fy_on + fn_on)
   elif stat == 'podn':
      if line_type == 'CTC':
         stat_values = fn_on/(fy_on + fn_on)
   elif stat == 'faratio':
      if line_type == 'CTC':
         stat_values = fy_on/(fy_on + fy_oy)
   elif stat == 'sratio':
      if line_type == 'CTC':
         stat_values = 1. - (fy_on/(fy_on + fy_oy))
   elif stat == 'csi' or stat == 'ts':
      if line_type == 'CTC':
         stat_values = fy_oy/(fy_oy + fy_on + fn_oy)
   elif stat == 'gss' or stat == 'ets':
      if line_type == 'CTC':
         C = ((fy_oy + fy_on)*(fy_oy + fn_oy))/total
         stat_values = (fy_oy - C)/(fy_oy + fy_on + fn_oy - C)
   elif stat == 'hk' or stat == 'tss' or stat == 'pss':
      if line_type == 'CTC':
         stat_values = (
            ((fy_oy*fn_on)-(fy_on*fn_oy))/((fy_oy+fn_oy)*(fy_on+fn_on))
         )
   elif stat == 'hss':
      if line_type == 'CTC':
         Ca = (fy_oy+fy_on)*(fy_oy+fn_oy)
         Cb = (fn_oy+fn_on)*(fy_on+fn_on)
         C = (Ca + Cb)/total
         stat_values = (fy_oy + fn_on - C)/(total - C)
   elif stat == 'si':
       if line_type == 'SL1L2':
           stat_values = 100*(np.sqrt(ffbar + oobar - 2*fobar))/obar
           stat_values = stat_values[stat_values<=200]  #get rid of infinite values
   else:
      logger.error("FATAL ERROR: "+stat+" is not a valid option")
      sys.exit(1)
   nindex = stat_values.index.nlevels
   if stat == 'fbar_obar' or stat == 'orate_frate' or stat == 'baser_frate':
      try:
         if nindex == 1:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            stat_values_array_fbar = (
               np.ma.masked_invalid(
                  stat_values_fbar.values.reshape(index0)
               )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            stat_values_array_obar = (
               np.ma.masked_invalid(
                  stat_values_obar.values.reshape(index0)
               )
            )
         elif nindex == 2:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            index1 = len(stat_values_fbar.index.get_level_values(1).unique())
            stat_values_array_fbar = (
               np.ma.masked_invalid(
                  stat_values_fbar.values.reshape(index0, index1)
               )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            index1 = len(stat_values_obar.index.get_level_values(1).unique())
            stat_values_array_obar = (
               np.ma.masked_invalid(
                  stat_values_obar.values.reshape(index0, index1)
               )
            )
         elif nindex == 3:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            index1 = len(stat_values_fbar.index.get_level_values(1).unique())
            index2 = len(stat_values_fbar.index.get_level_values(2).unique())
            stat_values_array_fbar = (
               np.ma.masked_invalid(
                  stat_values_fbar.values.reshape(index0, index1, index2)
               )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            index1 = len(stat_values_obar.index.get_level_values(1).unique())
            index2 = len(stat_values_obar.index.get_level_values(2).unique())
            stat_values_array_obar = (
               np.ma.masked_invalid(
                  stat_values_obar.values.reshape(index0, index1, index2)
               )
            )
         stat_values_array = np.ma.array([stat_values_array_fbar,
                                          stat_values_array_obar])
      except ValueError as e:
         logger.warning(e)
         logger.warning("This is usually OK, and will happen if "
                        + "event_equalization=False.") 
         logger.warning("Setting stat_values_array to Nonetype.")
         stat_values_array = None
         logger.warning("Continuing ...")
   else:
      try:
         if nindex == 1:
            index0 = len(stat_values.index.get_level_values(0).unique())
            stat_values_array = (
               np.ma.masked_invalid(
                  stat_values.values.reshape(1, index0)
               )
            )
         elif nindex == 2:
            index0 = len(stat_values.index.get_level_values(0).unique())
            index1 = len(stat_values.index.get_level_values(1).unique())
            stat_values_array = (
               np.ma.masked_invalid(
                  stat_values.values.reshape(1, index0, index1)
               )
            )
         elif nindex == 3:
            index0 = len(stat_values.index.get_level_values(0).unique())
            index1 = len(stat_values.index.get_level_values(1).unique())
            index2 = len(stat_values.index.get_level_values(2).unique())
            stat_values_array = (
               np.ma.masked_invalid(
                  stat_values.values.reshape(1, index0, index1, index2)
               )
            )
      except ValueError as e:
         logger.warning(e)
         logger.warning("This is usually OK, and will happen if "
                        + "event_equalization=False.") 
         logger.warning("Setting stat_values_array to Nonetype.")
         stat_values_array = None
         logger.warning("Continuing ...")
   return stat_values, stat_values_array, stat_plot_name

def get_lead_avg_file(stat, input_filename, fcst_lead, output_base_dir):
   lead_avg_filename = stat + '_' + os.path.basename(input_filename) \
      .replace('_dump_row.stat', '')
   # if fcst_leadX is in filename, replace it with fcst_lead_avgs
   # and add .txt to end of filename
   if f'fcst_lead{fcst_lead}' in lead_avg_filename:
      lead_avg_filename = (
         lead_avg_filename.replace(f'fcst_lead{fcst_lead}',
                                    'fcst_lead_avgs')
      )
      lead_avg_filename += '.txt'

   # if not, remove mention of forecast lead and
   # add fcst_lead_avgs.txt to end of filename
   elif 'fcst_lead_avgs' not in input_filename:
      lead_avg_filename = lead_avg_filename.replace(f'fcst_lead{fcst_lead}',
                                                     '')
      lead_avg_filename += '_fcst_lead_avgs.txt'
   lead_avg_file = os.path.join(output_base_dir, 'data',
                                lead_avg_filename)
   return lead_avg_file

def get_ci_file(stat, input_filename, fcst_lead, output_base_dir, ci_method):
   CI_filename = stat + '_' + os.path.basename(input_filename) \
      .replace('_dump_row.stat', '')
   # if fcst_leadX is in filename, replace it with fcst_lead_avgs
   # and add .txt to end of filename
   if f'fcst_lead{fcst_lead}' in CI_filename:
      CI_filename = CI_filename.replace(f'fcst_lead{fcst_lead}',
                                         'fcst_lead_avgs')

   # if not and fcst_lead_avgs isn't already in filename,
   # remove mention of forecast lead and
   # add fcst_lead_avgs.txt to end of filename
   elif 'fcst_lead_avgs' not in CI_filename:
      CI_filename = CI_filename.replace(f'fcst_lead{fcst_lead}',
                                      '')
      CI_filename += '_fcst_lead_avgs'
   CI_filename += '_CI_' + ci_method + '.txt'
   CI_file = os.path.join(output_base_dir, 'data',
                          CI_filename)
   return CI_file          

def equalize_samples(logger, df, group_by):
    # columns that will be used to drop duplicate rows across model groups
    cols_to_check = [
        key for key in [
            'LEAD_HOURS', 'VALID', 'INIT', 'FCST_THRESH_SYMBOL', 
            'FCST_THRESH_VALUE', 'OBS_LEV']
        if key in df.keys()
    ]
    df_groups = df.groupby(group_by)
    indexes = []
    # List all of the independent variables that are found in the data
    unique_indep_vars = np.unique(np.array(list(df_groups.groups.keys())).T[1])
    for unique_indep_var in unique_indep_vars:
        # Get all groups, in the form of DataFrames, that include the given 
        # independent variable
        dfs = [
            df_groups.get_group(name)[cols_to_check]
            for name in list(df_groups.groups.keys()) 
            if str(name[1]) == str(unique_indep_var)
        ]
        # merge all of these DataFrames together according to 
        # the columns in cols_to_check
        for i, dfs_i in enumerate(dfs):
            if i == 0:
                df_merged = dfs_i
            else:
                df_merged = df_merged.merge(
                    dfs_i, how='inner', indicator=False
                )
        # make sure to remove duplicate rows (looking only at the columns in 
        # cols_to_check) to reduce comp time in the next in the next step
        match_these = df_merged.drop_duplicates()
        # Get all the indices for rows in each group that match the merged df
        for dfs_i in dfs:
            for idx, row in dfs_i.iterrows():
                if (
                        row.to_numpy()[1:].tolist() 
                        in match_these.to_numpy()[:,1:].tolist()):
                    indexes.append(idx)
    # Select the matched rows by index among the rows in the original DataFrame
    df_equalized = df.loc[indexes]
    # Remove duplicates again, this time among both the columns 
    # in cols_to_check and the 'MODEL' column, which avoids, say, models with
    # repeated data from multiple entities
    df_equalized = df_equalized.loc[
        df_equalized[cols_to_check+['MODEL']].drop_duplicates().index
    ]
    # Regroup the data and move forward with this groups!
    df_equalized_groups = df_equalized.groupby(group_by)
    # Check that groups are indeed equally sized for each independent variable
    df_groups_sizes = df_equalized_groups.size()
    df_groups_sizes.index = df_groups_sizes.index.set_levels(
        df_groups_sizes.index.levels[-1].astype(str), level=-1
    )
    data_are_equalized = np.all([
        np.unique(df_groups_sizes.xs(str(unique_indep_var), level=1)).size == 1
        for unique_indep_var 
        in np.unique(np.array(list(df_groups_sizes.keys())).T[1])
    ])
    if data_are_equalized:
        logger.info(
            "Data were successfully equalized along the independent"
            + " variable."
        )
        return df_equalized, data_are_equalized
    else:
        logger.warning(
            "Data equalization along the independent variable failed."
        )
        logger.warning(
            "This may be a bug in the verif_plotting code. Please contact"
            + " the verif_plotting code manager about your issue."
        )
        logger.warning(
            "Skipping equalization.  Sample sizes will not be plotted."
        )
        return df, data_are_equalized

def get_name_for_listed_items(listed_items, joinchars, prechars, postchars, prechars_last, postchars_last):
    new_items = []
    if len(listed_items) == 1:
        return f"{prechars}{listed_items[0]}{postchars}"
    elif len(listed_items) == 2:
        return (f"{prechars}{listed_items[0]}{postchars} {prechars_last}"
                + f"{prechars}{listed_items[1]}{postchars}{postchars_last}")
    else:
        for i, item in enumerate(listed_items):
            if i == 0:
                start = item
            elif i == (len(listed_items)-1):
                if int(item) == int(listed_items[i-1]):
                    new_items.append(f"{prechars_last}{prechars}{start}{postchars}{postchars_last}")
                elif int(item) != int(listed_items[i-1])+1:
                    if int(start) != int(listed_items[i-1]):
                        new_items.append(f"{prechars}{start}-{listed_items[i-1]}{postchars}")
                        new_items.append(f"{prechars_last}{prechars}{item}{postchars}{postchars_last}")
                    else:
                        new_items.append(f"{prechars}{listed_items[i-1]}{postchars}")
                        new_items.append(f"{prechars_last}{prechars}{item}{postchars}{postchars_last}")
                elif int(start) == int(listed_items[0]):
                    new_items.append(f"{prechars}{start}-{item}{postchars}")
                else:
                    new_items.append(f"{prechars_last}{prechars}{start}-{item}{postchars}{postchars_last}")
            elif int(item) != int(listed_items[i-1])+1:
                if int(start) == int(listed_items[i-1]):
                    new_items.append(f"{prechars}{start}{postchars}")
                else:
                    new_items.append(
                        f"{prechars}{start}-{listed_items[i-1]}{postchars}"
                    )
                start=item
    return joinchars.join(new_items)

