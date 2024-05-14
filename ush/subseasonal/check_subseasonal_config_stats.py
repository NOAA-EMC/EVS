#!/usr/bin/env python3
'''
Program Name: check_subseasonal_config_stats.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/stats/subseasonal.
          This does a check on the user's settings in
          the passed config file.
'''

import sys
import os
import datetime
import calendar

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
RUN = os.environ['RUN']
VERIF_CASE_STEP = os.environ['VERIF_CASE_STEP']
VCS = os.environ['VERIF_CASE_STEP']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VCS_abbrev = os.environ['VERIF_CASE_STEP_abbrev']

# Do check for all environment variables needed by config
VCS_type_env_vars_dict = {
    'shared': ['model_list',
               'model_stats_dir_list',
               'model_file_format_list',
               'OUTPUTROOT',
               'start_date', 'end_date', 'make_met_data_by',
               'met_version', 'metplus_version'],
    'grid2grid_stats': ['g2gstats_type_list',
                        'g2gstats_temp_truth_name_list',
                        'g2gstats_temp_truth_file_format_list',
                        'g2gstats_temp_inithour_list', 
                        'g2gstats_temp_vhr_list',
                        'g2gstats_temp_fhr_min', 'g2gstats_temp_fhr_max',
                        'g2gstats_temp_fhr_inc',
                        'g2gstats_temp_grid', 'g2gstats_temp_gather_by',
                        'g2gstats_pres_lvls_truth_name_list',
                        'g2gstats_pres_lvls_truth_file_format_list',
                        'g2gstats_pres_lvls_inithour_list', 
                        'g2gstats_pres_lvls_vhr_list',
                        'g2gstats_pres_lvls_fhr_min', 
                        'g2gstats_pres_lvls_fhr_max',
                        'g2gstats_pres_lvls_fhr_inc',
                        'g2gstats_pres_lvls_grid', 
                        'g2gstats_pres_lvls_gather_by',
                        'g2gstats_sst_truth_name_list',
                        'g2gstats_sst_truth_file_format_list',
                        'g2gstats_sst_inithour_list',
                        'g2gstats_sst_vhr_list',
                        'g2gstats_sst_fhr_min', 'g2gstats_sst_fhr_max',
                        'g2gstats_sst_fhr_inc',
                        'g2gstats_sst_grid', 'g2gstats_sst_gather_by',
                        'g2gstats_seaice_truth_name_list',
                        'g2gstats_seaice_truth_file_format_list',
                        'g2gstats_seaice_inithour_list',
                        'g2gstats_seaice_vhr_list',
                        'g2gstats_seaice_fhr_min', 'g2gstats_seaice_fhr_max',
                        'g2gstats_seaice_fhr_inc',
                        'g2gstats_seaice_grid', 'g2gstats_seaice_gather_by'],
    'grid2obs_stats': ['g2ostats_type_list',
                       'g2ostats_prepbufr_truth_name_list',
                       'g2ostats_prepbufr_truth_file_format_list',
                       'g2ostats_prepbufr_inithour_list',
                       'g2ostats_prepbufr_vhr_list', 
                       'g2ostats_prepbufr_fhr_min',
                       'g2ostats_prepbufr_fhr_max', 
                       'g2ostats_prepbufr_fhr_inc',
                       'g2ostats_prepbufr_grid',
                       'g2ostats_prepbufr_gather_by']
}
VCS_type_env_check_list = ['shared', VERIF_CASE_STEP]
for VCS_type_env_check in VCS_type_env_check_list:
    VCS_type_env_var_check_list = VCS_type_env_vars_dict[VCS_type_env_check]
    for VCS_type_env_var_check in VCS_type_env_var_check_list:
        if not VCS_type_env_var_check in os.environ:
            print("FATAL ERROR: "+VCS_type_env_var_check+" not set in config "
                  +"under "+VCS_type_env_check+" settings")
            sys.exit(1)

