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
config = os.environ['config']
evs_run_mode = os.environ['evs_run_mode']

VERIF_CASE_STEP = VERIF_CASE+'_'+STEP

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
    'RUN_GRID2GRID_STATS': ['flux', 'means', 'ozone', 'precip_accum24hr',
                            'precip_accum3hr', 'pres_levs', 'sea_ice',
                            'snow', 'sst'],
    'RUN_GRID2GRID_PLOTS': ['flux', 'means', 'ozone', 'precip', 'pres_levs',
                            'sea_ice', 'snow', 'sst'],
    'RUN_GRID2OBS_STATS': ['pres_levs', 'ptype', 'sfc'],
    'RUN_GRID2OBS_PLOTS': ['pres_levs', 'ptype', 'sfc']
}
for VERIF_CASE_STEP_type in VERIF_CASE_STEP_type_list:
    if VERIF_CASE_STEP_type \
            not in valid_VERIF_CASE_STEP_type_opts_dict[
            'RUN_'+VERIF_CASE.upper()+'_'+STEP.upper()
            ]:
        print("ERROR: "+VERIF_CASE_STEP_type+" not a valid option for "
              +VERIF_CASE_STEP_abbrev+"_type_list. Valid options are "
              +','.join(valid_VERIF_CASE_STEP_type_opts_dict[
                  'RUN_'+VERIF_CASE.upper()+'_'+STEP.upper()
              ]))
        sys.exit(1)

# Set up setting names
evs_global_det_atmos_settings_dict = {}
if evs_run_mode == 'production':
    evs_global_det_atmos_settings_dict['evs'] = [
        'HOMEevs', 'config', 'NET', 'RUN', 'COMPONENT', 'STEP',
        'VERIF_CASE', 'envir', 'evs_run_mode', 'job', 'jobid',
        'pid', 'OUTPUTROOT', 'DATA', 'machine', 'nproc', 'USE_CFP',
        'evs_ver', 'ccpa_ver', 'obsproc_ver', 'PARMevs', 'USHevs',
        'EXECevs', 'FIXevs', 'DATAROOT', 'COMROOT', 'COMIN', 'COMOUT',
        'DCOMROOT', 'VERIF_CASE_STEP_abbrev'
    ]
else:
    evs_global_det_atmos_settings_dict['evs'] = [
        'HOMEevs', 'config', 'NET', 'RUN', 'COMPONENT', 'STEP',
        'VERIF_CASE', 'envir', 'evs_run_mode', 'job', 'jobid',
        'pid', 'OUTPUTROOT', 'DATA', 'machine', 'ACCOUNT',
        'QUEUE', 'QUEUESHARED', 'QUEUESERV', 'PARTITION_BATCH', 'nproc',
        'USE_CFP', 'MET_bin_exec', 'evs_ver', 'ccpa_ver', 'obsproc_ver',
        'PARMevs', 'USHevs', 'EXECevs', 'FIXevs', 'archive_obs_data_dir',
        'METviewer_AWS_scripts_dir', 'DATAROOT', 'COMROOT', 'COMIN', 'COMOUT',
        'VERIF_CASE_STEP_abbrev'
]
if STEP.upper() == 'STATS':
    evs_global_det_atmos_settings_dict['evs'].extend(
            ['COMINccpa', 'COMINnohrsc', 'COMINobsproc',
             'COMINosi_saf', 'COMINghrsst_ospo', 'COMINget_d']
    )
evs_global_det_atmos_settings_dict['shared'] = [
    'model_list', 'model_evs_data_dir_list', 'model_file_format_list',
    'OUTPUTROOT', 'start_date', 'end_date', 'metplus_verbosity',
    'met_verbosity','log_met_output_to_metplus', 'KEEPDATA',
    'SENDCOM', 'SENDARCH', 'SENDMETVIEWER'
]
evs_global_det_atmos_settings_dict['modules'] = ['MET_ROOT', 'METPLUS_PATH']
evs_global_det_atmos_settings_dict['RUN_GRID2GRID_STATS'] = [
    'g2gs_type_list', 'g2gs_mv_database_name', 'g2gs_mv_database_group',
    'g2gs_mv_database_desc'
]
evs_global_det_atmos_settings_dict['RUN_GRID2GRID_PLOTS'] = [
    'g2gp_model_plot_name_list', 'g2gp_type_list',
    'g2gp_event_equalization'
]
evs_global_det_atmos_settings_dict['RUN_GRID2OBS_STATS'] = [
    'g2os_type_list', 'g2os_mv_database_name', 'g2os_mv_database_group',
    'g2os_mv_database_desc'
]
evs_global_det_atmos_settings_dict['RUN_GRID2OBS_PLOTS'] = [
    'g2op_model_plot_name_list', 'g2op_type_list',
    'g2op_event_equalization'
]

