'''
Program Name: get_subseasonal_stat_files.py
Contact(s): Shannon Shields
Abstract: This script retrieves stat files for subseasonal plotting step.
'''

import os
import subprocess
import datetime
from time import sleep
import pandas as pd
import glob
import numpy as np

print("BEGIN: "+os.path.basename(__file__))

def get_time_info(start_date_str, end_date_str,
                  start_hr_str, end_hr_str, hr_inc_str,
                  fhr_list, date_type):
    """! This creates a list of dictionaries containing information
         on the valid dates and times, the initialization dates
         and times, and forecast hour pairings

         Args:
             start_date_str - string of the verification start
                              date
             end_date_str   - string of the verification end
                              date
             start_hr_str   - string of the verification start
                              hour
             end_hr_str     - string of the verification end
                              hour
             hr_inc_str     - string of the increment between
                              start_hr and end_hr
             fhr_list       - list of strings of the forecast
                              hours to verify
             date_type      - string defining by what type
                              date and times to create METplus
                              data

         Returns:
         time_info - list of dictionaries with the valid,
                     initalization, and forecast hour
                     pairings
    """
    sdate = datetime.datetime(int(start_date_str[0:4]),
                              int(start_date_str[4:6]),
                              int(start_date_str[6:]),
                              int(start_hr_str))
    edate = datetime.datetime(int(end_date_str[0:4]),
                              int(end_date_str[4:6]),
                              int(end_date_str[6:]),
                              int(end_hr_str))
    date_inc = datetime.timedelta(seconds=int(hr_inc_str))
    time_info = []
    date = sdate
    while date <= edate:
        if date_type == 'VALID':
            valid_time = date
        elif date_type == 'INIT':
            init_time = date
        for fhr in fhr_list:
            if fhr == 'anl':
                lead = '0'
            else:
                lead = fhr
            if date_type == 'VALID':
                init_time = valid_time - datetime.timedelta(hours=int(lead))
            elif date_type == 'INIT':
                valid_time = init_time + datetime.timedelta(hours=int(lead))
            t = {}
            t['valid_time'] = valid_time
            t['init_time'] = init_time
            t['lead'] = lead
            time_info.append(t)
        date = date + date_inc
    return time_info

def get_model_stat_file(valid_time_dt, init_time_dt, lead_str,
                        name, stat_data_dir, gather_by, VCS_dir_name,
                        VCS_sub_dir_name, link_data_dir):
    """! This links a model .stat file from its archive.

         Args:
             valid_time_dt    - datetime object of the valid time
             init_time_dt     - datetime object of the
                                initialization time
             lead_str         - string of the forecast lead
             name             - string of the model name
             stat_data_dir    - string of the online archive
                                for model MET .stat files
             gather_by        - string of the file format the
                                files are saved as in the data_dir
             VCS_dir_name     - string of VCS directory name
                                in 'metplus_data' archive
             VCS_sub_dir_name - string of VCS sub-directory name
                                (under VCS_dir_name)
                                in 'metplus_data' archive
             link_data_dir    - string of the directory to link
                                model data to

         Returns:
    """
    model_stat_gather_by_VCS_dir = os.path.join(stat_data_dir,
                                                'subseasonal', name+'.'
                                                +valid_time.strftime('%Y%m%d%H')
                                                )

    if gather_by == 'VALID':
         model_stat_file = os.path.join(model_stat_gather_by_VCS_dir,
                                        name+'_atmos_'+VCS_dir_name+'_v'
                                        +valid_time.strftime('%Y%m%d%H')
                                        +'.stat')
         link_model_stat_file = os.path.join(link_data_dir,
                                             name+'_atmos_'+VCS_dir_name+'_v'
                                             +valid_time.strftime('%Y%m%d')
                                             +'.stat')
    elif gather_by == 'INIT':
         model_stat_file = os.path.join(model_stat_gather_by_VCS_dir,
                                        name+'_atmos_'+VCS_dir_name+'_'
                                        +init_time.strftime('%Y%m%d%H')
                                        +'.stat')
         link_model_stat_file = os.path.join(link_data_dir,
                                             name+'_atmos_'+VCS_dir_name+'_'
                                             +init_time.strftime('%Y%m%d')
                                             +'.stat')
    elif gather_by == 'VSDB':
         if VCS_dir_name in ['grid2grid']:
             model_stat_file = os.path.join(model_stat_gather_by_VCS_dir,
                                            valid_time.strftime('%H')+'Z',
                                            name, name+'_'
                                            +valid_time.strftime('%Y%m%d')
                                            +'.stat')
             link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                                 +valid_time.strftime('%Y%m%d')
                                                 +'_valid'
                                                 +valid_time.strftime('%H')
                                                 +'.stat')
         elif VCS_dir_name in ['grid2obs', 'precip']:
             model_stat_file = os.path.join(model_stat_gather_by_VCS_dir,
                                            init_time.strftime('%H')+'Z',
                                            name, name+'_'
                                            +valid_time.strftime('%Y%m%d')
                                            +'.stat')
             link_model_stat_file = os.path.join(link_data_dir, name+'_valid'
                                                 +valid_time.strftime('%Y%m%d')
                                                 +'_init'
                                                 +init_time.strftime('%H')
                                                 +'.stat')
    if not os.path.exists(link_model_stat_file):
        if os.path.exists(model_stat_file):
            os.system('ln -sf '+model_stat_file+' '+link_model_stat_file)
        else:
            print("WARNING: "+model_stat_file+" does not exist")

