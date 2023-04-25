'''
Program Name: set_init_valid_fhr_subseasonal_stats_info.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/.
          This sets up the necessary environment variables
          for valid dates and times information, initialization
          dates and times information, and forecast hour
          information. This is written to a file and sourced
          by the scripts.
'''

import os
import numpy as np

print("BEGIN: "+os.path.basename(__file__))

def get_hr_list_info(hr_list):
    """! This gets the beginning hour, end hour, and
         increment for cycle or valid hour list

         Args:
             hr_list - list of strings of hours

         Returns:
             hr_beg - two digit string of the first hour
             hr_end - two digit string of the end hour
             hr_inc - string of the increment of the
                       hours in the list in seconds
    """
    hr_beg = (hr_list[0]).zfill(2)
    hr_end = (hr_list[-1]).zfill(2)
    hr_inc = str(int((24/len(hr_list))*3600))
    return hr_beg, hr_end, hr_inc

def get_forecast_hours(fcyc_list, vhr_list, fhr_min_str, fhr_max_str):
    """! This creates a list of forecast hours to be
         considered

         Args:
             fcyc_list   - list of strings of cycle hours
             vhr_list    - list of strings of valid hours
             fhr_min_str - string of the first forecast hour
             fhr_max_str - string of the last forecast hour

         Returns:
             fhr_list - string of all forecast hours
                        to be considered in the verification
    """
    fhr_min = float(fhr_min_str)
    fhr_max = float(fhr_max_str)
    nfcyc = len(fcyc_list)
    nvhr = len(vhr_list)
    if nfcyc > nvhr:
        fhr_intvl = int(24/nfcyc)
    else:
        fhr_intvl = int(24/nvhr)
    nfhr = fhr_max/fhr_intvl
    fhr_max = int(nfhr*fhr_intvl)
    fhr_list = []
    fhr = fhr_min
    while fhr <= fhr_max:
        fhr_list.append(str(int(fhr)))
        fhr+=fhr_intvl
    fhr_list_str = ', '.join(fhr_list)
    return fhr_list_str

# Get environment variables
RUN = os.environ['RUN']
VERIF_CASE_STEP = os.environ['VERIF_CASE_STEP']
VCS = os.environ['VERIF_CASE_STEP']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VCS_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VCS_type_list = os.environ[VERIF_CASE_STEP_abbrev+'_type_list'].split(' ')

# Build dictionary
env_var_dict = {}
if VCS in ['grid2grid_stats', 'grid2obs_stats']:
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        # Process forecast initialization cycles
        VCS_abbrev_type_fcyc_list = (
            os.environ[VCS_abbrev_type+'_fcyc_list'].split(' ')
        )
        (VCS_abbrev_type_fcyc_beg,
         VCS_abbrev_type_fcyc_end,
         VCS_abbrev_type_fcyc_inc) = \
            get_hr_list_info(VCS_abbrev_type_fcyc_list)
        env_var_dict[VCS_abbrev_type+'_fcyc_list'] = (
            os.environ[VCS_abbrev_type+'_fcyc_list']
        )
        env_var_dict[VCS_abbrev_type+'_init_hr_list'] = ', '.join(
            VCS_abbrev_type_fcyc_list
        )
        env_var_dict[VCS_abbrev_type+'_init_hr_beg'] = VCS_abbrev_type_fcyc_beg
        env_var_dict[VCS_abbrev_type+'_init_hr_end'] = VCS_abbrev_type_fcyc_end
        env_var_dict[VCS_abbrev_type+'_init_hr_inc'] = VCS_abbrev_type_fcyc_inc
        # Process valid hours
        # note: precip requires special processing
        if 'precip' in VCS:
            if VCS_type == 'ccpa_accum24hr':
                VCS_abbrev_type_vhr_list = [ '12' ]
                VCS_abbrev_type_obs_daily_file = 'True'
        else:
            VCS_abbrev_type_vhr_list = (
                os.environ[VCS_abbrev_type+'_vhr_list'].split(' ')
            )
        (VCS_abbrev_type_vhr_beg,
         VCS_abbrev_type_vhr_end,
         VCS_abbrev_type_vhr_inc) = get_hr_list_info(VCS_abbrev_type_vhr_list)
        env_var_dict[VCS_abbrev_type+'_vhr_list'] = ' '.join(
            VCS_abbrev_type_vhr_list
        )
        env_var_dict[VCS_abbrev_type+'_valid_hr_list'] = ', '.join(
            VCS_abbrev_type_vhr_list
        )
        env_var_dict[VCS_abbrev_type+'_valid_hr_beg'] = VCS_abbrev_type_vhr_beg
        env_var_dict[VCS_abbrev_type+'_valid_hr_end'] = VCS_abbrev_type_vhr_end
        env_var_dict[VCS_abbrev_type+'_valid_hr_inc'] = VCS_abbrev_type_vhr_inc
        if VCS == 'precip_stats':
            env_var_dict[VCS_abbrev_type+'_obs_daily_file'] = (
                VCS_abbrev_type_obs_daily_file
            )
        # Process forecast hours
        # note: precip requires special processing
        VCS_abbrev_type_fhr_min = os.environ[VCS_abbrev_type+'_fhr_min']
        VCS_abbrev_type_fhr_max = os.environ[VCS_abbrev_type+'_fhr_max']
        if 'precip' in VCS:
            VCS_abbrev_type_accum_length = (
                VCS_type.split('accum')[1].replace('hr','')
            )
            if int(VCS_abbrev_type_fhr_min) \
                    < int(VCS_abbrev_type_accum_length):
                VCS_abbrev_type_fhr_min = VCS_abbrev_type_accum_length
            VCS_abbrev_type_fhr_min_vhr_fcyc_list = []
            for vhr in VCS_abbrev_type_vhr_list:
                for fcyc in VCS_abbrev_type_fcyc_list:
                    fhr_min_vhr_fcyc = (
                        int(VCS_abbrev_type_fhr_min)
                        + (int(vhr) - int(fcyc))
                    )
                    if fhr_min_vhr_fcyc < int(VCS_abbrev_type_accum_length):
                        fhr_min_vhr_fcyc+=int(VCS_abbrev_type_accum_length)
                    VCS_abbrev_type_fhr_min_vhr_fcyc_list.append(
                        fhr_min_vhr_fcyc
                    )
            VCS_abbrev_type_fhr_min = np.amin(
                np.array(VCS_abbrev_type_fhr_min_vhr_fcyc_list)
            )
        VCS_abbrev_type_fhr_list_str = get_forecast_hours(
            VCS_abbrev_type_fcyc_list, VCS_abbrev_type_vhr_list,
            VCS_abbrev_type_fhr_min, VCS_abbrev_type_fhr_max
        )
        env_var_dict[VCS_abbrev_type+'_fhr_list'] = (
            VCS_abbrev_type_fhr_list_str
        )
        env_var_dict[VCS_abbrev_type+'_fhr_beg'] = (
            VCS_abbrev_type_fhr_list_str.split(', ')[0]
        )
        env_var_dict[VCS_abbrev_type+'_fhr_end'] = (
            VCS_abbrev_type_fhr_list_str.split(', ')[-1]
        )

# Create file with environment variables to source
with open('python_gen_env_vars.sh', 'a') as file:
    file.write('#!/bin/sh\n')
    file.write('echo BEGIN: python_gen_env_vars.sh\n')
    for name, value in env_var_dict.items():
        file.write('export '+name+'='+'"'+value+'"\n')
    file.write('echo END: python_gen_env_vars.sh')

print("END: "+os.path.basename(__file__))
