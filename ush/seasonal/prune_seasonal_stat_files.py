'''
Program Name: prune_seasonal_stat_files.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/.
          This prunes the MET .stat files for the
          specific plotting job to help decrease
          wall time.
'''

import glob
import subprocess
import os
import re

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
RUN_type = os.environ['RUN_type']
line_type = os.environ['line_type']
fcst_var_name = os.environ['fcst_var_name']
vx_mask = os.environ['vx_mask']
var_name = os.environ['var_name']

# Get list of models and loop through
env_var_model_list = []
regex = re.compile(r'model(\d+)$')
for key in os.environ.keys():
    result = regex.match(key)
    if result is not None:
        env_var_model_list.append(result.group(0))
for env_var_model in env_var_model_list:
    model = os.environ[env_var_model]
    # Get input and output data
    data_dir = os.path.join(DATA, 'stats', 'seasonal', 
                            'atmos.{valid?fmt=%Y%m%d%H}', model, RUN)
    met_stat_files = glob.glob(os.path.join(data_dir, model+'_*'))
    pruned_data_dir = os.path.join(
        DATA, 'stats', 'seasonal',
        'atmos.{valid?fmt=%Y%m%d%H}', model, RUN,
        line_type+'_'+var_name+'_'+vx_mask
    )
    if not os.path.exists(pruned_data_dir):
       os.makedirs(pruned_data_dir)
    with open(met_stat_files[0]) as msf:
        met_header_cols = msf.readline()
    all_grep_output = ''
    if RUN_type == 'anom' and 'HGT' in var_name:
        print("Pruning "+data_dir+" files for vx_mask "+vx_mask+", variable "
              +fcst_var_name+", line_type "+line_type+", interp "
              +os.environ['interp'])
        filter_cmd = (
            ' | grep "'+vx_mask
            +'" | grep "'+fcst_var_name
            +'" | grep "'+line_type
            +'" | grep "'+os.environ['interp']+'"'
        )
    else:
        print("Pruning "+data_dir+" files for vx_mask "+vx_mask+", variable "
              +fcst_var_name+", line_type "+line_type)
        filter_cmd = (
            ' | grep "'+vx_mask
            +'" | grep "'+fcst_var_name
            +'" | grep "'+line_type+'"'
        )
    # Prune the MET .stat files and write to new file
    for met_stat_file in met_stat_files:
        ps = subprocess.Popen('grep -R "'+model+'" '+met_stat_file+filter_cmd,
                              shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, encoding='UTF-8')
        grep_output = ps.communicate()[0]
        all_grep_output = all_grep_output+grep_output
    pruned_met_stat_file = os.path.join(pruned_data_dir,
                                        model+'.stat')
    with open(pruned_met_stat_file, 'w') as pmsf:
        pmsf.write(met_header_cols+all_grep_output)

print("END: "+os.path.basename(__file__))