# Read in common environment variables
RUN = os.environ['RUN']
model_list = os.environ['model_list'].split(' ')
model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
machine = os.environ['machine']
VERIF_CASE_STEP = os.environ['VERIF_CASE_STEP']
VCS = os.environ['VERIF_CASE_STEP']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VCS_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
if VCS != 'tropcyc':
    VCS_type_list = os.environ[VERIF_CASE_STEP_abbrev+'_type_list'].split(' ')

# Set some common variables
cwd = os.getcwd()

if VERIF_CASE_STEP == 'grid2grid_plots':
  # Read in VERIF_CASE_STEP related environment variables
  # Get stat files for each option in VCS_type_list
  for VCS_type in VCS_type_list:
      VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
      # Read in VCS_type environment variables
      VCS_abbrev_type_fcyc_list = os.environ[
          VCS_abbrev_type+'_fcyc_list'
      ].split(' ')
      VCS_abbrev_type_vhr_list = os.environ[
          VCS_abbrev_type+'_vhr_list'
      ].split(' ')
      VCS_abbrev_type_start_hr = os.environ[
          VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
      ]
      VCS_abbrev_type_end_hr = os.environ[
          VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
      ]
      VCS_abbrev_type_hr_inc = os.environ[
          VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
      ]
      VCS_abbrev_type_fhr_list = os.environ[
          VCS_abbrev_type+'_fhr_list'
      ].split(', ')
      VCS_abbrev_type_gather_by_list = os.environ[
          VCS_abbrev_type+'_gather_by_list'
      ].split(' ')
      # Get date and time information for VCS_type
      VCS_abbrev_type_time_info_dict = get_time_info(
          start_date, end_date, VCS_abbrev_type_start_hr,
          VCS_abbrev_type_end_hr, VCS_abbrev_type_hr_inc,
          VCS_abbrev_type_fhr_list, plot_by
      )
      # Get model stat files
      for model in model_list:
          model_idx = model_list.index(model)
          model_stat_dir = model_stat_dir_list[model_idx]
          model_VCS_abbrev_type_gather_by = (
              VCS_abbrev_type_gather_by_list[model_idx]
          )
          link_model_VCS_type_dir = os.path.join(cwd, 'data',
                                                 model, VCS_type)
          if not os.path.exists(link_model_VCS_type_dir):
              os.makedirs(link_model_VCS_type_dir)
          for time in VCS_abbrev_type_time_info_dict:
              valid_time = time['valid_time']
              init_time = time['init_time']
              lead = time['lead']
              if init_time.strftime('%H') not in VCS_abbrev_type_fcyc_list:
                  continue
              elif valid_time.strftime('%H') not in VCS_abbrev_type_vhr_list:
                  continue
              else:
                  get_model_stat_file(valid_time, init_time, lead,
                                      model, model_stat_dir,
                                      model_VCS_abbrev_type_gather_by,
                                      'grid2grid', VCS_type,
                                      link_model_VCS_type_dir)
