#!/usr/bin/env python3
'''
Program Name: prune_stat_files.py
Contact(s): Marcel Caron, Mallory Row, and L. Gwen Chen (lichuan.chen@noaa.gov)
Abstract: This script is run by all scripts in the verif_plotting software.
          This prunes the MET stat files for the specific plotting job to help
          decrease wall time.
'''

import glob
import subprocess
import os
import re
import sys
import numpy as np
import shlex
from datetime import datetime, timedelta as td
SETTINGS_DIR = os.environ['USH_DIR']
sys.path.insert(0, os.path.abspath(SETTINGS_DIR))
import string_template_substitution

def daterange(start, end, td):
   curr = start
   while curr <= end:
      yield curr
      curr+=td

def expand_met_stat_files(met_stat_files, data_dir, output_base_template, RUN_case, 
                          RUN_type, line_type, vx_mask, var_name, model, 
                          obtype, eval_period, valid):
    met_stat_files_out = np.concatenate((
        met_stat_files, 
        glob.glob(os.path.join(
            # edit below to define stats archive path. Use '*' as wildcard.
            data_dir, 
            string_template_substitution.do_string_sub(
                output_base_template, 
                RUN_CASE=str(RUN_case), RUN_CASE_UPPER=str(RUN_case).upper(),
                RUN_CASE_LOWER=str(RUN_case).lower(), RUN_TYPE=str(RUN_type), 
                RUN_TYPE_UPPER=str(RUN_type).lower(), 
                RUN_TYPE_LOWER=str(RUN_type).lower(), LINE_TYPE=str(line_type),
                LINE_TYPE_UPPER=str(line_type).upper(), 
                LINE_TYPE_LOWER=str(line_type).lower(),
                VX_MASK=str(vx_mask), VX_MASK_UPPER=str(vx_mask).upper(),
                VX_MASK_LOWER=str(vx_mask).lower(), 
                VAR_NAME=str(var_name), VAR_NAME_UPPER=str(var_name).upper(),
                VAR_NAME_LOWER=str(var_name).lower(), MODEL=str(model), 
                MODEL_UPPER=str(model).upper(), MODEL_LOWER=str(model).lower(),
                OBTYPE=str(obtype), OBTYPE_UPPER=str(obtype).upper(),
                OBTYPE_LOWER=str(obtype).lower(), EVAL_PERIOD=str(eval_period),
                EVAL_PERIOD_UPPER=str(eval_period).upper(),
                EVAL_PERIOD_LOWER=str(eval_period).lower(),
                VALID=valid, valid=valid
            )
        ))
    ))
    return met_stat_files_out

def prune_data(data_dir, prune_dir, tmp_dir, output_base_template, valid_range, 
               eval_period, RUN_case, RUN_type, line_type, vx_mask, 
               fcst_var_names, var_name, model_list, obtype):

   print("BEGIN: "+os.path.basename(__file__))
   # Get list of models and loop through
   for model in model_list:
      # Get input and output data
      met_stat_files = []
      for valid in daterange(valid_range[0], valid_range[1], td(days=1)):
         met_stat_files = expand_met_stat_files(
            met_stat_files, data_dir, output_base_template, RUN_case, RUN_type, 
            line_type, vx_mask, var_name, model, obtype, eval_period, valid
         ) 
      pruned_data_dir = os.path.join(
         prune_dir, line_type+'_'+var_name+'_'+vx_mask+'_'+eval_period, tmp_dir
      )
      if not os.path.exists(pruned_data_dir):
         os.makedirs(pruned_data_dir)
      if len(met_stat_files) == 0:
         continue
      with open(met_stat_files[0]) as msf:
         met_header_cols = msf.readline()
      fcst_var_filter = ' '.join(
        '-e '+shlex.quote(fcst_var_name) for fcst_var_name in fcst_var_names
      )
      filter_cmd = (
         ' | grep -F '+shlex.quote(vx_mask)
         +' | grep -F '+shlex.quote(line_type)
      )
      log_msg = "Pruning "+data_dir+" files for model "+model+", vx_mask "
               +vx_mask+", variable "+'/'.join(fcst_var_names)+", line_type "+line_type
      if RUN_type == 'anom' and 'HGT' in var_name:
         filter_cmd += ' | grep -F '+shlex.quote(os.environ['INTERP'])
         log_msg += ", interp "+os.environ['INTERP']
      
      filter_cmd += ' | grep -F '+shlex.quote(model)
      # Prune the MET .stat files and write to new file
      met_stat_files_cmd = ' '.join(
         shlex.quote(str(met_stat_file)) for met_stat_file in met_stat_files
      )
      pruned_met_stat_file = os.path.join(
         pruned_data_dir, model+'.stat'
      )
      grep_cmd = (
         'grep -Fh '+fcst_var_filter+' '+met_stat_files_cmd+filter_cmd
      )
      with open(pruned_met_stat_file, 'w') as pmsf:
         pmsf.write(met_header_cols)
         subprocess.run(grep_cmd, shell=True, stdout=pmsf, encoding='UTF-8')
   print("END: "+os.path.basename(__file__))
