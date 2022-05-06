'''
Program Name: global_det_atmos_check_settings.py
Contact(s): Mallory Row
Abstract: This script is run by all scripts in scripts/.
          This does a check on the user's settings.
'''

import sys
import os
import datetime
import calendar

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables to use
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP
# Set up setting names
evs_global_det_atmos_settings_dict = {
    'evs': ['HOMEevs', 'config', 'NET', 'RUN', 'COMPONENT', 'STEP',
            'VERIF_CASE', 'envir', 'evs_run_mode', 'job', 'jobid',
            'pid', 'OUTPUTROOT', 'DATA', 'machine', 'ACCOUNT',
            'QUEUE', 'QUEUESHARED', 'QUEUESERV', 'PARTITION_BATCH', 'nproc',
            'USE_CFP', 'MET_bin_exec', 'evs_ver', 'ccpa_ver', 'obsproc_ver',
            'PARMevs', 'USHevs', 'EXECevs', 'FIXevs', 'DATAROOT', 'COMROOT',
            'era_interim_climo_files', 'DCOMROOT_PROD', 'COMROOT_PROD',
            'VERIF_CASE_STEP_abbrev'],
    'shared': ['model_list', 'model_stat_dir_list', 'model_file_format_list',
               'OUTPUTROOT', 'start_date', 'end_date', 'metplus_verbosity',
               'met_verbosity','log_met_output_to_metplus', 'KEEPDATA',
               'SENDCOM'],
    'modules': ['MET_ROOT', 'METPLUS_PATH'],
    'RUN_GRID2GRID_STATS': ['g2gs_type_list', 'g2gs_pres_levs_truth_name_list',
                            'g2gs_pres_levs_truth_format_list',
                            'g2gs_pres_levs_cycle_list',
                            'g2gs_pres_levs_valid_hr_list',
                            'g2gs_pres_levs_fhr_min', 'g2gs_pres_levs_fhr_max',
                            'g2gs_pres_levs_fhr_inc',
                            'g2gs_precip_file_format_list',
                            'g2gs_precip_file_accum_list',
                            'g2gs_precip_cycle_list',
                            'g2gs_precip_fhr_min', 'g2gs_precip_fhr_max',
                            'g2gs_precip_fhr_inc',
                            'g2gs_snow_cycle_list',
                            'g2gs_snow_fhr_min', 'g2gs_snow_fhr_max',
                            'g2gs_snow_fhr_inc',
                            'g2gs_sst_cycle_list',
                            'g2gs_sst_fhr_min', 'g2gs_sst_fhr_max',
                            'g2gs_sst_fhr_inc',
                            'g2gs_sea_ice_cycle_list',
                            'g2gs_sea_ice_fhr_min', 'g2gs_sea_ice_fhr_max',
                            'g2gs_sea_ice_fhr_inc',
                            'g2gs_ozone_cycle_list',
                            'g2gs_ozone_fhr_min', 'g2gs_ozone_fhr_max',
                            'g2gs_ozone_fhr_inc',
                            'g2gs_means_cycle_list',
                            'g2gs_means_valid_hr_list',
                            'g2gs_means_fhr_min', 'g2gs_means_fhr_max'],
    'RUN_GRID2OBS_STATS': ['g2os_type_list', 'g2os_pres_levs_cycle_list',
                           'g2os_pres_levs_valid_hr_list',
                           'g2os_pres_levs_fhr_min', 'g2os_pres_levs_fhr_max',
                           'g2os_pres_levs_fhr_inc',
                           'g2os_sfc_cycle_list',
                           'g2os_sfc_valid_hr_list',
                           'g2os_sfc_fhr_min', 'g2os_sfc_fhr_max',
                           'g2os_sfc_fhr_inc',
                           'g2os_flux_cycle_list',
                           'g2os_flux_fhr_min', 'g2os_flux_fhr_max',
                           'g2os_flux_fhr_inc',
                           'g2os_sea_ice_cycle_list',
                           'g2os_sea_ice_fhr_min', 'g2os_sea_ice_fhr_max',
                           'g2os_sea_ice_fhr_inc',]
}

# Select dictionary to check
env_check_group_list = ['evs', 'shared', 'modules',
                        'RUN_'+VERIF_CASE.upper()+'_'+STEP.upper()]