verif_case_step_settings_dict = {
    'RUN_GRID2GRID_STATS': {
        'flux': ['init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc'],
        'means': ['init_hr_list', 'valid_hr_list',
                  'fhr_min', 'fhr_max', 'fhr_inc'],
        'ozone': ['init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc'],
        'precip_accum24hr': ['file_format_list', 'file_accum_list', 'var_list',
                             'init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc'],
        'precip_accum3hr': ['file_format_list', 'file_accum_list', 'var_list',
                            'init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc'],
        'pres_levs': ['truth_name_list', 'truth_format_list',
                      'init_hr_list', 'valid_hr_list',
                      'fhr_min', 'fhr_max', 'fhr_inc'],
        'sea_ice': ['init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc'],
        'snow': ['init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc'],
        'sst': ['init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc']
    },
    'RUN_GRID2GRID_PLOTS': {
        'flux': [],
        'means': ['init_hr_list', 'valid_hr_list',
                  'fhr_min', 'fhr_max', 'fhr_inc'],
        'ozone': [],
        'precip': ['init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc'],
        'pres_levs': ['truth_name_list', 'init_hr_list', 'valid_hr_list',
                      'fhr_min', 'fhr_max', 'fhr_inc'],
        'sea_ice': [],
        'snow': ['init_hr_list', 'fhr_min', 'fhr_max', 'fhr_inc'],
        'sst': []
    },
    'RUN_GRID2OBS_STATS': {
        'pres_levs': ['init_hr_list', 'valid_hr_list',
                      'fhr_min', 'fhr_max', 'fhr_inc'],
        'ptype': ['init_hr_list', 'valid_hr_list',
                  'fhr_min', 'fhr_max', 'fhr_inc'],
        'sfc': ['init_hr_list', 'valid_hr_list',
                'fhr_min', 'fhr_max', 'fhr_inc']
    },
    'RUN_GRID2OBS_PLOTS': {
        'pres_levs': ['init_hr_list', 'valid_hr_list',
                      'fhr_min', 'fhr_max', 'fhr_inc'],
        'ptype': ['init_hr_list', 'valid_hr_list',
                  'fhr_min', 'fhr_max', 'fhr_inc'],
        'sfc': ['init_hr_list', 'valid_hr_list',
                'fhr_min', 'fhr_max', 'fhr_inc']
    }
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
                      +"check configuration file "+config)
            sys.exit(1)
verif_type_list  = os.environ[VERIF_CASE_STEP_abbrev+'_type_list'].split(' ')
for verif_type in verif_type_list:
    verif_type_env_var_list = (
        verif_case_step_settings_dict[
            'RUN_'+VERIF_CASE.upper()+'_'+STEP.upper()
        ][verif_type]
    )
    for verif_type_env_var in verif_type_env_var_list:
         env_var_check = (VERIF_CASE_STEP_abbrev+'_'+verif_type+'_'
                          +verif_type_env_var)
         if not env_var_check in os.environ:
              print("ERROR: "+env_var_check+" not set in environment, "
                    +"check configuration file "+config)
              sys.exit(1)

# Do check for list variables lengths
check_config_var_len_list = ['model_evs_data_dir_list',
                             'model_file_format_list']
if STEP.upper() == 'PLOTS':
    check_config_var_len_list.append(VERIF_CASE_STEP_abbrev
                                     +'_model_plot_name_list')
verif_case_step_check_len_dict = {
    'RUN_GRID2GRID_STATS': {
        'flux': [],
        'means': [],
        'ozone': [],
        'precip_accum24hr': ['file_format_list', 'file_accum_list',
                             'var_list'],
        'precip_accum3hr': ['file_format_list', 'file_accum_list',
                            'var_list'],
        'pres_levs': ['truth_name_list', 'truth_format_list'],
        'sea_ice': [],
        'snow': [],
        'sst': []
    },
    'RUN_GRID2GRID_PLOTS': {
        'flux': [],
        'means': [],
        'ozone': [],
        'precip': [],
        'pres_levs': ['truth_name_list'],
        'sea_ice': [],
        'snow': [],
        'sst': []
    },
    'RUN_GRID2OBS_STATS': {
        'pres_levs': [],
        'ptype': [],
        'sfc': []
    },
    'RUN_GRID2OBS_PLOTS': {
        'pres_levs': [],
        'ptype': [],
        'sfc': []
    },
}
for verif_type in verif_type_list:
    for check_list in verif_case_step_check_len_dict[
            'RUN_'+VERIF_CASE.upper()+'_'+STEP.upper()
             ][verif_type]:
        check_config_var_len_list.append(
            VERIF_CASE_STEP_abbrev+'_'+verif_type+'_'+check_list
        )
for config_var in check_config_var_len_list:
    if len(os.environ[config_var].split(' ')) \
            != len(os.environ['model_list'].split(' ')):
     print("ERROR: length of "+config_var+" (length="
           +str(len(os.environ[config_var].split(' ')))+", values="
           +os.environ[config_var]+") not equal to length of model_list "
           +"(length="+str(len(os.environ['model_list'].split(' ')))+", "
           +"values="+os.environ['model_list']+", check "+config+")")
     sys.exit(1)

# Set valid list of options settings
valid_config_var_values_dict = {
    'metplus_verbosity': ['DEBUG', 'INFO', 'WARN', 'ERORR'],
    'met_verbosity': ['0', '1', '2', '3', '4', '5'],
    'log_met_output_to_metplus': ['yes', 'no'],
    'KEEPDATA': ['YES', 'NO'],
    'SENDCOM': ['YES', 'NO'],
}
if STEP.upper() == 'PLOTS':
    valid_config_var_values_dict[
        VERIF_CASE_STEP_abbrev+'_event_equalization'
    ] = ['YES', 'NO']

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
