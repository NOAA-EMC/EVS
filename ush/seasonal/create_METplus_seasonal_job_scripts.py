'''
Program Name: create_METplus_seasonal_job_scripts.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/.
          This creates multiple independent job cards. These
          jobs contain all the necessary environment variables
          and METplus commands needed to run the specific
          METplus verification use case and types (each job
          could be run independently on the command line).
'''

import sys
import os
import datetime
import glob

print("BEGIN: "+os.path.basename(__file__))

def init_env_dict():
    """! Initialize dictionary with environment variables
         and their values to write in job scripts common
         to all METplus jobs

         Args:

         Returns:
             env_var_dict - dictionary with keys as environment
                            variable names and values as
                            environment variable values
    """
    env_var_list = [
        'HOMEevs', 'USHevs', 'PARMevs',
        'FIXevs', 'maskpath', 'members', 
        'METplus_version', 'HOMEMETplus', 'USHMETplus',
        'log_MET_output_to_METplus', 'METplus_verbosity', 'MET_version',
        'HOMEMET', 'HOMEMET_bin_exec', 'MET_verbosity', 'DATA', 'RUN', 'RM',
        'CUT', 'TR', 'NCAP2', 'CONVERT', 'NCDUMP'
    ]
    env_var_dict = {}
    for env_var in env_var_list:
        env_var_dict[env_var] = os.environ[env_var]
    return env_var_dict

