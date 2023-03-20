'''
Program Name: check_subseasonal_config_settings.py
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
    'shared': ['model_list', 'members',
               'model_dir_list', 'model_stat_dir_list',
               'model_file_format_list', 'model_data_run_hpss',
               'model_hpss_dir_list', 'hpss_walltime', 'OUTPUTROOT',
               'start_date', 'end_date', 'make_met_data_by', 'plot_by',
               'SEND2WEB', 'webhost', 'webhostid', 'webdir', 'MET_version',
               'METplus_version', 'METplus_verbosity', 'MET_verbosity',
               'log_MET_output_to_METplus', 'SENDARCH', 'SENDMETVIEWER',
               'KEEPDATA', 'SENDECF', 'SENDCOM', 'SENDDBN', 'SENDDBN_NTC'],
    'RUN_GRID2GRID_PREP': ['g2gprep_truth_name',
                           'g2gprep_truth_file_format_list',
                           'g2gprep_fcyc_list',
                           'g2gprep_vhr_list',
                           'g2gprep_fhr_min', 'g2gprep_fhr_max',
                           'g2gprep_gather_by'],
    'RUN_GRID2GRID_STATS': ['g2gstats_type_list', 'g2gstats_anom_truth_name',
                            'g2gstats_anom_truth_file_format_list',
                            'g2gstats_anom_fcyc_list', 
                            'g2gstats_anom_vhr_list',
                            'g2gstats_anom_fhr_min', 'g2gstats_anom_fhr_max',
                            'g2gstats_anom_grid', 'g2gstats_anom_gather_by',
                            'g2gstats_pres_truth_name',
                            'g2gstats_pres_truth_file_format_list',
                            'g2gstats_pres_fcyc_list', 
                            'g2gstats_pres_vhr_list',
                            'g2gstats_pres_fhr_min', 'g2gstats_pres_fhr_max',
                            'g2gstats_pres_grid', 'g2gstats_pres_gather_by',
                            'g2gstats_sfc_truth_name',
                            'g2gstats_sfc_truth_file_format_list',
                            'g2gstats_sfc_fcyc_list', 'g2gstats_sfc_vhr_list',
                            'g2gstats_sfc_fhr_min', 'g2gstats_sfc_fhr_max',
                            'g2gstats_sfc_grid', 'g2gstats_sfc_gather_by',
                            'g2gstats_ENSO_truth_name',
                            'g2gstats_ENSO_truth_file_format_list',
                            'g2gstats_ENSO_fcyc_list',
                            'g2gstats_ENSO_vhr_list',
                            'g2gstats_ENSO_fhr_min', 'g2gstats_ENSO_fhr_max',
                            'g2gstats_ENSO_grid', 'g2gstats_ENSO_gather_by',
                            'g2gstats_OLR_truth_name',
                            'g2gstats_OLR_truth_file_format_list',
                            'g2gstats_OLR_fcyc_list',
                            'g2gstats_OLR_vhr_list',
                            'g2gstats_OLR_fhr_min', 'g2gstats_OLR_fhr_max',
                            'g2gstats_OLR_grid', 'g2gstats_OLR_gather_by',
                            'g2gstats_mv_database_name', 
                            'g2gstats_mv_database_group',
                            'g2gstats_mv_database_desc'],
    'RUN_GRID2GRID_PLOTS': ['g2gplots_model_plot_name_list', 
                            'g2gplots_type_list',
                            'g2gplots_anom_truth_name_list',
                            'g2gplots_anom_gather_by_list', 
                            'g2gplots_anom_fcyc_list',
                            'g2gplots_anom_vhr_list', 'g2gplots_anom_fhr_min',                            'g2gplots_anom_fhr_max', 'g2gplots_anom_event_eq',
                            'g2gplots_anom_grid', 
                            'g2gplots_pres_truth_name_list',
                            'g2gplots_pres_gather_by_list', 
                            'g2gplots_pres_fcyc_list',
                            'g2gplots_pres_vhr_list', 'g2gplots_pres_fhr_min',                            'g2gplots_pres_fhr_max', 'g2gplots_pres_event_eq',                            'g2gplots_pres_grid', 
                            'g2gplots_sfc_truth_name_list',
                            'g2gplots_sfc_gather_by_list', 
                            'g2gplots_sfc_fcyc_list',
                            'g2gplots_sfc_vhr_list', 'g2gplots_sfc_fhr_min',
                            'g2gplots_sfc_fhr_max', 'g2gplots_sfc_event_eq',
                            'g2gplots_sfc_grid', 'g2gplots_make_scorecard',
                            'g2gplots_sc_mv_database_list',
                            'g2gplots_sc_valid_start_date',
                            'g2gplots_sc_valid_end_date',
                            'g2gplots_sc_fcyc_list', 'g2gplots_sc_vhr_list'],
    'RUN_GRID2OBS_PREP': ['g2oprep_type_list',
                          'g2oprep_upper_air_msg_type_list',
                          'g2oprep_upper_air_fcyc_list',
                          'g2oprep_upper_air_vhr_list',
                          'g2oprep_upper_air_fhr_min',
                          'g2oprep_upper_air_fhr_max',
                          'g2oprep_upper_air_gather_by',
                          'g2oprep_conus_sfc_msg_type_list',
                          'g2oprep_conus_sfc_fcyc_list',
                          'g2oprep_conus_sfc_vhr_list',
                          'g2oprep_conus_sfc_fhr_min',
                          'g2oprep_conus_sfc_fhr_max',
                          'g2oprep_conus_sfc_gather_by',
                          'g2oprep_prepbufr_data_run_hpss'],
    'RUN_GRID2OBS_STATS': ['g2ostats_type_list',
                           'g2ostats_PrepBufr_msg_type_list',
                           'g2ostats_PrepBufr_fcyc_list',
                           'g2ostats_PrepBufr_vhr_list', 
                           'g2ostats_PrepBufr_fhr_min',
                           'g2ostats_PrepBufr_fhr_max', 
                           'g2ostats_PrepBufr_grid',
                           'g2ostats_PrepBufr_gather_by',
                           'g2ostats_sfc_msg_type_list',
                           'g2ostats_sfc_fcyc_list',
                           'g2ostats_sfc_vhr_list', 
                           'g2ostats_sfc_fhr_min',
                           'g2ostats_sfc_fhr_max', 
                           'g2ostats_sfc_grid',
                           'g2ostats_sfc_gather_by',
                           'g2ostats_prepbufr_data_run_hpss',
                           'g2ostats_mv_database_name', 
                           'g2ostats_mv_database_group',
                           'g2ostats_mv_database_desc'],
    'RUN_GRID2OBS_PLOTS': ['g2oplots_model_plot_name_list', 
                           'g2oplots_type_list',
                           'g2oplots_upper_air_msg_type_list',
                           'g2oplots_upper_air_gather_by_list',
                           'g2oplots_upper_air_fcyc_list',
                           'g2oplots_upper_air_vhr_list', 
                           'g2oplots_upper_air_fhr_min',
                           'g2oplots_upper_air_fhr_max', 
                           'g2oplots_upper_air_event_eq',
                           'g2oplots_upper_air_grid',
                           'g2oplots_conus_sfc_msg_type_list',
                           'g2oplots_conus_sfc_gather_by_list',
                           'g2oplots_conus_sfc_fcyc_list',
                           'g2oplots_conus_sfc_vhr_list', 
                           'g2oplots_conus_sfc_fhr_min',
                           'g2oplots_conus_sfc_fhr_max', 
                           'g2oplots_conus_sfc_event_eq',
                           'g2oplots_conus_sfc_grid'],
    'RUN_PRECIP_STATS': ['precipstats_type_list',
                         'precipstats_ccpa_accum24hr_model_bucket_list',
                         'precipstats_ccpa_accum24hr_model_var_list',
                         'precipstats_ccpa_accum24hr_model_file_format_list',
                         'precipstats_ccpa_accum24hr_fcyc_list',
                         'precipstats_ccpa_accum24hr_fhr_min',
                         'precipstats_ccpa_accum24hr_fhr_max',
                         'precipstats_ccpa_accum24hr_grid',
                         'precipstats_ccpa_accum24hr_gather_by',
                         'precipstats_obs_data_run_hpss',
                         'precipstats_mv_database_name',
                         'precipstats_mv_database_group',
                         'precipstats_mv_database_desc'],
    'RUN_PRECIP_PLOTS': ['precipplots_model_plot_name_list',
                         'precipplots_type_list',
                         'precipplots_ccpa_accum24hr_gather_by_list',
                         'precipplots_ccpa_accum24hr_fcyc_list',
                         'precipplots_ccpa_accum24hr_fhr_min',
                         'precipplots_ccpa_accum24hr_fhr_max',
                         'precipplots_ccpa_accum24hr_event_eq',
                         'precipplots_ccpa_accum24hr_grid']
}
VCS_type_env_check_list = ['shared', 'RUN_'+VERIF_CASE_STEP.upper()]
for VCS_type_env_check in VCS_type_env_check_list:
    VCS_type_env_var_check_list = VCS_type_env_vars_dict[VCS_type_env_check]
    for VCS_type_env_var_check in VCS_type_env_var_check_list:
        if not VCS_type_env_var_check in os.environ:
            print("ERROR: "+VCS_type_env_var_check+" not set in config "
                  +"under "+VCS_type_env_check+" settings")
            sys.exit(1)

if VERIF_CASE_STEP != 'tropcyc':
    VCS_type_list = os.environ[VERIF_CASE_STEP_abbrev+'_type_list'].split(' ')

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
valid_VCS_type_opts_dict = {
    'grid2grid_stats': ['anom', 'pres', 'sfc', 'ENSO', 'OLR'],
    'grid2grid_plots': ['anom', 'pres', 'sfc'],
    'grid2obs_prep': ['upper_air', 'conus_sfc'],
    'grid2obs_stats': ['PrepBufr', 'sfc'],
    'grid2obs_plots': ['upper_air', 'conus_sfc'],
    'precip_stats': ['ccpa_accum24hr'],
    'precip_plots': ['ccpa_accum24hr']
}
if VERIF_CASE_STEP != 'tropcyc':
    for VCS_type in VCS_type_list:
        if VCS_type not in valid_VCS_type_opts_dict[VCS]:
            print("ERROR: "+VCS_type+" not a valid option for "
                  +VCS_abbrev+"_type_list. Valid options are "
                  +', '.join(valid_VCS_type_opts_dict[VCS]))
            sys.exit(1)

# Do check for list config variables lengths
check_config_var_len_list = ['model_dir_list', 'model_stat_dir_list',
                             'model_prep_dir_list',
                             'model_file_format_list', 'model_hpss_dir_list']
if VERIF_CASE_STEP in ['grid2grid_plots', 'grid2obs_plots', 'precip_plots']:
    check_config_var_len_list.append(VCS_abbrev+'_model_plot_name_list')
if VERIF_CASE_STEP == 'tropcyc':
    check_config_var_len_list.append(VCS+'_model_atcf_name_list')
    check_config_var_len_list.append(VCS+'_model_plot_name_list')
    check_config_var_len_list.append(VCS+'_model_file_format_list')
elif VERIF_CASE_STEP == 'maps2d':
    check_config_var_len_list.append(VCS+'_anl_file_format_list')
else:
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        if VERIF_CASE_STEP == 'grid2grid_stats':
            check_config_var_len_list.append(
                VCS_abbrev_type+'_truth_file_format_list'
            )
        elif VERIF_CASE_STEP == 'grid2grid_plots':
            check_config_var_len_list.append(
                VCS_abbrev_type+'_truth_name_list'
            )
            check_config_var_len_list.append(
                VCS_abbrev_type+'_gather_by_list'
            )
        elif VERIF_CASE_STEP == 'grid2obs_plots':
            check_config_var_len_list.append(
                VCS_abbrev_type+'_gather_by_list'
            )
        elif VERIF_CASE_STEP == 'precip_stats':
            check_config_var_len_list.append(
                VCS_abbrev_type+'_model_bucket_list'
            )
            check_config_var_len_list.append(
                VCS_abbrev_type+'_model_var_list'
            )
            check_config_var_len_list.append(
                VCS_abbrev_type+'_model_file_format_list'
            )
        elif VERIF_CASE_STEP == 'precip_plots':
            check_config_var_len_list.append(
                VCS_abbrev_type+'_gather_by_list'
            )
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
    'model_data_run_hpss': ['YES', 'NO'],
    'make_met_data_by': ['VALID', 'INIT'],
    'plot_by': ['VALID', 'INIT'],
    'SEND2WEB': ['YES', 'NO'],
    'METplus_verbosity': ['DEBUG', 'INFO', 'WARN', 'ERORR'],
    'MET_verbosity': ['0', '1', '2', '3', '4', '5'],
    'log_MET_output_to_METplus': ['yes', 'no'],
    'SENDARCH': ['YES', 'NO'],
    'SENDMETVIEWER': ['YES', 'NO'],
    'KEEPDATA': ['YES', 'NO'],
    'SENDECF': ['YES', 'NO'],
    'SENDCOM': ['YES', 'NO'],
    'SENDDBN': ['YES', 'NO'],
    'SENDDBN_NTC': ['YES', 'NO']
}
if VERIF_CASE_STEP in ['grid2grid_prep', 'grid2grid_stats']:
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_truth_name'] = ['gfs_anl', 
                                                        'ecmwf_anl',
                                                        'ccpa_anl', 
                                                        'mrms_anl',
                                                        'umd_anl',
                                                        'ghrsst_anl',
                                                        'osi_anl',
                                                        'ims_anl']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 
                                                       'VSDB']
        if 'anl' in os.environ[VCS_abbrev_type+'_truth_name']:
            truth_opt_list = ['anl', 'anal', 'analysis']
        elif 'f00' in os.environ[VCS_abbrev_type+'_truth_name']:
            truth_opt_list = ['f0', 'f00', 'f000']
        if 'anl' in os.environ[VCS_abbrev_type+'_truth_name'] \
                or 'f00' in os.environ[VCS_abbrev_type+'_truth_name']:
            for truth_file_format \
                    in os.environ[VCS_abbrev_type+'_truth_file_format_list'] \
                    .split(' '):
                if not any(opt in truth_file_format for opt in truth_opt_list):
                    print("ERROR: "+truth_file_format+" in "+VCS_abbrev_type
                          +"_truth_file_format_list does not contain an "
                          +"expected string ("+', '.join(truth_opt_list)+") "
                          +"for "+VCS_abbrev_type+"_truth_name set as "
                          +os.environ[VCS_abbrev_type+'_truth_name'])
                    sys.exit(1)
elif VERIF_CASE_STEP == 'grid2grid_plots':
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_truth_name_list'] = ['gfs_anl',
                                                             'ecmwf_anl',
                                                             'ccpa_anl',
                                                             'mrms_anl',
                                                             'umd_anl',
                                                             'ghrsst_anl',
                                                             'osi_anl',
                                                             'ims_anl']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_event_eq'] = ['True', 'False']
elif VERIF_CASE_STEP in ['grid2obs_prep', 'grid2obs_stats']:
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_msg_type_list'] = ['ADPUPA',
                                                           'AIRCAR',
                                                           'AIRCFT',
                                                           'ADPSFC',
                                                           'ERS1DA',
                                                           'GOESND',
                                                           'GPSIPW',
                                                           'MSONET',
                                                           'PROFLR',
                                                           'QKSWND',
                                                           'RASSDA',
                                                           'SATEMP',
                                                           'SATWND',
                                                           'SFCBOG',
                                                           'SFCSHP',
                                                           'SPSSMI',
                                                           'SYNDAT',
                                                           'VADWND',
                                                           'SURFACE',
                                                           'ANYAIR',
                                                           'ANYSFC',
                                                           'ONLYSF']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 
                                                       'VSDB']
    valid_config_var_values_dict[VERIF_CASE_STEP_abbrev
                                 +'_prepbufr_data_run_hpss'] = ['YES', 'NO']
elif VERIF_CASE_STEP == 'grid2obs_plots':
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_msg_type_list'] = ['ADPUPA',
                                                           'AIRCAR',
                                                           'AIRCFT',
                                                           'ADPSFC',
                                                           'ERS1DA',
                                                           'GOESND',
                                                           'GPSIPW',
                                                           'MSONET',
                                                           'PROFLR',
                                                           'QKSWND',
                                                           'RASSDA',
                                                           'SATEMP',
                                                           'SATWND',
                                                           'SFCBOG',
                                                           'SFCSHP',
                                                           'SPSSMI',
                                                           'SYNDAT',
                                                           'VADWND',
                                                           'SURFACE',
                                                           'ANYAIR',
                                                           'ANYSFC',
                                                           'ONLYSF']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_event_eq'] = ['True', 'False']
elif VERIF_CASE_STEP == 'precip_stats':
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_gather_by'] = ['VALID', 'INIT', 
                                                       'VSDB']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_model_var_list'] = ['APCP', 'PRATE']
        VCS_abbrev_type_accum_length = (
            VCS_type.split('accum')[1].replace('hr','')
        )
        for model_bucket in \
                os.environ[VCS_abbrev_type+'_model_bucket_list'].split(' '):
            if model_bucket != 'continuous':
                if model_bucket.isnumeric():
                    if int(model_bucket) > int(VCS_abbrev_type_accum_length):
                        print("ERROR: value of "+model_bucket+" in "
                              +VCS_abbrev_type+"_model_bucket_list must be "
                              +"<= to "+VCS_abbrev_type+" accumulation length "
                              +"which is "+VCS_abbrev_type_accum_length)
                        sys.exit(1)
                else:
                    print("ERROR: value of "+model_bucket+" in "
                          +VCS_abbrev_type+"_model_bucket_list "
                          +"must be numeric")
                    sys.exit(1)
    valid_config_var_values_dict[VERIF_CASE_STEP_abbrev
                                 +'_obs_data_run_hpss'] = ['YES', 'NO']
elif VERIF_CASE_STEP == 'precip_plots':
    for VCS_type in VCS_type_list:
        VCS_abbrev_type = VERIF_CASE_STEP_abbrev+'_'+VCS_type
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_gather_by_list'] = ['VALID', 'INIT',
                                                            'VSDB']
        valid_config_var_values_dict[VCS_abbrev_type
                                     +'_event_eq'] = ['True', 'False']

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



