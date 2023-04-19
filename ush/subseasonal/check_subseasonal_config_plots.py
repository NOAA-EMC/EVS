'''
Program Name: check_subseasonal_config_plots.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/.
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
               'model_dir_list', 'model_plots_dir_list',
               'model_file_format_list',
               'OUTPUTROOT',
               'start_date', 'end_date', 'plot_by',
               'SEND2WEB', 'webhost', 'webhostid', 'webdir', 'met_version',
               'metplus_version', 'metplus_verbosity', 'met_verbosity',
               'log_met_output_to_metplus', 'SENDARCH',
               'KEEPDATA'],
    'grid2grid_plots': ['g2gplots_model_plot_name_list', 
                        'g2gplots_type_list',
                        'g2gplots_event_eq'],
    'grid2obs_plots': ['g2oplots_model_plot_name_list', 
                       'g2oplots_type_list',
                       'g2oplots_PrepBufr_msg_type_list',
                       'g2oplots_PrepBufr_gather_by_list',
                       'g2oplots_PrepBufr_fcyc_list',
                       'g2oplots_PrepBufr_vhr_list', 
                       'g2oplots_PrepBufr_fhr_min',
                       'g2oplots_PrepBufr_fhr_max', 
                       'g2oplots_PrepBufr_event_eq',
                       'g2oplots_PrepBufr_grid']
}
VCS_type_env_check_list = ['shared', VERIF_CASE_STEP]
for VCS_type_env_check in VCS_type_env_check_list:
    VCS_type_env_var_check_list = VCS_type_env_vars_dict[VCS_type_env_check]
    for VCS_type_env_var_check in VCS_type_env_var_check_list:
        if not VCS_type_env_var_check in os.environ:
            print("ERROR: "+VCS_type_env_var_check+" not set in config "
                  +"under "+VCS_type_env_check+" settings")
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
VCS_type_list = os.environ[VERIF_CASE_STEP_abbrev+'_type_list'].split(' ')
valid_VCS_type_opts_dict = {
    'grid2grid_plots': ['anom', 'pres', 'ENSO', 'OLR', 'precip', 'sst', 
                        'sea_ice'],
    'grid2obs_plots': ['PrepBufr']
}
for VCS_type in VCS_type_list:
    if VCS_type not in valid_VCS_type_opts_dict[VCS]:
        print("ERROR: "+VCS_type+" not a valid option for "
              +VCS_abbrev+"_type_list. Valid options are "
              +', '.join(valid_VCS_type_opts_dict[VCS]))
        sys.exit(1)

# Do check for list config variables lengths
check_config_var_len_list = ['model_dir_list', 'model_plots_dir_list',
                             'model_file_format_list']
if VERIF_CASE_STEP in ['grid2grid_plots', 'grid2obs_plots']:
    check_config_var_len_list.append(VCS_abbrev+'_model_plot_name_list')
    #for VCS_type in VCS_type_list:
        #VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        #if VERIF_CASE_STEP == 'grid2grid_plots':
          #check_config_var_len_list.append(
              #VCS_abbrev_type+'_truth_name_list'
          #)

for config_var in check_config_var_len_list:
    if len(os.environ[config_var].split(' ')) \
            != len(os.environ['model_list'].split(' ')):
        print("ERROR: length of "+config_var+" (length="
              +str(len(os.environ[config_var].split(' ')))+", values="
              +os.environ[config_var]+") not equal to length of model_list "
              +"(length="+str(len(os.environ['model_list'].split(' ')))+", "
              +"values="+os.environ['model_list']+")")
        sys.exit(1)

# Do check for valid list config variable options
valid_config_var_values_dict = {
    'plot_by': ['VALID', 'INIT'],
    'SEND2WEB': ['YES', 'NO'],
    'metplus_verbosity': ['DEBUG', 'INFO', 'WARN', 'ERROR'],
    'met_verbosity': ['0', '1', '2', '3', '4', '5'],
    'log_met_output_to_metplus': ['yes', 'no'],
    'SENDARCH': ['YES', 'NO'],
    'KEEPDATA': ['YES', 'NO']
}
if VERIF_CASE_STEP == 'grid2grid_plots':
    valid_config_var_values_dict[VCS_abbrev
                                 +'_event_eq'] = ['YES', 'NO']
    #for VCS_type in VCS_type_list:
        #VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        #valid_config_var_values_dict[VCS_abbrev_type
                                     #+'_truth_name_list'] = ['gfs_anl',
                                                             #'ecmwf_f00',
                                                             #'ccpa_anl',
                                                             #'mrmsak_anl',
                                                             #'mrmshi_anl',
                                                             #'umd_anl',
                                                             #'ghrsst_anl',
                                                             #'osi_anl']
elif VERIF_CASE_STEP == 'grid2obs_plots':
    valid_config_var_values_dict[VCS_abbrev
                                 +'_event_eq'] = ['YES', 'NO']
    #for VCS_type in VCS_type_list:
        #VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        #valid_config_var_values_dict[VCS_abbrev_type
                                     #+'_msg_type_list'] = ['ADPUPA',
                                                           #'AIRCAR',
                                                           #'AIRCFT',
                                                           #'ADPSFC',
                                                           #'ERS1DA',
                                                           #'GOESND',
                                                           #'GPSIPW',
                                                           #'MSONET',
                                                           #'PROFLR',
                                                           #'QKSWND',
                                                           #'RASSDA',
                                                           #'SATEMP',
                                                           #'SATWND',
                                                           #'SFCBOG',
                                                           #'SFCSHP',
                                                           #'SPSSMI',
                                                           #'SYNDAT',
                                                           #'VADWND',
                                                           #'SURFACE',
                                                           #'ANYAIR',
                                                           #'ANYSFC',
                                                           #'ONLYSF']

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