elif VCS == 'grid2obs_plots':
    # Read in VERIF_CASE_STEP related environment variables
    # Get stat files for each option in VCS_type_list
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        # Read in VCS_type environment variables
        VCS_abbrev_type_fcyc_list = os.environ[
            VCS_abbrev_type+'_fcyc_list'
        ].split(' ')
        VCS_abbrev_type_vhr_list = os.environ[
            VCS_abbrev_type+'_vhr_list'
        ].split(' ')
        VCS_abbrev_type_start_hr = os.environ[
            VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        VCS_abbrev_type_end_hr = os.environ[
            VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        VCS_abbrev_type_hr_inc = os.environ[
            VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        VCS_abbrev_type_fhr_list = os.environ[
            VCS_abbrev_type+'_fhr_list'
        ].split(', ')
        VCS_abbrev_type_gather_by_list = os.environ[
            VCS_abbrev_type+'_gather_by_list'
        ].split(' ')
        # Get date and time information for VCS_type
        VCS_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, VCS_abbrev_type_start_hr,
            VCS_abbrev_type_end_hr, VCS_abbrev_type_hr_inc,
            VCS_abbrev_type_fhr_list, plot_by
        )
        # Get model stat files
        for model in model_list:
            model_idx = model_list.index(model)
            model_stat_dir = model_stat_dir_list[model_idx]
            model_VCS_abbrev_type_gather_by = (
                VCS_abbrev_type_gather_by_list[model_idx]
            )
            link_model_VCS_type_dir = os.path.join(cwd, 'data',
                                                   model, VCS_type)
            if not os.path.exists(link_model_VCS_type_dir):
                os.makedirs(link_model_VCS_type_dir)
            for time in VCS_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in VCS_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in VCS_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_VCS_abbrev_type_gather_by,
                                        'grid2obs', VCS_type,
                                        link_model_VCS_type_dir)
elif VERIF_CASE_STEP == 'precip_plots':
    # Read in VERIF_CASE_STEP related environment variables
    # Get stat files for each option in VCS_type_list
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        # Read in VCS_type environment variables
        VCS_abbrev_type_fcyc_list = os.environ[
            VCS_abbrev_type+'_fcyc_list'
        ].split(' ')
        VCS_abbrev_type_vhr_list = os.environ[
            VCS_abbrev_type+'_vhr_list'
        ].split(' ')
        VCS_abbrev_type_start_hr = os.environ[
            VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_beg'
        ]
        VCS_abbrev_type_end_hr = os.environ[
            VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_end'
        ]
        VCS_abbrev_type_hr_inc = os.environ[
            VCS_abbrev_type+'_'+make_met_data_by.lower()+'_hr_inc'
        ]
        VCS_abbrev_type_fhr_list = os.environ[
            VCS_abbrev_type+'_fhr_list'
        ].split(', ')
        VCS_abbrev_type_gather_by_list = os.environ[
            VCS_abbrev_type+'_gather_by_list'
        ].split(' ')
        # Get date and time information for VCS_type
        VCS_abbrev_type_time_info_dict = get_time_info(
            start_date, end_date, VCS_abbrev_type_start_hr,
            VCS_abbrev_type_end_hr, VCS_abbrev_type_hr_inc,
            VCS_abbrev_type_fhr_list, plot_by
        )
        # Get model stat files
        for model in model_list:
            model_idx = model_list.index(model)
            model_stat_dir = model_stat_dir_list[model_idx]
            model_VCS_abbrev_type_gather_by = (
                VCS_abbrev_type_gather_by_list[model_idx]
            )
            link_model_VCS_type_dir = os.path.join(cwd, 'data',
                                                   model, VCS_type)
            if not os.path.exists(link_model_VCS_type_dir):
                os.makedirs(link_model_VCS_type_dir)
            for time in VCS_abbrev_type_time_info_dict:
                valid_time = time['valid_time']
                init_time = time['init_time']
                lead = time['lead']
                if init_time.strftime('%H') not in VCS_abbrev_type_fcyc_list:
                    continue
                elif valid_time.strftime('%H') not in VCS_abbrev_type_vhr_list:
                    continue
                else:
                    get_model_stat_file(valid_time, init_time, lead,
                                        model, model_stat_dir,
                                        model_VCS_abbrev_type_gather_by,
                                        'precip', VCS_type,
                                        link_model_VCS_type_dir)

print("END: "+os.path.basename(__file__))