def create_job_scripts_stats(start_date_dt, end_date_dt, case, case_abbrev,
                             case_type_list, run_metplus, machine_conf,
                             conf_dir):
    """! Writes out individual job scripts based on requested verification
         for stats RUN

         Args:
             start_date_dt  - datetime object of the verification start
                              date
             end_date_dt    - datetime object of the verification end
                              date
             case           - string of the verification use case
             case_abbrev    - string of case abbrevation
             case_type_list - list of strings of the types of the
                              verification use case
             run_metplus    - string of path to run_metplus.py
             machine_conf   - string of path to machine METplus conf
             conf_dir       - string of path to base METplus conf directory
         Returns:
    """
    njob = 0
    # Initialize environment variable job dictionary
    job_env_dict = init_env_dict()
    job_env_dict['make_met_data_by'] = os.environ['make_met_data_by']
    # Set important METplus paths
    make_met_data_conf_dir = os.path.join(
        conf_dir, case, 'stats'
    )
    gather_conf_dir = os.path.join(
        conf_dir, case, 'stats'
    )
    # Set case
    job_env_dict['RUN_case'] = case
    # Set up model environment variables in dictionary
    for model in os.environ['model_list'].split(' '):
        job_env_dict['model'] = model
        model_idx = os.environ['model_list'].split(' ').index(model)
        # Set up case_type environment variables in dictionary
        for case_type in case_type_list:
            job_env_dict['RUN_type'] = case_type
            case_abbrev_type = case_abbrev+'_'+case_type
            case_type_env_list = ['gather_by', 'grid',
                                  'fhr_list', 'fhr_beg', 'fhr_end',
                                  'valid_hr_list', 'valid_hr_beg',
                                  'valid_hr_end', 'valid_hr_inc',
                                  'init_hr_list', 'init_hr_beg',
                                  'init_hr_end', 'init_hr_inc']
            for case_type_env in case_type_env_list:
                job_env_dict[case_type_env] = (
                    os.environ[case_abbrev_type+'_'+case_type_env]
                )
            if case == 'grid2grid':
                obtype = os.environ[
                    case_abbrev_type+'_truth_name'
                ].replace('self', model)
                job_env_dict['obtype'] = obtype
            elif case == 'grid2obs':
                if case_type == 'upper_air':
                    obtype = 'gdas'
                elif case_type == 'conus_sfc':
                    date_dt = start_date_dt
                    if date_dt \
                            >= datetime.datetime.strptime('20170320',
                                                          '%Y%m%d'):
                        obtype = 'nam'
                        #obtype = 'rap'

                    else:
                        obtype = 'ndas'
                elif case_type == 'polar_sfc':
                    obtype = 'iabp'
                job_env_dict['obtype'] = obtype
                job_env_dict['msg_type_list'] = ', '.join(
                    os.environ[case_abbrev_type+'_msg_type_list'].split(' ')
                )
            elif case == 'precip':
                job_env_dict['obtype'] = case_type
                job_env_dict['model_bucket'] = os.environ[
                    case_abbrev_type+'_model_bucket_list'
                ].split(' ')[model_idx]
                job_env_dict['model_var'] = os.environ[
                    case_abbrev_type+'_model_var_list'
                ].split(' ')[model_idx]
                job_env_dict['model_file_format'] = os.environ[
                    case_abbrev_type+'_model_file_format_list'
                ].split(' ')[model_idx][0:4]
                if job_env_dict['model_bucket'] == 'continuous':
                    job_env_dict['pcp_combine_method'] = 'SUBTRACT'
                else:
                    job_env_dict['pcp_combine_method'] = 'SUM'
            elif case == 'satellite':
                job_env_dict['obtype'] = case_type
                job_env_dict['sea_ice_thresh'] = os.environ[
                    case_abbrev_type+'_sea_ice_thresh'
                ]
            # Set up date environment variables in dictionary
            date_dt = start_date_dt
            while date_dt <= end_date_dt:
                njob+=1
                job_env_dict['DATE'] = date_dt.strftime('%Y%m%d')
                # Need to do check on grid-to-grid truth file
                # for the date: was requested truth subsituted?
                if case == 'grid2grid':
                    truth_file_list = glob.glob(
                        os.path.join(job_env_dict['DATA'], 'grid2grid_stats',
                                     'data', model, case_type+'.truth.'
                                     +date_dt.strftime('%Y%m%d')+'*')
                    )
                    link_truth_name_list = []
                    if len(truth_file_list) > 0:
                        for truth_file in truth_file_list:
                            if os.path.islink(truth_file):
                                if model in os.readlink(truth_file) \
                                    and 'f000' in os.readlink(truth_file) \
                                    and obtype != model+'_f00':
                                        link_truth_name_list.append(model+'_f00')
                                else:
                                    link_truth_name_list.append(obtype)
                            else:
                                link_truth_name_list.append(obtype)
                    if obtype != model+'_f00':
                        if all(truth == model+'_f00'
                                for truth in link_truth_name_list):
                            job_env_dict['obtype'] = model+'_f00'
                # Create job file
                job_filename = os.path.join(job_env_dict['DATA'],
                                            job_env_dict['RUN'],
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                job_file.write('#!/bin/sh\n')
                job_file.write('set -x\n')
                job_file.write('\n')
                # Write environment variables
                for name, value in job_env_dict.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                job_file.write('\n')
                # Write METplus commmands
                metplus_conf_list = [
                    os.path.join(
                        make_met_data_conf_dir,
                        case_type+'_'+job_env_dict['make_met_data_by']+'.conf'
                    )
                ]
                if case == 'grid2grid' and case_type == 'anom':
                    metplus_conf_list = [
                        os.path.join(
                            make_met_data_conf_dir,
                            case_type+'_height_'
                            +job_env_dict['make_met_data_by']+'.conf'
                        )
                    ]
                metplus_conf_list.append(
                    os.path.join(
                        gather_conf_dir, job_env_dict['gather_by']+'.conf'
                    )
                )
                for metplus_conf in metplus_conf_list:
                    job_file.write(
                        run_metplus+' -c '+machine_conf+' '
                        +'-c '+metplus_conf+'\n'
                    )
                job_file.close()
                date_dt = date_dt + datetime.timedelta(days=1)

def create_job_scripts_plots(start_date_dt, end_date_dt, case, case_abbrev,
                             case_type_list, run_metplus, machine_conf,
                             conf_dir):
    """! Writes out individual job scripts based on requested verification
         for plots RUN

         Args:
             start_date_dt  - datetime object of the verification start
                              date
             end_date_dt    - datetime object of the verification end
                              date
             case           - string of the verification use case
             case_abbrev    - string of case abbrevation
             case_type_list - list of strings of the types of the
                              verification use case
             run_metplus    - string of path to run_metplus.py
             machine_conf   - string of path to machine METplus conf
             conf_dir       - string of path to base METplus conf directory

         Returns:
    """
    # Set up plotting information dictionary
    plotting_case_case_type_dict = {
        'grid2grid_anom': {
            'SAL1L2': {
                'plot_stats_list': 'acc',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['NHX', 'SHX', 'TRO'],
                'var_dict': {
                    'HGT': {'fcst_var_name': 'HGT',
                            'fcst_var_levels': ['P500'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'HGT',
                            'obs_var_levels': ['P500'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    #'HGT_WV1_0-20': {'fcst_var_name': 'HGT',
                                     #'fcst_var_levels': ['P500'],
                                     #'fcst_var_thresholds': '',
                                     #'fcst_var_options': '',
                                     #'obs_var_name': 'HGT',
                                     #'obs_var_levels': ['P500'],
                                     #'obs_var_thresholds': '',
                                     #'obs_var_options': ''},
                    #'HGT_WV1_0-3': {'fcst_var_name': 'HGT',
                                    #'fcst_var_levels': ['P500'],
                                    #'fcst_var_thresholds': '',
                                    #'fcst_var_options': '',
                                    #'obs_var_name': 'HGT',
                                    #'obs_var_levels': ['P500'],
                                    #'obs_var_thresholds': '',
                                    #'obs_var_options': ''},
                    #'HGT_WV1_4-9': {'fcst_var_name': 'HGT',
                                    #'fcst_var_levels': ['P500'],
                                    #'fcst_var_thresholds': '',
                                    #'fcst_var_options': '',
                                    #'obs_var_name': 'HGT',
                                    #'obs_var_levels': ['P500'],
                                    #'obs_var_thresholds': '',
                                    #'obs_var_options': ''},
                    #'HGT_WV1_10-20': {'fcst_var_name': 'HGT',
                                      #'fcst_var_levels': ['P500'],
                                      #'fcst_var_thresholds': '',
                                      #'fcst_var_options': '',
                                      #'obs_var_name': 'HGT',
                                      #'obs_var_levels': ['P500'],
                                      #'obs_var_thresholds': '',
                                      #'obs_var_options': ''},
                    'TMP': {'fcst_var_name': 'TMP',
                            'fcst_var_levels': ['P850'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'TMP',
                            'obs_var_levels': ['P850'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    'UGRD': {'fcst_var_name': 'UGRD',
                             'fcst_var_levels': ['P250'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'UGRD',
                             'obs_var_levels': ['P250'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    'VGRD': {'fcst_var_name': 'VGRD',
                             'fcst_var_levels': ['P250'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'VGRD',
                             'obs_var_levels': ['P250'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    #'PRMSL': {'fcst_var_name': 'PRMSL',
                              #'fcst_var_levels': ['Z0'],
                              #'fcst_var_thresholds': '',
                              #'fcst_var_options': '',
                              #'obs_var_name': 'PRMSL',
                              #'obs_var_levels': ['Z0'],
                              #'obs_var_thresholds': '',
                              #'obs_var_options': ''}
                 }
            },
            'SL1L2': {
                'plot_stats_list': 'bias, rmse',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['NHX', 'SHX', 'TRO'],
                'var_dict': {
                    'HGT': {'fcst_var_name': 'HGT',
                            'fcst_var_levels': ['P500'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'HGT',
                            'obs_var_levels': ['P500'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    'TMP': {'fcst_var_name': 'TMP',
                            'fcst_var_levels': ['P850'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'TMP',
                            'obs_var_levels': ['P850'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    'UGRD': {'fcst_var_name': 'UGRD',
                             'fcst_var_levels': ['P250'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'UGRD',
                             'obs_var_levels': ['P250'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    'VGRD': {'fcst_var_name': 'VGRD',
                             'fcst_var_levels': ['P250'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'VGRD',
                             'obs_var_levels': ['P250'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                }
            }
            #'VAL1L2': {
                #'plot_stats_list': 'acc',
                #'interp' : 'NEAREST',
                #'vx_mask_list' : ['NHX', 'SHX', 'PNA', 'TRO'],
                #'var_dict': {
                    #'UGRD_VGRD': {'fcst_var_name': 'UGRD_VGRD',
                                  #'fcst_var_levels': ['P850', 'P500', 'P250'],
                                  #'fcst_var_thresholds': '',
                                  #'fcst_var_options': '',
                                  #'obs_var_name': 'UGRD_VGRD',
                                  #'obs_var_levels': ['P850', 'P500', 'P250'],
                                  #'obs_var_thresholds': '',
                                  #'obs_var_options': ''}
                #}
            #}
        },
        'grid2grid_pres': {
            'SL1L2': {
                'plot_stats_list': 'rmse',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['NHX', 'SHX', 'TRO'],
                'var_dict': {
                    'HGT': {'fcst_var_name': 'HGT',
                            'fcst_var_levels': ['P500'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'HGT',
                            'obs_var_levels': ['P500'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    'TMP': {'fcst_var_name': 'TMP',
                            'fcst_var_levels': ['P850'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'TMP',
                            'obs_var_levels': ['P850'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    'UGRD': {'fcst_var_name': 'UGRD',
                             'fcst_var_levels': ['P250'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'UGRD',
                             'obs_var_levels': ['P250'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    'VGRD': {'fcst_var_name': 'VGRD',
                             'fcst_var_levels': ['P250'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'VGRD',
                             'obs_var_levels': ['P250'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    #'O3MR': {'fcst_var_name': 'O3MR',
                             #'fcst_var_levels': ['P100', 'P70', 'P50',
                                                 #'P30', 'P20', 'P10',
                                                 #'P5', 'P1'],
                             #'fcst_var_thresholds': '',
                             #'fcst_var_options': '',
                             #'obs_var_name': 'O3MR',
                             #'obs_var_levels': ['P100', 'P70', 'P50',
                                                #'P30', 'P20', 'P10',
                                                #'P5', 'P1'],
                             #'obs_var_thresholds': '',
                             #'obs_var_options': ''}
                }
            },
            #'VL1L2': {
                #'plot_stats_list': 'bias, rmse, msess, rsd, rmse_md, rmse_pv',
                #'interp' : 'NEAREST',
                #'vx_mask_list' : ['NHX', 'SHX', 'PNA', 'TRO'],
                #'var_dict': {
                    #'UGRD_VGRD': {'fcst_var_name': 'UGRD_VGRD',
                                  #'fcst_var_levels': ['P1000', 'P850', 'P700',
                                                      #'P500', 'P200', 'P100',
                                                      #'P50', 'P20', 'P10',
                                                      #'P5', 'P1'],
                                  #'fcst_var_thresholds': '',
                                  #'fcst_var_options': '',
                                  #'obs_var_name': 'UGRD_VGRD',
                                  #'obs_var_levels': ['P1000', 'P850', 'P700',
                                                     #'P500', 'P200', 'P100',
                                                     #'P50', 'P20', 'P10',
                                                     #'P5', 'P1'],
                                  #'obs_var_thresholds': '',
                                  #'obs_var_options': ''}
                #}
            #}
        },
        'grid2grid_sfc': {
            'SL1L2': {
                'plot_stats_list': 'fbar',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['NHX', 'SHX', 'N60', 'S60', 'TRO', 'NPO',
                                  'SPO', 'NAO', 'SAO', 'CONUS'],
                'var_dict': {
                    'TMP2m': {'fcst_var_name': 'TMP',
                              'fcst_var_levels': ['Z2'],
                              'fcst_var_thresholds': '',
                              'fcst_var_options': '',
                              'obs_var_name': 'TMP',
                              'obs_var_levels': ['Z2'],
                              'obs_var_thresholds': '',
                              'obs_var_options': ''},
                    'TMPsfc': {'fcst_var_name': 'TMP',
                               'fcst_var_levels': ['Z0'],
                               'fcst_var_thresholds': '',
                               'fcst_var_options': '',
                               'obs_var_name': 'TMP',
                               'obs_var_levels': ['Z0'],
                               'obs_var_thresholds': '',
                               'obs_var_options': ''},
                    'TMPtrops': {'fcst_var_name': 'TMP',
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': 'GRIB_lvl_typ = 7;',
                                 'obs_var_name': 'TMP',
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': 'GRIB_lvl_typ = 7;'},
                    'RH2m': {'fcst_var_name': 'RH',
                             'fcst_var_levels': ['Z2'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'RH',
                             'obs_var_levels': ['Z2'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    'SPFH2m': {'fcst_var_name': 'SPFH',
                               'fcst_var_levels': ['Z2'],
                               'fcst_var_thresholds': '',
                               'fcst_var_options': '',
                               'obs_var_name': 'SPFH',
                               'obs_var_levels': ['Z2'],
                               'obs_var_thresholds': '',
                               'obs_var_options': ''},
                    'HPBL': {'fcst_var_name': 'HPBL',
                             'fcst_var_levels': ['L0'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'HPBL',
                             'obs_var_levels': ['L0'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    'PRESsfc': {'fcst_var_name': 'PRES',
                                'fcst_var_levels': ['Z0'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_name': 'PRES',
                                'obs_var_levels': ['Z0'],
                                'obs_var_thresholds': '',
                                'obs_var_options': ''},
                    'PREStrops': {'fcst_var_name': 'PRES',
                                  'fcst_var_levels': ['L0'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': 'GRIB_lvl_typ = 7;',
                                  'obs_var_name': 'PRES',
                                  'obs_var_levels': ['L0'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': 'GRIB_lvl_typ = 7;'},
                    'PRMSL': {'fcst_var_name': 'PRMSL',
                              'fcst_var_levels': ['Z0'],
                              'fcst_var_thresholds': '',
                              'fcst_var_options': '',
                              'obs_var_name': 'PRMSL',
                              'obs_var_levels': ['Z0'],
                              'obs_var_thresholds': '',
                              'obs_var_options': ''},
                    'UGRD10m': {'fcst_var_name': 'UGRD',
                                'fcst_var_levels': ['Z10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_name': 'UGRD',
                                'obs_var_levels': ['Z10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': ''},
                    'VGRD10m': {'fcst_var_name': 'VGRD',
                                'fcst_var_levels': ['Z10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_name': 'VGRD',
                                'obs_var_levels': ['Z10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': ''},
                    'TSOILtop': {'fcst_var_name': 'TSOIL',
                                 'fcst_var_levels': ['Z10-0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_name': 'TSOIL',
                                 'obs_var_levels': ['Z10-0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': ''},
                    'SOILWtop': {'fcst_var_name': 'SOILW',
                                 'fcst_var_levels': ['Z10-0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_name': 'SOILW',
                                 'obs_var_levels': ['Z10-0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': ''},
                    'WEASD': {'fcst_var_name': 'WEASD',
                              'fcst_var_levels': ['Z0'],
                              'fcst_var_thresholds': '',
                              'fcst_var_options': '',
                              'obs_var_name': 'WEASD',
                              'obs_var_levels': ['Z0'],
                              'obs_var_thresholds': '',
                              'obs_var_options': ''},
                    'CAPE': {'fcst_var_name': 'CAPE',
                             'fcst_var_levels': ['Z0'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'CAPE',
                             'obs_var_levels': ['Z0'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    'PWAT': {'fcst_var_name': 'PWAT',
                             'fcst_var_levels': ['L0'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'PWAT',
                             'obs_var_levels': ['L0'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    'CWAT': {'fcst_var_name': 'CWAT',
                             'fcst_var_levels': ['L0'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'CWAT',
                             'obs_var_levels': ['L0'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''},
                    'HGTtrops': {'fcst_var_name': 'HGT',
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': 'GRIB_lvl_typ = 7;',
                                 'obs_var_name': 'HGT',
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': 'GRIB_lvl_typ = 7;'},
                    'TOZNEclm': {'fcst_var_name': 'TOZNE',
                                 'fcst_var_levels': ['L0'],
                                 'fcst_var_thresholds': '',
                                 'fcst_var_options': '',
                                 'obs_var_name': 'TOZNE',
                                 'obs_var_levels': ['L0'],
                                 'obs_var_thresholds': '',
                                 'obs_var_options': ''}
                }
            }
        },
        'grid2obs_upper_air': {
            'SL1L2': {
                'plot_stats_list': 'bias, rmse, fbar_obar',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['NH', 'SH', 'TRO', 'G236', 'POLAR',
                                  'ARCTIC'],
                'var_dict': {
                    'TMP': {'fcst_var_name': 'TMP',
                            'fcst_var_levels': ['P1000', 'P925', 'P850',
                                                'P700', 'P500', 'P400',
                                                'P300', 'P250', 'P200',
                                                'P150', 'P100', 'P50',
                                                'P10', 'P5', 'P1'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'TMP',
                            'obs_var_levels': ['P1000', 'P925', 'P850',
                                                'P700', 'P500', 'P400',
                                                'P300', 'P250', 'P200',
                                                'P150', 'P100', 'P50',
                                                'P10', 'P5', 'P1'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    'RH': {'fcst_var_name': 'RH',
                           'fcst_var_levels': ['P1000', 'P925', 'P850',
                                               'P700', 'P500', 'P400',
                                               'P300', 'P250', 'P200',
                                               'P150', 'P100', 'P50',
                                               'P10', 'P5', 'P1'],
                           'fcst_var_thresholds': '',
                           'fcst_var_options': '',
                           'obs_var_name': 'RH',
                           'obs_var_levels': ['P1000', 'P925', 'P850',
                                               'P700', 'P500', 'P400',
                                               'P300', 'P250', 'P200',
                                               'P150', 'P100', 'P50',
                                               'P10', 'P5', 'P1'],
                           'obs_var_thresholds': '',
                           'obs_var_options': ''}
                }
            },
            'VL1L2': {
                'plot_stats_list': 'bias, rmse, fbar_obar',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['NH', 'SH', 'TRO', 'G236', 'POLAR',
                                  'ARCTIC'],
                'var_dict': {
                    'UGRD_VGRD': {'fcst_var_name': 'UGRD_VGRD',
                                  'fcst_var_levels': ['P1000', 'P925', 'P850',
                                                      'P700', 'P500', 'P400',
                                                      'P300', 'P250', 'P200',
                                                      'P150', 'P100', 'P50',
                                                      'P10', 'P5', 'P1'],
                                  'fcst_var_thresholds': '',
                                  'fcst_var_options': '',
                                  'obs_var_name': 'UGRD_VGRD',
                                  'obs_var_levels': ['P1000', 'P925', 'P850',
                                                     'P700', 'P500', 'P400',
                                                     'P300', 'P250', 'P200',
                                                     'P150', 'P100', 'P50',
                                                     'P10', 'P5', 'P1'],
                                  'obs_var_thresholds': '',
                                  'obs_var_options': ''}
                }
            }
        },
        'grid2obs_conus_sfc': {
            'SL1L2': {
                'plot_stats_list': 'bias, rmse, fbar_obar',
                'interp' : 'NEAREST',
                #'vx_mask_list' : ['WEST', 'EAST', 'MDW', 'NPL', 'SPL', 'NEC',
                                  #'SEC', 'NWC', 'SWC', 'NMT', 'SMT', 'SWD',
                                  #'GRB', 'LMV', 'GMC', 'APL', 'NAK', 'SAK'],
                'vx_mask_list' : ['CONUS'], #HWI
                #'vx_mask_list' : ['NAK', 'SAK'],
                'var_dict': {
                    'TMP2m': {'fcst_var_name': 'TMP',
                              'fcst_var_levels': ['Z2'],
                              'fcst_var_thresholds': '',
                              'fcst_var_options': '',
                              'obs_var_name': 'TMP',
                              'obs_var_levels': ['Z2'],
                              'obs_var_thresholds': '',
                              'obs_var_options': ''},
                    'UGRD10m': {'fcst_var_name': 'UGRD',
                                'fcst_var_levels': ['Z10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_name': 'UGRD',
                                'obs_var_levels': ['Z10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': ''},
                    'VGRD10m': {'fcst_var_name': 'VGRD',
                                'fcst_var_levels': ['Z10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_name': 'VGRD',
                                'obs_var_levels': ['Z10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': ''}
                    #'RH2m': {'fcst_var_name': 'RH',
                             #'fcst_var_levels': ['Z2'],
                             #'fcst_var_thresholds': '',
                             #'fcst_var_options': '',
                             #'obs_var_name': 'RH',
                             #'obs_var_levels': ['Z2'],
                             #'obs_var_thresholds': '',
                             #'obs_var_options': ''},
                    #'DPT2m': {'fcst_var_name': 'DPT',
                              #'fcst_var_levels': ['Z2'],
                              #'fcst_var_thresholds': '',
                              #'fcst_var_options': '',
                              #'obs_var_name': 'DPT',
                              #'obs_var_levels': ['Z2'],
                              #'obs_var_thresholds': '',
                              #'obs_var_options': ''},
                    #'TCDC': {'fcst_var_name': 'TCDC',
                             #'fcst_var_levels': ['L0'],
                             #'fcst_var_thresholds': '',
                             #'fcst_var_options': 'GRIB_lvl_typ = 200;',
                             #'obs_var_name': 'TCDC',
                             #'obs_var_levels': ['L0'],
                             #'obs_var_thresholds': '',
                             #'obs_var_options': ''},
                    #'PRMSL': {'fcst_var_name': 'PRMSL',
                              #'fcst_var_levels': ['Z0'],
                              #'fcst_var_thresholds': '',
                              #'fcst_var_options': '',
                              #'obs_var_name': 'PRMSL',
                              #'obs_var_levels': ['Z0'],
                              #'obs_var_thresholds': '',
                              #'obs_var_options': ''},
                    #'VISsfc': {'fcst_var_name': 'VIS',
                               #'fcst_var_levels': ['Z0'],
                               #'fcst_var_thresholds': '',
                               #'fcst_var_options': '',
                               #'obs_var_name': 'VIS',
                               #'obs_var_levels': ['Z0'],
                               #'obs_var_thresholds': '',
                               #'obs_var_options': ''},
                    #'HGTcldceil': {'fcst_var_name': 'HGT',
                                   #'fcst_var_levels': ['L0'],
                                   #'fcst_var_thresholds': '',
                                   #'fcst_var_options': 'GRIB_lvl_typ = 215;',
                                   #'obs_var_name': 'HGT',
                                   #'obs_var_levels': ['L0'],
                                   #'obs_var_thresholds': '',
                                   #'obs_var_options': ''},
                    #'CAPEsfc': {'fcst_var_name': 'CAPE',
                                #'fcst_var_levels': ['Z0'],
                                #'fcst_var_thresholds': '',
                                #'fcst_var_options': '',
                                #'obs_var_name': 'CAPE',
                                #'obs_var_levels': ['L100000-0'],
                                #'obs_var_thresholds': '',
                                #'obs_var_options': ''},
                    #'GUSTsfc': {'fcst_var_name': 'GUST',
                                #'fcst_var_levels': ['Z0'],
                                #'fcst_var_thresholds': '',
                                #'fcst_var_options': '',
                                #'obs_var_name': 'GUST',
                                #'obs_var_levels': ['Z0'],
                                #'obs_var_thresholds': '',
                                #'obs_var_options': ''},
                    #'HPBL': {'fcst_var_name': 'HPBL',
                             #'fcst_var_levels': ['L0'],
                             #'fcst_var_thresholds': '',
                             #'fcst_var_options': '',
                             #'obs_var_name': 'HPBL',
                             #'obs_var_levels': ['L0'],
                             #'obs_var_thresholds': '',
                             #'obs_var_options': ''}
                }
            },
            'SAL1L2': {
                'plot_stats_list': 'acc',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['CONUS'], #HWI
                #'vx_mask_list' : ['NAK', 'SAK'],
                'var_dict': {
                    'TMP2m': {'fcst_var_name': 'TMP',
                              'fcst_var_levels': ['Z2'],
                              'fcst_var_thresholds': '',
                              'fcst_var_options': '',
                              'obs_var_name': 'TMP',
                              'obs_var_levels': ['Z2'],
                              'obs_var_thresholds': '',
                              'obs_var_options': ''},
                    'UGRD10m': {'fcst_var_name': 'UGRD',
                                'fcst_var_levels': ['Z10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_name': 'UGRD',
                                'obs_var_levels': ['Z10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': ''},
                    'VGRD10m': {'fcst_var_name': 'VGRD',
                                'fcst_var_levels': ['Z10'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_name': 'VGRD',
                                'obs_var_levels': ['Z10'],
                                'obs_var_thresholds': '',
                                'obs_var_options': ''}
                }
            },
            'CTC': {
                'plot_stats_list': 'hss',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['CONUS'], #HWI
                #'vx_mask_list' : ['NAK', 'SAK'],
                'var_dict': {
                    'TMP2m': {'fcst_var_name': 'TMP',
                              'fcst_var_levels': ['Z2'],
                              'fcst_var_thresholds': '',
                              'fcst_var_options': '',
                              'obs_var_name': 'TMP',
                              'obs_var_levels': ['Z2'],
                              'obs_var_thresholds': '',
                              'obs_var_options': ''}#,
                    #'UGRD10m': {'fcst_var_name': 'UGRD',
                                #'fcst_var_levels': ['Z10'],
                                #'fcst_var_thresholds': '',
                                #'fcst_var_options': '',
                                #'obs_var_name': 'UGRD',
                                #'obs_var_levels': ['Z10'],
                                #'obs_var_thresholds': '',
                                #'obs_var_options': ''},
                    #'VGRD10m': {'fcst_var_name': 'VGRD',
                                #'fcst_var_levels': ['Z10'],
                                #'fcst_var_thresholds': '',
                                #'fcst_var_options': '',
                                #'obs_var_name': 'UGRD',
                                #'obs_var_levels': ['Z10'],
                                #'obs_var_thresholds': '',
                                #'obs_var_options': ''}
                }
            }, 
            'VL1L2': {
                'plot_stats_list': 'bias, rmse, fbar_obar',
                'interp' : 'NEAREST',
                #'vx_mask_list' : ['WEST', 'EAST', 'MDW', 'NPL', 'SPL', 'NEC',
                                  #'SEC', 'NWC', 'SWC', 'NMT', 'SMT', 'SWD',
                                  #'GRB', 'LMV', 'GMC', 'APL', 'NAK', 'SAK'],
                'vx_mask_list' : ['CONUS'], #HWI
                #'vx_mask_list' : ['NAK', 'SAK'],
                'var_dict': {
                    'UGRD_VGRD10m': {'fcst_var_name': 'UGRD_VGRD',
                                     'fcst_var_levels': ['Z10'],
                                     'fcst_var_thresholds': '',
                                     'fcst_var_options': '',
                                     'obs_var_name': 'UGRD_VGRD',
                                     'obs_var_levels': ['Z10'],
                                     'obs_var_thresholds': '',
                                     'obs_var_options': ''},
                }
            }
        },
        'grid2obs_polar_sfc': {
            'SL1L2': {
                'plot_stats_list': 'bias, rmse, fbar_obar',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['ARCTIC'],
                'var_dict': {
                    'TMP2m': {'fcst_var_name': 'TMP',
                              'fcst_var_levels': ['Z2'],
                              'fcst_var_thresholds': '',
                              'fcst_var_options': '',
                              'obs_var_name': 'TMP',
                              'obs_var_levels': ['Z2'],
                              'obs_var_thresholds': '',
                              'obs_var_options': ''},
                    'TMPsfc': {'fcst_var_name': 'TMP',
                               'fcst_var_levels': ['Z0'],
                               'fcst_var_thresholds': '',
                               'fcst_var_options': '',
                               'obs_var_name': 'TMP',
                               'obs_var_levels': ['Z0'],
                               'obs_var_thresholds': '',
                               'obs_var_options': ''},
                    'PRESsfc': {'fcst_var_name': 'PRES',
                                'fcst_var_levels': ['Z0'],
                                'fcst_var_thresholds': '',
                                'fcst_var_options': '',
                                'obs_var_name': 'PRES',
                                'obs_var_levels': ['Z0'],
                                'obs_var_thresholds': '',
                                'obs_var_options': ''}
                }
            }
        },
        'precip_ccpa_accum24hr': {
            'CTC': {
                'plot_stats_list': 'bias, ets',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['EAST', 'WEST'],
                'var_dict': {
                   'APCP_24': {'fcst_var_name': 'APCP_24',
                               'fcst_var_levels': ['A24'],
                               'fcst_var_thresholds': ('ge0.2, ge2, ge5, '
                                                       +'ge10, ge15, ge25, '
                                                       +'ge35, ge50, ge75'),
                               'fcst_var_options': '',
                               'obs_var_name': 'APCP_24',
                               'obs_var_levels': ['A24'],
                               'obs_var_thresholds': ('ge0.2, ge2, ge5, '
                                                      +'ge10, ge15, ge25, '
                                                      +'ge35, ge50, ge75'),
                               'obs_var_options': ''}
                }
            }
        },
        'satellite_ghrsst_ncei_avhrr_anl': {
            'SL1L2': {
                'plot_stats_list': 'bias, rmse',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['NH', 'SH', 'POLAR', 'ARCTIC', 'SEA_ICE',
                                  'SEA_ICE_FREE', 'SEA_ICE_POLAR',
                                  'SEA_ICE_FREE_POLAR'],
                'var_dict': {
                    'SST': {'fcst_var_name': 'TMP_Z0_mean',
                            'fcst_var_levels': ['Z0'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'analysed_sst',
                            'obs_var_levels': ['Z0'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    'ICEC': {'fcst_var_name': 'ICEC_Z0_mean',
                             'fcst_var_levels': ['Z0'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options':  '',
                             'obs_var_name': 'sea_ice_fraction',
                             'obs_var_levels': ['Z0'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''}
                }
            }
        },
        'satellite_ghrsst_ospo_geopolar_anl': {
            'SL1L2': {
                'plot_stats_list': 'bias, rmse',
                'interp' : 'NEAREST',
                'vx_mask_list' : ['NH', 'SH', 'POLAR', 'ARCTIC', 'SEA_ICE',
                                  'SEA_ICE_FREE', 'SEA_ICE_POLAR',
                                  'SEA_ICE_FREE_POLAR'],
                'var_dict': {
                    'SST': {'fcst_var_name': 'TMP_Z0_mean',
                            'fcst_var_levels': ['Z0'],
                            'fcst_var_thresholds': '',
                            'fcst_var_options': '',
                            'obs_var_name': 'analysed_sst',
                            'obs_var_levels': ['Z0'],
                            'obs_var_thresholds': '',
                            'obs_var_options': ''},
                    'ICEC': {'fcst_var_name': 'ICEC_Z0_mean',
                             'fcst_var_levels': ['Z0'],
                             'fcst_var_thresholds': '',
                             'fcst_var_options': '',
                             'obs_var_name': 'sea_ice_fraction',
                             'obs_var_levels': ['Z0'],
                             'obs_var_thresholds': '',
                             'obs_var_options': ''}
                }
            }
        }
    }
    njob = 0
    # Initialize environment variable job dictionary
    job_env_dict = init_env_dict()
    job_env_dict['plot_by'] = os.environ['plot_by']
    if job_env_dict['plot_by'] == 'VALID':
        job_env_dict['VALID_BEG'] = start_date_dt.strftime('%Y%m%d')
        job_env_dict['VALID_END'] = end_date_dt.strftime('%Y%m%d')
        job_env_dict['INIT_BEG'] = ''
        job_env_dict['INIT_END'] = ''
        if case == 'grid2obs':
            job_env_dict['group_list'] = 'FCST_VALID_HOUR_LIST'
            job_env_dict['loop_list'] = 'FCST_INIT_HOUR_LIST'
        else:
            job_env_dict['group_list'] = 'FCST_INIT_HOUR_LIST'
            job_env_dict['loop_list'] = 'FCST_VALID_HOUR_LIST'
    elif job_env_dict['plot_by'] == 'INIT':
        job_env_dict['VALID_BEG'] = ''
        job_env_dict['VALID_END'] = ''
        job_env_dict['INIT_BEG'] = start_date_dt.strftime('%Y%m%d')
        job_env_dict['INIT_END'] = end_date_dt.strftime('%Y%m%d')
        if case == 'grid2obs':
            job_env_dict['group_list'] = 'FCST_INIT_HOUR_LIST'
            job_env_dict['loop_list'] = 'FCST_VALID_HOUR_LIST'
        else:
            job_env_dict['group_list'] = 'FCST_VALID_HOUR_LIST'
            job_env_dict['loop_list'] = 'FCST_INIT_HOUR_LIST'
    # Set important METplus paths
    plot_conf_dir = os.path.join(conf_dir, case, 'plots')
    # Set case
    job_env_dict['RUN_case'] = case
    # Set up model environment variables in dictionary
    model_list = os.environ['model_list'].split(' ')
    model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
    model_plot_name_list = os.environ[
        case_abbrev+'_model_plot_name_list'
    ].split(' ')
    nmodels = len(model_list)
    if nmodels > 8:
        print("ERROR: Too many models listed in model_list ("
              +str(nmodels)+"), current maximum is 8")
        sys.exit(1)
    for model in model_list:
        model_idx = model_list.index(model)
        model_num = model_idx + 1
        job_env_dict['model'+str(model_num)] = model
        job_env_dict['model'+str(model_num)+'_stat_dir'] = (
            model_stat_dir_list[model_idx]
        )
        job_env_dict['model'+str(model_num)+'_plot_name'] = (
            model_plot_name_list[model_idx]
        )
    # Set up case_type environment variables in dictionary
    for case_type in case_type_list:
        case_abbrev_type = case_abbrev+'_'+case_type
        model_gather_by_list = (
            os.environ[case_abbrev_type+'_gather_by_list'].split(' ')
        )
        for model in model_list:
            model_idx = model_list.index(model)
            model_num = model_idx + 1
            job_env_dict['model'+str(model_num)+'_gather_by'] = (
                model_gather_by_list[model_idx]
            )
            if case == 'grid2grid':
                job_env_dict['model'+str(model_num)+'_obtype'] = (
                    os.environ[case_abbrev_type+'_truth_name_list'].split(' ')
                )[model_idx]
                if 'self' in job_env_dict['model'+str(model_num)+'_obtype']:
                    job_env_dict['model'+str(model_num)+'_obtype'] = (
                        job_env_dict['model'+str(model_num)+'_obtype'] \
                        .replace('self', model)
                    )
            elif case == 'grid2obs':
                job_env_dict['model'+str(model_num)+'_obtype'] = (
                    '_'.join(os.environ[
                        case_abbrev_type+'_msg_type_list'
                    ].split(' '))
                )
            elif case == 'precip':
                job_env_dict['model'+str(model_num)+'_obtype'] = case_type
            elif case == 'satellite':
                job_env_dict['model'+str(model_num)+'_obtype'] = case_type
        job_env_dict['RUN_type'] = case_type
        case_type_env_list = ['grid', 'event_eq', 'fhr_list', 'valid_hr_list',
                              'valid_hr_beg', 'valid_hr_end', 'valid_hr_inc',
                              'init_hr_list', 'init_hr_beg', 'init_hr_end',
                              'init_hr_inc']
        for case_type_env in case_type_env_list:
            job_env_dict[case_type_env] = (
                os.environ[case_abbrev_type+'_'+case_type_env]
            )
        plotting_dict = plotting_case_case_type_dict[case+'_'+case_type]
        # Set up plotting environment variables in dictionary
        for line_type in list(plotting_dict.keys()):
            job_env_dict['line_type'] = line_type
            job_env_dict['plot_stats_list'] = (
                plotting_dict[line_type]['plot_stats_list']
            )
            var_dict = plotting_dict[line_type]['var_dict']
            vx_mask_list = plotting_dict[line_type]['vx_mask_list']
            vx_mask_list.append(job_env_dict['grid'])
            for var_name, fcst_obs_var_info in var_dict.items():
                job_env_dict['var_name'] = var_name
                for var_info, var_info_val in fcst_obs_var_info.items():
                    if 'levels' in var_info:
                        job_env_dict[var_info] = (
                            ' '.join(var_info_val).replace(' ', ', ')
                        )
                    else:
                        job_env_dict[var_info] = var_info_val
                if case == 'grid2grid' and case_type == 'anom' \
                        and 'HGT_WV1' in var_name:
                    job_env_dict['interp'] = (
                        var_name.replace('HGT_', '')
                    )
                    job_env_dict['fourier_decomp'] = 'True'
                    job_env_dict['wave_num_list'] = (
                        var_name.replace('HGT_WV1_', '')
                    )
                else:
                    job_env_dict['interp'] = plotting_dict[line_type]['interp']
                    job_env_dict['fourier_decomp'] = 'False'
                    job_env_dict['wave_num_list'] = ''
                for vx_mask in vx_mask_list:
                    job_env_dict['vx_mask'] = vx_mask
                    njob+=1
                    # Create job file
                    job_filename = os.path.join(job_env_dict['DATA'],
                                                job_env_dict['RUN'],
                                                'metplus_job_scripts',
                                                'job'+str(njob))
                    job_file = open(job_filename, 'w')
                    job_file.write('#!/bin/sh\n')
                    job_file.write('set -x\n')
                    job_file.write('\n')
                    # Write environment variables
                    for name, value in job_env_dict.items():
                        job_file.write('export '+name+'="'+value+'"\n')
                    job_file.write('\n')
                    # Write METplus commands
                    job_file.write(
                        'python '
                        +os.path.join(job_env_dict['USHevs'],
                                      'seasonal',
                                      'prune_seasonal_stat_files.py\n')
                    )
                    job_file.write('\n')
                    metplus_conf = os.path.join(
                        plot_conf_dir, 'nmodels'+str(nmodels)+'.conf'
                    )
                    job_file.write(
                        run_metplus+' -c '+machine_conf+' -c '+metplus_conf
                        +'\n'
                    )
                    job_file.write('\n')
                    line_type_var_name_vx_mask_img_dir = os.path.join(
                        job_env_dict['DATA'], job_env_dict['RUN'],
                        'metplus_output',
                        'plot_by_'+job_env_dict['plot_by'], 'make_plots',
                        line_type+'_'+var_name+'_'+vx_mask, case,
                        case_type, 'images'
                    )
                    main_img_dir = os.path.join(
                        job_env_dict['DATA'], job_env_dict['RUN'],
                        'metplus_output', 'images'
                    )
                    job_file.write(
                        'nimgs=$(ls '+line_type_var_name_vx_mask_img_dir
                        +'/* |wc -l)\n'
                    )
                    job_file.write('if [ $nimgs -ne 0 ]; then\n')
                    job_file.write(
                         '    ln -sf '+line_type_var_name_vx_mask_img_dir
                         +'/* '+main_img_dir+'/.\n'
                    )
                    job_file.write('fi')
                    job_file.close()

def create_job_scripts_tropcyc(start_date_dt, end_date_dt, case, case_abbrev,
                               tc_list, run_metplus, machine_conf,
                               conf_dir):
    """! Writes out individual job scripts based on requested tropical
         cyclone verification

         Args:
             start_date_dt  - datetime object of the verification start
                              date
             end_date_dt    - datetime object of the verification end
                              date
             case           - string of the verification use case
             case_abbrev    - string of case abbrevation
             tc_list        - list of strings of the basin_year_name
             run_metplus    - string of path to run_metplus.py
             machine_conf   - string of path to machine METplus conf
             conf_dir       - string of path to base METplus conf directory

         Returns:
    """
    tc_dict = get_tc_info.get_tc_dict()
    METplus_process = os.environ['METplus_'+case_abbrev+'_process']
    if METplus_process == 'tc_pairs':
        njob = 0
    elif METplus_process == 'tc_stat':
        npoe = int(os.environ['ncount_poe'])
        njob = int(os.environ['ncount_job'])
    # Initialize environment variable job dictionary
    job_env_dict = init_env_dict()
    # Set important METplus paths
    make_met_data_conf_dir = os.path.join(conf_dir, case, 'stats')
    gather_conf_dir = os.path.join(conf_dir, case, 'stats')
    # Set up model environment variables in dictionary
    model_list = os.environ['model_list'].split(' ')
    model_atcf_name_list = (
        os.environ[case_abbrev+'_model_atcf_name_list'].split(' ')
    )
    model_plot_name_list = (
        os.environ[case_abbrev+'_model_plot_name_list'].split(' ')
    )
    nmodels = len(model_list)
    if nmodels > 8:
        print("ERROR: Too many models listed in model_list ("
              +str(nmodels)+"), current maximum is 8")
        sys.exit(1)
    # Other jobs scripts
    stat_list = os.environ[case_abbrev+'_stat_list'].split(' ')
    storm_level_list = os.environ[case_abbrev+'_storm_level_list'].split(' ')
    model_tmp_atcf_name_list = []
    for model in model_list:
        model_idx = model_list.index(model)
        model_num = model_idx + 1
        model_atcf_name = model_atcf_name_list[model_idx]
        model_tmp_atcf_name_list.append('M'+str(model_num).zfill(3))
    if METplus_process == 'tc_stat':
        job_env_dict['START_DATE'] = start_date_dt.strftime('%Y%m%d')
        job_env_dict['END_DATE'] = end_date_dt.strftime('%Y%m%d')
        job_env_dict['fhr_list'] = (
            os.environ[case_abbrev+'_fhr_list'].replace(' ','')
        )
        job_env_dict['init_hour_list'] = (
            os.environ[case_abbrev+'_init_hr_list'].replace(' ','')
        )
        job_env_dict['valid_hour_list'] = (
            os.environ[case_abbrev+'_valid_hr_list'].replace(' ','')
        )
        job_env_dict['model_list'] = ', '.join(model_list)
        job_env_dict['model_atcf_name_list'] = ', '.join(model_atcf_name_list)
        job_env_dict['model_tmp_atcf_name_list'] = ', '.join(
            model_tmp_atcf_name_list
        )
        job_env_dict['model_plot_name_list'] = ', '.join(model_plot_name_list)
        job_env_dict['stat_list'] = ','.join(stat_list)
        job_env_dict['storm_level_list'] = ','.join(storm_level_list)
    basin_list = []
    # Set up tropical cyclone environment variables in dictionary
    for tc in tc_list:
        basin = tc.split('_')[0]
        year = tc.split('_')[1]
        name = tc.split('_')[2]
        if tc == 'WP_2018_HECTOR':
            basin = 'EP'
        if basin not in basin_list:
            basin_list.append(basin)
        tc_id =  tc_dict[tc]
        bdeck_file = os.path.join(job_env_dict['DATA'],
                                  job_env_dict['RUN'], 'data', 'bdeck',
                                  'b'+tc_id+'.dat')
        if not os.path.exists(bdeck_file):
            continue
        tc_start_date, tc_end_date = (
            get_tc_info.get_tc_dates(bdeck_file)
        )
        job_env_dict['TC_START_DATE'] = tc_start_date
        job_env_dict['TC_END_DATE'] = tc_end_date
        job_env_dict['tc'] = tc
        job_env_dict['basin'] = basin
        job_env_dict['year'] = year
        job_env_dict['name'] = name
        job_env_dict['tc_id'] = tc_id.upper()
        job_env_dict['tc_num'] = tc_id[2:4]
        # Write job scripts for METplus process
        if METplus_process == 'tc_pairs':
            for model in model_list:
                job_env_dict['model'] = model
                model_idx = model_list.index(model)
                job_env_dict['model_tmp_atcf_name'] = (
                    model_tmp_atcf_name_list[model_idx]
                )
                # Create job file
                njob+=1
                job_filename = os.path.join(job_env_dict['DATA'],
                                            job_env_dict['RUN'],
                                            'metplus_job_scripts',
                                            'job'+str(njob))
                job_file = open(job_filename, 'w')
                job_file.write('#!/bin/sh\n')
                job_file.write('set -x\n')
                job_file.write('\n')
                # Write environment variables
                for name, value in job_env_dict.items():
                    job_file.write('export '+name+'="'+value+'"\n')
                job_file.write('\n')
                # Write METplus commands
                metplus_conf = os.path.join(make_met_data_conf_dir, 'tc.conf')
                job_file.write(run_metplus+' -c '+machine_conf+' '
                               +'-c '+metplus_conf)
                job_file.close()
        elif METplus_process == 'tc_stat':
            # Create job file
            njob+=1
            job_filename = os.path.join(job_env_dict['DATA'],
                                        job_env_dict['RUN'],
                                        'metplus_job_scripts',
                                        'job'+str(njob))
            job_file = open(job_filename, 'w')
            job_file.write('#!/bin/sh\n')
            job_file.write('set -x\n')
            job_file.write('\n')
            # Write environment variables
            for name, value in job_env_dict.items():
                job_file.write('export '+name+'="'+value+'"\n')
            job_file.write('\n')
            # Write METplus commands
            metplus_conf = os.path.join(gather_conf_dir, 'tc.conf')
            job_file.write(run_metplus+' -c '+machine_conf+' '
                           +'-c '+metplus_conf+'\n')
            job_file.write('\n')
            job_file.write(
                'python '
                +os.path.join(job_env_dict['USHevs'],
                                           'seasonal',
                                           'plot_tropcyc_lead_average.py')
                +'\n'
            )
            job_file.write('\n')
            tc_img_dir = os.path.join(
                job_env_dict['DATA'], job_env_dict['RUN'], 'metplus_output',
                'plot', tc, 'images'
            )
            main_img_dir = os.path.join(
                job_env_dict['DATA'], job_env_dict['RUN'], 'metplus_output',
                'images'
            )
            job_file.write('nimgs=$(ls '+tc_img_dir+'/* |wc -l)\n')
            job_file.write('if [ $nimgs -ne 0 ]; then\n')
            job_file.write('    ln -sf '+tc_img_dir+'/* '+main_img_dir+'/.\n')
            job_file.write('fi')
            job_file.close()
    # Write basin mean job scripts
    if METplus_process == 'tc_stat':
        for del_key in ['TC_START_DATE', 'TC_END_DATE', 'tc', 'basin',
                        'year', 'name', 'tc_id', 'tc_num']:
            if del_key in list(job_env_dict.keys()):
                del job_env_dict[del_key]
        for basin in basin_list:
            job_env_dict['basin'] = basin
            # Create job file
            njob+=1
            job_filename = os.path.join(job_env_dict['DATA'],
                                        job_env_dict['RUN'],
                                        'metplus_job_scripts',
                                        'job'+str(njob))
            job_file = open(job_filename, 'w')
            job_file.write('#!/bin/sh\n')
            job_file.write('set -x\n')
            job_file.write('\n')
            # Write environment variables
            for name, value in job_env_dict.items():
                job_file.write('export '+name+'="'+value+'"\n')
            job_file.write('\n')
            # Write METplus commands
            metplus_conf = os.path.join(gather_conf_dir, 'basin.conf')
            job_file.write(
                run_metplus+' -c '+machine_conf+' -c '+metplus_conf+'\n'
            )
            job_file.write('\n')
            job_file.write(
                'python '
                +os.path.join(job_env_dict['USHevs'],
                                           'seasonal',
                                           'plot_tropcyc_lead_average.py')
                +'\n'
            )
            job_file.write('\n')
            basin_img_dir = os.path.join(
                job_env_dict['DATA'], job_env_dict['RUN'], 'metplus_output',
                'plot', basin, 'images'
            )
            main_img_dir = os.path.join(
                job_env_dict['DATA'], job_env_dict['RUN'], 'metplus_output',
                'images'
            )
            job_file.write('nimgs=$(ls '+basin_img_dir+'/* |wc -l)\n')
            job_file.write('if [ $nimgs -ne 0 ]; then\n')
            job_file.write('    ln -sf '+basin_img_dir+'/* '+main_img_dir+'/.\n')
            job_file.write('fi')
            job_file.close()


def create_job_scripts_maps(start_date_dt, end_date_dt, case, case_abbrev,
                            case_type_list, run_metplus, machine_conf,
                            conf_dir):
    """! Writes out individual job scripts based on requested verification
         for maps2d or mapdsda RUN

         Args:
             start_date_dt  - datetime object of the verification start
                              date
             end_date_dt    - datetime object of the verification end
                              date
             case           - string of the verification use case
             case_abbrev    - string of case abbrevation
             case_type_list - list of strings of the types of the
                              verification use case
             run_metplus    - string of path to run_metplus.py
             machine_conf   - string of path to machine METplus conf
             conf_dir       - string of path to base METplus conf directory

         Returns:
    """
    # Set up plotting information dictionary
    plotting_case_case_type_dict = {
        'maps2d_model2model': {
            'preslevs': {'TMP': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                 '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                 '5hPa', '1hPa'],
                         'HGT': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                 '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                 '5hPa', '1hPa'],
                         'UGRD': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa'],
                         'VGRD': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa'],
                         'VVEL': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa'],
                         'RH': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                '5hPa', '1hPa'],
                         'CLWMR': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                   '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                   '5hPa', '1hPa'],
                         'O3MR': ['1000hPa', '850hPa', '700hPa', '500hPa',
                                  '200hPa', '100hPa', '70hPa', '50hPa', '10hPa',
                                  '5hPa', '1hPa']},
            'sfc': {'TMP': ['2mAGL', 'sfc'],
                    'TMAX': ['2mAGL_range6hr'],
                    'TMIN': ['2mAGL_range6hr'],
                    'DPT': ['2mAGL'],
                    'RH': ['2mAGL'],
                    'SPFH': ['2mAGL'],
                    'UGRD': ['10mAGL'],
                    'VGRD': ['10mAGL'],
                    'GUST': ['sfc'],
                    'PRES': ['sfc'],
                    'MSLET': ['msl'],
                    'PRMSL': ['msl'],
                    'LFTX': ['sfc'],
                    '4LFTX': ['sfc'],
                    'VIS': ['sfc'],
                    'HGT': ['sfc'],
                    'HINDEX': ['sfc'],
                    'ICEC': ['sfc'],
                    'U-GWD': ['sfc_avg6hr'],
                    'V-GWD': ['sfc_avg6hr'],
                    'UFLX': ['sfc_avg6hr'],
                    'VFLX': ['sfc_avg6hr'],
                    'ALBDO': ['sfc_avg6hr'],
                    'LHTFL': ['sfc_avg6hr'],
                    'SHTFL': ['sfc_avg6hr'],
                    'GFLUX': ['sfc_avg6hr']},
            'totcol': {'PWAT': ['column'],
                       'CWAT': ['column'],
                       'TOZNE': ['column'],
                       'CWORK': ['column_avg6hr'],
                       'RH': ['column']},
            'precip': {'APCP': ['sfc_accum6hr'],
                       'ACPCP': ['sfc_accum6hr'],
                       'SNOD': ['sfc'],
                       'WEASD': ['sfc'],
                       'WATR': ['sfc_accum6hr'],
                       'PRATE': ['sfc_avg6hr'],
                       'CRAIN': ['sfc_avg6hr'],
                       'CSNOW': ['sfc_avg6hr'],
                       'CICEP': ['sfc_avg6hr'],
                       'CFRZR': ['sfc_avg6hr']},
            'cloudsrad': {'DLWRF': ['sfc_avg6hr'],
                          'ULWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'DSWRF': ['sfc_avg6hr'],
                          'USWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'ALBDO': ['sfc_avg6hr'],
                          'SUNSD': ['sfc'],
                          'TCDC': ['column_avg6hr', 'pbl_avg6hr', 'low_avg6hr',
                                   'mid_avg6hr', 'high_avg6hr', 'convective'],
                          'PRES': ['lowcloudbase_avg6hr',
                                   'midcloudbase_avg6hr',
                                   'highcloudbase_avg6hr',
                                   'convectivecloudbase',
                                   'lowcloudtop_avg6hr', 'midcloudtop_avg6hr',
                                   'highcloudtop_avg6hr',
                                   'convectivecloudtop'],
                          'TMP': ['lowcloudtop_avg6hr', 'midcloudtop_avg6hr',
                                  'highcloudtop_avg6hr'],
                          'CWAT': ['column'],
                          'CWORK': ['column_avg6hr']},
            'capecin': {'CAPE': ['sfc'],
                        'CIN': ['sfc']},
            'pbl': {'HPBL': ['sfc'],
                    'VRATE': ['pbl'],
                    'UGRD': ['pbl'],
                    'VGRD': ['pbl'],
                    'TCDC': ['pbl_avg6hr']},
            'groundsoil': {'TMP': ['sfc'],
                           'TSOIL': ['0-10cmUGL', '10-40cmUGL',
                                     '40-100cmUGL', '100-200cmUGL'],
                           'SOILW': ['0-10cmUGL', '10-40cmUGL',
                                     '40-100cmUGL', '100-200cmUGL'],
                           'LHTFL': ['sfc_avg6hr'],
                           'SHTFL': ['sfc_avg6hr'],
                           'GFLUX': ['sfc_avg6hr'],
                           'WATR': ['sfc_accum6hr'],
                           'PEVPR': ['sfc'],
                           'FLDCP': ['sfc'],
                           'WILT': ['sfc']},
            'tropopause': {'HGT': ['tropopause'],
                           'TMP': ['tropopause'],
                           'PRES': ['tropopause'],
                           'UGRD': ['tropopause'],
                           'VGRD': ['tropopause'],
                           'VWSH': ['tropopause'],
                           'ICAHT': ['tropopause']},
            'sigma0995': {'TMP': ['0.995sigma'],
                          'POT': ['0.995sigma'],
                          'UGRD': ['0.995sigma'],
                          'VGRD': ['0.995sigma'],
                          'VVEL': ['0.995sigma'],
                          'RH': ['0.995sigma']},
            'maxwindlev': {'TMP': ['maxwindlev'],
                           'PRES': ['maxwindlev'],
                           'HGT': ['maxwindlev'],
                           'UGRD': ['maxwindlev'],
                           'VGRD': ['maxwindlev'],
                           'ICAHT': ['maxwindlev']},
            'highesttropfrzlev': {'HGT': ['highesttropfrzlev'],
                                  'RH': ['highesttropfrzlev']}
        },
        'maps2d_model2obs': {
            'cloudsrad': {'DLWRF': ['sfc_avg6hr'],
                          'ULWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'DSWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'USWRF': ['sfc_avg6hr', 'toa_avg6hr'],
                          'TCDC': ['column_avg6hr', 'low_avg6hr',
                                   'mid_avg6hr', 'high_avg6hr']},
            'sfc': {'TMP': ['2mAGL']},
            'totcol': {'PWAT': ['column'],
                       'CWAT': ['column']},
            'precip': {'PRATE': ['sfc_avg6hr']}
        },
        'mapsda_gdas':{
            'preslevs':{'TMP': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                '500hPa', '200hPa', '100hPa', '70hPa',
                                '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                                '3hPa', '2hPa', '1hPa'],
                        'UGRD': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                 '500hPa', '200hPa', '100hPa', '70hPa',
                                 '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                                 '3hPa', '2hPa', '1hPa'],
                        'VGRD': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                 '500hPa', '200hPa', '100hPa', '70hPa',
                                 '50hPa', '30hPa', '10hPa', '7hPa',
                                 '5hPa', '3hPa', '2hPa', '1hPa'],
                        'RH': ['1000hPa', '925hPa', '800hPa', '700hPa',
                               '500hPa', '200hPa', '100hPa', '70hPa',
                               '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                               '3hPa', '2hPa', '1hPa'],
                        'CLWMR': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                  '500hPa', '200hPa', '100hPa', '70hPa',
                                  '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                                  '3hPa', '2hPa', '1hPa'],
                        'O3MR': ['1000hPa', '925hPa', '800hPa', '700hPa',
                                 '500hPa', '200hPa', '100hPa', '70hPa',
                                 '50hPa', '30hPa', '10hPa', '7hPa', '5hPa',
                                 '3hPa', '2hPa', '1hPa']},
            'sfc': {'MSLET': ['msl']}
        },
        'mapsda_ens': {
            'preslevs': {'TMP': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa'],
                        'UGRD': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa'],
                        'VGRD': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa'],
                        'SPFH': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa'],
                        'CLWMR': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                  '10hPa', '1hPa'],
                        'O3MR': ['1000hPa', '850hPa', '500hPa', '250hPa',
                                 '10hPa', '1hPa']},
            'sfc': {'PRES': ['sfc']}
        }
    }
    maps2d_model2obs_obs_var_name = {
        'DLWRF': ['lw_sfc_down'],
        'ULWRF': ['lw_sfc_up', 'lw_toa_up'],
        'DSWRF': ['sw_sfc_down', 'sw_toa_down'],
        'USWRF': ['sw_sfc_up', 'sw_toa_up'],
        'TCDC': ['cldt', 'cldl', 'cldm', 'cldh'],
        'TMP': ['air'],
        'PWAT': ['tpw'],
        'CWAT': ['clwp'],
        'PRATE': ['precip']
    }
    njob = 0
    # Initialize environment variable job dictionary
    job_env_dict = init_env_dict()
    job_env_dict['START_DATE'] = start_date_dt.strftime('%Y%m%d')
    job_env_dict['END_DATE'] = end_date_dt.strftime('%Y%m%d')
    job_env_dict['latlon_area'] = os.environ[case_abbrev+'_latlon_area']
    job_env_dict['plot_diff'] = os.environ[case_abbrev+'_plot_diff']
    # Set important METplus paths
    case_conf_dir = os.path.join(conf_dir, case)
    # Set up model environment variables in dictionary
    model_list = os.environ['model_list'].split(' ')
    model_plot_name_list = os.environ[
        case_abbrev+'_model_plot_name_list'
    ].split(' ')
    nmodels = len(model_list)
    for model in model_list:
        model_idx = model_list.index(model)
        model_num = model_idx + 1
        job_env_dict['model'+str(model_num)] = model
        job_env_dict['model'+str(model_num)+'_plot_name'] = (
            model_plot_name_list[model_idx]
        )
    # Set up case_type environment variables in dictionary
    for case_type in case_type_list:
        case_abbrev_type = case_abbrev+'_'+case_type
        case_type_env_list = ['make_met_data_by', 'regrid_to_grid',
                              'hour_beg', 'hour_end', 'hour_inc']
        for case_type_env in case_type_env_list:
            job_env_dict[case_type_env] = (
                os.environ[case_abbrev_type+'_'+case_type_env]
            )
        job_env_dict['plot_by'] = job_env_dict['make_met_data_by']
        job_env_dict['RUN_type'] = case_type
        # Check we have enough room on subplots before continuing
        if case == 'maps2d':
            if case_type == 'model2model':
                if os.environ[case_abbrev_type+'_forecast_anl_diff'] == 'YES':
                    nsubplots = nmodels * 2
                    error_msg = (
                        '(number of models in model_list ,'+str(nmodels)+', '
                        +'times 2, for '+case_abbrev_type
                        +'_forecast_anl_diff = YES)'
                    )
                else:
                    nsubplots = nmodels
                    error_msg = (
                        '(number of models in model_list ,'+str(nmodels)+')'
                    )
            elif case_type == 'model2obs':
                nsubplots = nmodels + 1
                error_msg = (
                    '(number of models in model_list ,'+str(nmodels)+', '
                    +'plus 1, for observations)'
                )
        elif case == 'mapsda':
            if case_type == 'gdas':
                nsubplots = nmodels + 1
                error_msg = (
                    '(number of models in model_list ,'+str(nmodels)+', '
                    +'plus 1, for model1 analysis)'
                )
            elif case_type == 'ens':
                nsubplots = nmodels
                error_msg = (
                    '(number of models in model_list ,'+str(nmodels)+')'
                )
        if nsubplots > 8:
            print("ERROR: Requested verification results in "
                  +str(nsubplots)+" subplots "+error_msg
                  +", current maximum is 8")
            sys.exit(1)
        # Set some specific case_type environment variables in own dictionary
        case_type_env_dict = {}
        if case == 'maps2d':
            if case_type == 'model2model':
                case_type_env_dict['forecast_anl_diff'] = (
                    os.environ[case_abbrev_type+'_forecast_anl_diff']
                )
            elif case_type == 'model2obs':
                case_type_env_dict['use_ceres'] = (
                    os.environ[case_abbrev_type+'_use_ceres']
                )
                case_type_env_dict['use_monthly_mean'] = (
                    os.environ[case_abbrev_type+'_use_monthly_mean']
                )
        # Set forecasting plotting list
        if case == 'maps2d':
            forecast_to_plot_list = (
                os.environ[case_abbrev_type+'_forecast_to_plot_list'] \
                .split(' ')
            )
        elif case == 'mapsda':
            forecast_to_plot_list = (
                ('fhr'+os.environ[case_abbrev_type+'_guess_hour']).split(' ')
            )
        # Set up plotting environment variables in dictionary
        plotting_dict = plotting_case_case_type_dict[case+'_'+case_type]
        for var_group in list(plotting_dict.keys()):
            var_group_img_dir = os.path.join(
                job_env_dict['DATA'], job_env_dict['RUN'], 'metplus_output',
                'plot_by_'+job_env_dict['plot_by'], case_type,
                var_group, 'imgs'
            )
            if not os.path.exists(var_group_img_dir):
                os.makedirs(var_group_img_dir)
            for model in model_list:
                var_group_name_make_met_model_dir = os.path.join(
                    job_env_dict['DATA'], job_env_dict['RUN'],
                    'metplus_output',
                    'make_met_data_by_'+job_env_dict['make_met_data_by'],
                    'series_analysis', case_type, var_group, model
                )
                if not os.path.exists(var_group_name_make_met_model_dir):
                    os.makedirs(var_group_name_make_met_model_dir)
            job_env_dict['var_group'] = var_group
            for var_name, var_levels in plotting_dict[var_group].items():
                job_env_dict['var_name'] = var_name
                job_env_dict['var_levels'] = (
                    ' '.join(var_levels).replace(' ', ', ')
                )
                for model in model_list:
                    model_num = (model_list.index(model)) + 1
                    if case == 'maps2d':
                        if case_type == 'model2model':
                            if case_type_env_dict['forecast_anl_diff'] \
                                    == 'YES':
                                obtype = model+'_anl'
                            else:
                                obtype = model
                        elif case_type == 'model2obs':
                            if var_group in ['cloudsrad', 'totcol']:
                                if case_type_env_dict['use_ceres'] == 'YES':
                                    obtype = 'ceres'
                                else:
                                    if var_name == 'TCDC':
                                        obtype = 'rad_isccp'
                                    elif var_name == 'CWAT':
                                        obtype = 'clwp'
                                    elif var_name == 'PWAT':
                                        obtype = 'nvap'
                                    elif var_name in ['DLWRF', 'ULWRF',
                                                      'DSWRF', 'USWRF']:
                                        obtype = 'rad_srb2'
                            elif var_group == 'sfc':
                                obtype = 'ghcn_cams'
                            elif var_group == 'precip':
                                obtype = 'gpcp'
                            case_type_env_dict['obtype_var_name'] = ' '.join(
                                maps2d_model2obs_obs_var_name[var_name]
                            ).replace(' ', ', ')
                    elif case == 'mapsda':
                        if case_type == 'gdas':
                            obtype = model+'_anl'
                        elif case_type == 'ens':
                            obtype = model
                    job_env_dict['model'+str(model_num)+'_obtype'] = obtype
                for forecast_to_plot in forecast_to_plot_list:
                    job_env_dict['forecast_to_plot'] = forecast_to_plot
                    njob+=1
                    job_env_dict['job_num_id'] = str(njob)
                    # Create job file
                    job_filename = os.path.join(job_env_dict['DATA'],
                                                job_env_dict['RUN'],
                                                'metplus_job_scripts',
                                                'job'+str(njob))
                    job_file = open(job_filename, 'w')
                    job_file.write('#!/bin/sh\n')
                    job_file.write('set -x\n')
                    job_file.write('\n')
                    # Write environment variables
                    for name, value in job_env_dict.items():
                        job_file.write('export '+name+'="'+value+'"\n')
                    for name, value in case_type_env_dict.items():
                        job_file.write('export '+name+'="'+value+'"\n')
                    job_file.write('\n')
                    # Write METplus commands
                    if case == 'maps2d' \
                            or (case == 'mapsda' and case_type == 'gdas'):
                        job_file.write(
                            'python '
                            +os.path.join(
                                job_env_dict['USHevs'],
                               'seasonal', 
                               'create_MET_series_analysis_seasonal_jobs.py\n'
                            )
                        )
                        for model in model_list:
                            job_file.write(os.path.join(DATA, RUN,
                                                        'metplus_job_scripts',
                                                        'series_analysis_'
                                                        +'job'+str(njob)+'_'
                                                        +model+'.sh')+'\n')
                        job_file.write('\n')
                    if os.environ['machine'] == 'ORION':
                        job_file.write('echo "WARNING: Cartopy not installed '
                                       +'on Orion, cannot create plots."\n')
                    else:
                        plotting_script_list = []
                        plotting_script_list.append(
                            'plot_'+case+'_lat_lon_errors.py'
                        )
                        if var_group == 'preslevs':
                            plotting_script_list.append(
                                'plot_'+case+'_zonal_mean_errors.py'
                            )
                        for plotting_script in plotting_script_list:
                            job_file.write(
                                'python '
                                 +os.path.join(job_env_dict['USHevs'],
                                               'subseasonal',
                                                plotting_script)
                                +'\n'
                            )
                        job_file.write('\n')
                        main_img_dir = os.path.join(
                            job_env_dict['DATA'], job_env_dict['RUN'],
                            'metplus_output', 'images'
                        )
                        job_file.write('nimgs=$(ls '+var_group_img_dir
                                       +'/* |wc -l)\n')
                        job_file.write('if [ $nimgs -ne 0 ]; then\n')
                        job_file.write('    ln -sf '+var_group_img_dir
                                       +'/* '+main_img_dir+'/.\n')
                        job_file.write('fi')
                    job_file.close()

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
machine = os.environ['machine']
MPMD = os.environ['MPMD']
nproc = int(os.environ['nproc'])
start_date = os.environ['start_date']
end_date = os.environ['end_date']
RUN_abbrev = os.environ['RUN_abbrev']

# Set up date information
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                          int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                          int(end_date[6:]))
# Set important METplus paths
USHMETplus_run_metplus = os.path.join(
    os.environ['USHMETplus'], 'run_metplus.py'
)
PARMevs_machine_conf = os.path.join(
    os.environ['PARMevs'], 'metplus_config', 'machine.conf'
)
PARMevs_METplus_conf_dir = os.path.join(
    os.environ['PARMevs'], 'metplus_config',
    'seasonal'
)

# Run job creation function
if RUN in ['grid2grid_stats', 'grid2obs_stats', 'precip_stats',
           'satellite_stats']:
    create_job_scripts_stats(
        sdate, edate, RUN.split('_')[0], RUN_abbrev,
        os.environ[RUN_abbrev+'_type_list'].split(' '),
        USHMETplus_run_metplus, PARMevs_machine_conf,
        PARMevs_METplus_conf_dir
    )
elif RUN in ['grid2grid_plots', 'grid2obs_plots', 'precip_plots',
             'satellite_plots']:
    create_job_scripts_plots(
        sdate, edate, RUN.split('_')[0], RUN_abbrev,
        os.environ[RUN_abbrev+'_type_list'].split(' '),
        USHMETplus_run_metplus, PARMevs_machine_conf,
        PARMevs_METplus_conf_dir
    )
elif RUN in ['tropcyc']:
    import get_tc_info
    tc_dict = get_tc_info.get_tc_dict()
    RUN_abbrev_tc_list = []
    RUN_abbrev_config_storm_list = (
        os.environ[RUN_abbrev+'_storm_list'].split(' ')
    )
    for config_storm in RUN_abbrev_config_storm_list:
        config_storm_basin = config_storm.split('_')[0]
        config_storm_year = config_storm.split('_')[1]
        config_storm_name = config_storm.split('_')[2]
        if config_storm_name == 'ALLNAMED':
            for byn in list(tc_dict.keys()):
                if config_storm_basin+'_'+config_storm_year in byn:
                    RUN_abbrev_tc_list.append(byn)
        else:
            RUN_abbrev_tc_list.append(config_storm)
    create_job_scripts_tropcyc(
        sdate, edate, RUN, RUN_abbrev, RUN_abbrev_tc_list,
        USHMETplus_run_metplus, PARMevs_machine_conf,
        PARMevs_METplus_conf_dir
    )
elif RUN in ['maps2d', 'mapsda']:
    create_job_scripts_maps(
        sdate, edate, RUN, RUN_abbrev,
        os.environ[RUN_abbrev+'_type_list'].split(' '),
        USHMETplus_run_metplus, PARMevs_machine_conf,
        PARMevs_METplus_conf_dir
    )

# If running MPMD, create POE scripts
if MPMD == 'YES':
    job_files = glob.glob(
        os.path.join(DATA, RUN, 'metplus_job_scripts', 'job*')
    )
    njob_files = len(job_files)
    if njob_files == 0:
        print("ERROR: No job files created in "
              +os.path.join(DATA, RUN, 'metplus_job_scripts'))
        sys.exit(1)
    if RUN == 'tropcyc':
        METplus_tropcyc_process = os.environ['METplus_tropcyc_process']
        if METplus_tropcyc_process == 'tc_pairs':
            njob, iproc = 1, 0
            node = 1
        else:
            njob_from_tc_pairs = int(os.environ['ncount_job'])
            npoe_from_tc_pairs = int(os.environ['ncount_poe'])
            njob = njob_from_tc_pairs + 1
            iproc = 0
            node = npoe_from_tc_pairs + 1
    else:
        njob, iproc = 1, 0
        node = 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        poe_filename = os.path.join(DATA, RUN, 'metplus_job_scripts',
                                        'poe_jobs'+str(node))
        if iproc == 0:
            poe_file = open(poe_filename, 'w')
        iproc+=1
        poe_file.write(
            os.path.join(DATA, RUN, 'metplus_job_scripts', job)+'\n'
        )
        njob+=1
    poe_file.close()
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_file = open(poe_filename, 'a')
    iproc+=1
    while iproc <= nproc:
        poe_file.write(
            '/bin/echo '+str(iproc)+'\n'
        )
        iproc+=1
poe_file.close()

print("END: "+os.path.basename(__file__))
