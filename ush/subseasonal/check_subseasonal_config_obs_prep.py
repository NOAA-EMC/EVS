#!/usr/bin/env python3
'''
Program Name: check_subseasonal_config_obs_prep.py
Contact(s): Shannon Shields
Abstract: This script is run by exevs_subseasonal_obs_prep.sh
          in scripts/prep/subseasonal.
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

# Do check for all environment variables needed by config
env_vars_dict = {
    'shared': ['OUTPUTROOT',
               'start_date', 'end_date', 'make_prep_data_by',
               'inithour_list', 'vhr_list', 'fhr_min', 'fhr_max']
}
env_check_list = ['shared']
for env_check in env_check_list:
    env_var_check_list = env_vars_dict[env_check]
    for env_var_check in env_var_check_list:
        if not env_var_check in os.environ:
            print("FATAL ERROR: "+env_var_check+" not set in config "
                  +"under "+env_check+" settings")
            sys.exit(1)


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


# Do check for valid list config variable options
valid_config_var_values_dict = {
    'make_prep_data_by': ['VALID', 'INIT']
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
        print("FATAL ERROR: value of "+failed_config_value+" for "
              +config_var+" not a valid option. Valid options are "
              +', '.join(valid_config_var_values_dict[config_var]))
        sys.exit(1)

print("END: "+os.path.basename(__file__))