VCS_type_list = os.environ[VERIF_CASE_STEP_abbrev+'_type_list'].split(' ')

# Do date check
date_check_name_list = ['start', 'end']
for date_check_name in date_check_name_list:
    date_check = os.environ[date_check_name+'_date']
    date_check_year = int(date_check[0:4])
    date_check_month = int(date_check[4:6])
    date_check_day = int(date_check[6:])
    if len(date_check) != 8:
        print("FATAL ERROR: "+date_check_name+"_date not in YYYYMMDD format")
        sys.exit(1)
    if date_check_month > 12 or int(date_check_month) == 0:
        print("FATAL ERROR: month "+str(date_check_month)+" in value "
              +date_check+" for "+date_check_name+"_date is not a valid month")
        sys.exit(1)
    if date_check_day \
            > calendar.monthrange(date_check_year, date_check_month)[1]:
        print("FATAL ERROR: day "+str(date_check_day)+" in value "
              +date_check+" for "+date_check_name+"_date is not a valid day "
              +"for month")
        sys.exit(1)
if datetime.datetime.strptime(os.environ['end_date'], '%Y%m%d') \
        < datetime.datetime.strptime(os.environ['start_date'], '%Y%m%d'):
    print("FATAL ERROR: end_date ("+os.environ['end_date']+") cannot be less "
          +"than start_date ("+os.environ['start_date']+")")
    sys.exit(1)

# Do check for valid config options
valid_VCS_type_opts_dict = {
    'grid2grid_stats': ['temp', 'pres_lvls', 'sst', 'seaice'],
    'grid2obs_stats': ['prepbufr']
}
for VCS_type in VCS_type_list:
    if VCS_type not in valid_VCS_type_opts_dict[VCS]:
        print("FATAL ERROR: "+VCS_type+" not a valid option for "
              +VCS_abbrev+"_type_list. Valid options are "
              +', '.join(valid_VCS_type_opts_dict[VCS]))
        sys.exit(1)

# Do check for list config variables lengths
check_config_var_len_list = ['model_stats_dir_list',
                             'model_file_format_list']
for config_var in check_config_var_len_list:
    if len(os.environ[config_var].split(' ')) \
            != len(os.environ['model_list'].split(' ')):
        print("FATAL ERROR: length of "+config_var+" (length="
              +str(len(os.environ[config_var].split(' ')))+", values="
              +os.environ[config_var]+") not equal to length of model_list "
              +"(length="+str(len(os.environ['model_list'].split(' ')))+", "
              +"values="+os.environ['model_list']+")")
        sys.exit(1)

# Do check for valid list config variable options
valid_config_var_values_dict = {
    'make_met_data_by': ['VALID', 'INIT']
}
if VERIF_CASE_STEP == 'grid2grid_stats':
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_truth_name_list'] = ['gfs_anl', 
                                                             'ecmwf_anl',
                                                             'umd_anl',
                                                             'ghrsst_anl',
                                                             'osi_anl']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 
                                                       'VSDB']
elif VERIF_CASE_STEP == 'grid2obs_stats':
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_truth_name_list'] = ['nam_anl']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 
                                                       'VSDB']

# Run through and check config variables from dictionary
for config_var in list(valid_config_var_values_dict.keys()):
    if 'list' in config_var:
        for list_item in os.environ[config_var].split(' '):
            if list_item not in valid_config_var_values_dict[config_var]:
                config_var_pass = False
                failed_config_value = list_item
                break
            else:
                config_var_pass = True
    else:
        if os.environ[config_var] \
                not in valid_config_var_values_dict[config_var]:
            config_var_pass = False
            failed_config_value = os.environ[config_var]
        else:
            config_var_pass = True
    if not config_var_pass:
        print("FATAL ERROR: value of "+failed_config_value+" for "
              +config_var+" not a valid option. Valid options are "
              +', '.join(valid_config_var_values_dict[config_var]))
        sys.exit(1)

print("END: "+os.path.basename(__file__))



