'''
Program Name: create_METplus_seasonal_output_dirs.py
Contact(s): Shannon Shields
Abstract: This script is run by all scripts in scripts/.
          This creates the base directories and their subdirectories
          for the METplus verification use cases and their types.
'''

import os

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
make_met_data_by = os.environ['make_met_data_by']
plot_by = os.environ['plot_by']
model_list = os.environ['model_list'].split(' ')
RUN_abbrev = os.environ['RUN_abbrev']
if RUN != 'tropcyc':
    RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')

# Create METplus output base directories
metplus_output_dir = os.path.join(DATA, RUN, 'metplus_output')
metplus_job_scripts_dir = os.path.join(DATA, RUN, 'metplus_job_scripts')
os.makedirs(metplus_output_dir, mode=0o755)
os.makedirs(metplus_job_scripts_dir, mode=0o755)

# Build information of METplus output subdirectories to create
metplus_output_subdir_list = [ 'confs', 'logs', 'tmp' ]
if 'plots' in RUN:
    metplus_output_subdir_list.append(
       os.path.join('plot_by_'+plot_by, 'stat_analysis')
    )
    metplus_output_subdir_list.append(
        os.path.join('plot_by_'+plot_by,'make_plots')
    )
    metplus_output_subdir_list.append('images')
    if RUN == 'grid2grid_plots':
        if os.environ[RUN_abbrev+'_make_scorecard'] == 'YES':
            metplus_output_subdir_list.append('scorecard')
elif RUN in ['grid2grid_stats', 'satellite_stats']:
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        gather_by = os.environ[RUN_abbrev_type+'_gather_by']
        for model in model_list:
            metplus_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'grid_stat', RUN_type, model)
            )
            metplus_output_subdir_list.append(
                os.path.join('gather_by_'+gather_by, 'stat_analysis',
                             RUN_type, model)
            )
elif RUN == 'grid2obs_stats':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        gather_by = os.environ[RUN_abbrev_type+'_gather_by']
        if RUN_type in ['upper_air', 'conus_sfc']:
           met_2nc_tool = 'pb2nc'
           obs_file = 'prepbufr'
        elif RUN_type == 'polar_sfc':
           met_2nc_tool = 'ascii2nc'
           obs_file = 'iabp'
        metplus_output_subdir_list.append(
            os.path.join('make_met_data_by_'+make_met_data_by,
                         met_2nc_tool, RUN_type, obs_file)
        )
        for model in model_list:
            metplus_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'point_stat', RUN_type, model)
            )
            metplus_output_subdir_list.append(
                os.path.join('gather_by_'+gather_by, 'stat_analysis',
                             RUN_type, model)
            )
elif RUN == 'precip_stats':
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        gather_by = os.environ[RUN_abbrev_type+'_gather_by']
        for model in model_list:
            metplus_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'pcp_combine', RUN_type, model)
            )
            metplus_output_subdir_list.append(
                os.path.join('make_met_data_by_'+make_met_data_by,
                             'grid_stat', RUN_type, model)
            )
            metplus_output_subdir_list.append(
                os.path.join('gather_by_'+gather_by, 'stat_analysis',
                             RUN_type, model)
            )
elif RUN == 'tropcyc':
    metplus_output_subdir_list.append('images')
    import get_tc_info
    tc_dict = get_tc_info.get_tc_dict()
    RUN_abbrev_tc_list = []
    for config_storm in os.environ[RUN_abbrev+'_storm_list'].split(' '):
        config_storm_basin = config_storm.split('_')[0]
        config_storm_year = config_storm.split('_')[1]
        config_storm_name = config_storm.split('_')[2]
        if config_storm_name == 'ALLNAMED':
            for byn in list(tc_dict.keys()):
                if config_storm_basin+'_'+config_storm_year in byn:
                    RUN_abbrev_tc_list.append(byn)
        else:
            RUN_abbrev_tc_list.append(config_storm)
    for tc in RUN_abbrev_tc_list:
        basin = tc.split('_')[0]
        metplus_output_subdir_list.append(
            os.path.join('gather', 'tc_stat', tc)
        )
        metplus_output_subdir_list.append(
            os.path.join('plot', tc, 'images')
        )
        if (os.path.join('gather', 'tc_stat', basin)
                not in metplus_output_subdir_list):
            metplus_output_subdir_list.append(
                os.path.join('gather', 'tc_stat', basin)
            )
        if (os.path.join('plot', basin, 'imgs')
                not in metplus_output_subdir_list):
            metplus_output_subdir_list.append(
                os.path.join('plot', basin, 'imgs')
            )
        for model in model_list:
            metplus_output_subdir_list.append(
                os.path.join('make_met_data', 'tc_pairs', tc, model)
            )
elif RUN == 'maps2d':
    metplus_output_subdir_list.append('images')
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        make_met_data_by = os.environ[RUN_abbrev_type
                                     +'_make_met_data_by']
        plot_by = make_met_data_by
        metplus_output_subdir_list.append(os.path.join('plot_by_'+plot_by))
        metplus_output_subdir_list.append(
           os.path.join('make_met_data_by_'+make_met_data_by,
                        'series_analysis', RUN_type)
        )
elif RUN == 'mapsda':
    metplus_output_subdir_list.append('images')
    for RUN_type in RUN_type_list:
        RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
        make_met_data_by = os.environ[RUN_abbrev_type
                                      +'_make_met_data_by']
        plot_by = make_met_data_by
        metplus_output_subdir_list.append(os.path.join('plot_by_'+plot_by))
        if type == 'gdas':
            metplus_output_subdir_list.append(
               os.path.join('make_met_data_by_'+make_met_data_by,
                            'series_analysis', RUN_type)
            )

# Create METplus output subdirectories
for subdir in metplus_output_subdir_list:
    metplus_output_subdir = os.path.join(metplus_output_dir, subdir)
    if not os.path.exists(metplus_output_subdir):
        os.makedirs(metplus_output_subdir, mode=0o755)

print("END: "+os.path.basename(__file__))