for env_check_group in env_check_group_list:
    env_var_check_list = (
        evs_global_det_atmos_settings_dict[env_check_group]
    )
    for env_var_check in env_var_check_list:
        if not env_var_check in os.environ:
            if env_check_group == 'modules':
                print("ERROR: "+env_var_check+" not set in environment, "
                      +"review modules loaded in "
                      +"global_det_atmos_load_modules.sh")
            elif env_check_group == 'evs':
                print("ERROR: "+env_var_check+" was not set in environment, "
                      +"was not set through previous EVS scripts")
            else:
                print("ERROR: "+env_var_check+" not set in environment, "
                      +"review modules loaded in "
                      +"global_det_atmos_load_modules.sh")
            sys.exit(1)

# Do date check
date_check_name_list = ['start', 'end']
for date_check_name in date_check_name_list:
    date_check = os.environ[date_check_name+'_date']
    date_check_year = int(date_check[0:4])
    date_check_month = int(date_check[4:6])
    date_check_day = int(date_check[6:])
    if len(date_check) != 8:
        print("ERROR: "+date_check_name+"_date not in YYYYMMDD format")
        sys.exit(1)
    if date_check_month > 12 or int(date_check_month) == 0:
        print("ERROR: month "+str(date_check_month)+" in value "
              +date_check+" for "+date_check_name+"_date is not a valid month")
        sys.exit(1)
    if date_check_day \
            > calendar.monthrange(date_check_year, date_check_month)[1]:
        print("ERROR: day "+str(date_check_day)+" in value "
              +date_check+" for "+date_check_name+"_date is not a valid day "
              +"for month")
        sys.exit(1)
if datetime.datetime.strptime(os.environ['end_date'], '%Y%m%d') \
        < datetime.datetime.strptime(os.environ['start_date'], '%Y%m%d'):
    print("ERROR: end_date ("+os.environ['end_date']+") cannot be less than "
          +"start_date ("+os.environ['start_date']+")")
    sys.exit(1)

# Do check for valid config options
VERIF_CASE_STEP_type_list = (
    os.environ[VERIF_CASE_STEP_abbrev+'_type_list'].split(' ')
)
valid_VERIF_CASE_STEP_type_opts_dict = {
    'grid2grid_stats': ['pres_levs', 'precip', 'snow', 'sst', 'sea_ice',
                        'ozone', 'means'],
    'grid2obs_stats': ['pres_levs', 'sfc', 'flux', 'sea_ice']
}
for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
    if VERIF_CASE_STEP_type \
            not in valid_VERIF_CASE_STEP_type_opts_dict[VERIF_CASE_STEP]:
        print("ERROR: "+VERIF_CASE_STEP_type+" not a valid option for "
              +VERIF_CASE_STEP_abbrev+"_type_list. Valid options are "
              +','.join(valid_VERIF_CASE_STEP_type_opts_dict[VERIF_CASE_STEP]))
        sys.exit(1)

# Do check for list variables lengths
check_config_var_len_list = ['model_stat_dir_list', 'model_file_format_list']
if VERIF_CASE_STEP == 'grid2grid_stats':
    check_config_var_len_list.append(VERIF_CASE_STEP_abbrev
                                    +'_pres_levs_truth_name_list')
    check_config_var_len_list.append(VERIF_CASE_STEP_abbrev
                                    +'_pres_levs_truth_format_list')
    check_config_var_len_list.append(VERIF_CASE_STEP_abbrev
                                    +'_precip_file_format_list')
    check_config_var_len_list.append(VERIF_CASE_STEP_abbrev
                                    +'_precip_file_accum_list')
for config_var in check_config_var_len_list:
    if len(os.environ[config_var].split(' ')) \
            != len(os.environ['model_list'].split(' ')):
     print("ERROR: length of "+config_var+" (length="
           +str(len(os.environ[config_var].split(' ')))+", values="
           +os.environ[config_var]+") not equal to length of model_list "
           +"(length="+str(len(os.environ['model_list'].split(' ')))+", "
           +"values="+os.environ['model_list']+")")
     sys.exit(1)

# Set valid list of options settings
valid_config_var_values_dict = {
    'metplus_verbosity': ['DEBUG', 'INFO', 'WARN', 'ERORR'],
    'met_verbosity': ['0', '1', '2', '3', '4', '5'],
    'log_met_output_to_metplus': ['yes', 'no'],
    'KEEPDATA': ['YES', 'NO'],
    'SENDCOM': ['YES', 'NO'],
}

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
        print("ERROR: value of "+failed_config_value+" for "
              +config_var+" not a valid option. Valid options are "
              +', '.join(valid_config_var_values_dict[config_var]))
        sys.exit(1)

print("END: "+os.path.basename(__file__))
