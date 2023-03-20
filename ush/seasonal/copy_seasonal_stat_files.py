'''
Program Name: copy_seasonal_stat_files.py
Contact(s): Shannon Shields
Abstract: This script is run by all stat scripts in scripts/seasonal/stats/
          It copies the stat files to the online archive or
          to COMROOT.
'''

import os
import datetime

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
DATA = os.environ['DATA']
RUN = os.environ['RUN']
model_list = os.environ['model_list'].split(' ')
model_stat_dir_list = os.environ['model_stat_dir_list'].split(' ')
start_date = os.environ['start_date']
end_date = os.environ['end_date']
make_met_data_by = os.environ['make_met_data_by']
RUN_abbrev = os.environ['RUN_abbrev']
RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')
SENDCOM = os.environ['SENDCOM']
SENDDBN = os.environ ['SENDDBN']
SENDARCH = os.environ['SENDARCH']

# Set up date information
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                          int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                          int(end_date[6:]))

for RUN_type in RUN_type_list:
    RUN_abbrev_type = RUN_abbrev+'_'+RUN_type
    RUN_abbrev_type_gather_by = os.environ[
        RUN_abbrev_type+'_gather_by'
    ]
    if RUN_abbrev_type_gather_by == 'VALID':
        RUN_abbrev_type_gather_by_hour_list = os.environ[
            RUN_abbrev_type+'_vhr_list'
        ].split(' ')
    elif RUN_abbrev_type_gather_by == 'INIT':
        RUN_abbrev_type_gather_by_hour_list = os.environ[
            RUN_abbrev_type+'_fcyc_list'
        ].split(' ')
    elif RUN_abbrev_type_gather_by ==  'VSDB':
        if RUN in ['grid2grid_stats']:
            RUN_abbrev_type_gather_by_hour_list = os.environ[
                RUN_abbrev_type+'_vhr_list'
            ].split(' ')
        elif RUN in ['grid2obs_stats', 'precip_stats']:
            RUN_abbrev_type_gather_by_hour_list = os.environ[
                RUN_abbrev_type+'_fcyc_list'
            ].split(' ')
    date = sdate
    while date <= edate:
        DATE = date.strftime('%Y%m%d')
        COMIN = os.getenv(
            'COMIN',
            os.path.join(os.environ['OUTPUTROOT'], 'com', os.environ['NET'],
                         os.environ['envir'], RUN+'.'+DATE)
        )
        COMOUT = os.getenv(
            'COMOUT',
            os.path.join(os.environ['OUTPUTROOT'], 'com', os.environ['NET'],
                         os.environ['envir'], RUN+'.'+DATE)
        )
        for model in model_list:
            model_idx = model_list.index(model)
            model_stat_dir = model_stat_dir_list[model_idx]
            for gather_by_hour in RUN_abbrev_type_gather_by_hour_list:
                if RUN in ['grid2grid_stats']:
                    evs_seasonal_file = os.path.join(
                        DATA, RUN, 'metplus_output',
                        'gather_by_'+RUN_abbrev_type_gather_by,
                        'stat_analysis', RUN_type, model,
                        model+'_'+DATE+gather_by_hour+'.stat'
                    )
                elif RUN in ['grid2obs_stats', 'precip_stats']:
                    if RUN_abbrev_type_gather_by == 'VSDB':
                        evs_seasonal_file = os.path.join(
                            DATA, RUN, 'metplus_output',
                            'gather_by_'+RUN_abbrev_type_gather_by,
                            'stat_analysis', RUN_type, model,
                             model+'_'+DATE
                             +os.environ[RUN_abbrev_type+'_valid_hr_beg']
                             +'_'+DATE
                             +os.environ[RUN_abbrev_type+'_valid_hr_end']
                             +'_'+gather_by_hour+'.stat'
                        )
                    else:
                        evs_seasonal_file = os.path.join(
                            DATA, RUN, 'metplus_output',
                            'gather_by_'+RUN_abbrev_type_gather_by,
                            'stat_analysis', RUN_type, model,
                             model+'_'+DATE+gather_by_hour+'.stat'
                        )
                archive_file = os.path.join(
                     model_stat_dir, 'metplus_data',
                     'by_'+RUN_abbrev_type_gather_by,
                     RUN.split('_')[0], RUN_type, gather_by_hour+'Z',
                     model, model+'_'+DATE+'.stat'
                )
                comout_file = os.path.join(
                    COMOUT, model+'_'+RUN.split('_')[0]+'_'+RUN_type
                    +'_'+DATE+'_'+gather_by_hour+'Z_'
                    +RUN_abbrev_type_gather_by+'.stat'
                )
                if os.path.exists(evs_seasonal_file) \
                        and os.path.getsize(evs_seasonal_file):
                    if SENDARCH == 'YES':
                        archive_file_dir = archive_file.rpartition('/')[0]
                        if not os.path.exists(archive_file_dir):
                            os.makedirs(archive_file_dir)
                        print("Copying "+evs_seasonal_file+" to "+archive_file)
                        os.system('cpfs '+evs_seasonal_file+' '+archive_file)
                    if SENDCOM == 'YES':
                        if not os.path.exists(COMOUT):
                            os.makedirs(COMOUT)
                        print("Copying "+evs_seasonal_file+" to "+comout_file)
                        os.system('cpfs '+evs_seasonal_file+' '+comout_file)
                        if SENDDBM == 'YES':
                            os.system(
                                os.getenv('DBNROOT', '')+'/bin/dbn_alert '
                                +'MODEL EVS_SEASONAL '+os.environ['job']+' '
                                +comout_file
                        )
                else:
                    print("**************************************************")
                    print("** WARNING: "+evs_seasonal_file+" "
                          +"was not generated or zero size")
                    print("**************************************************\n")
        date = date + datetime.timedelta(days=1)

print("END: "+os.path.basename(__file__))
