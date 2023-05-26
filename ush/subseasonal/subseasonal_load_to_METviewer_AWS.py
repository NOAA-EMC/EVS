#!/usr/bin/env python3
'''
Program Name: subseasonal_load_to_METviewer_AWS.py
Contact(s): Shannon Shields
Abstract: This is run at the end of all stats scripts
          in scripts/.
          This script loads data to the METviewer AWS
          server.
              1) Create a temporary directory and
                 link the files that are to be
                 loaded
              2) Create XML that will load files
              3) Create database on AWS server
              4) Listing of METviewer databases
'''

import datetime
import os
import subprocess

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
KEEPDATA = os.environ['KEEPDATA']
machine = os.environ['machine']
DATAROOT = os.environ['DATAROOTtmp']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
COMPONENT = os.environ['COMPONENT']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
PARTITION_BATCH = os.environ['PARTITION_BATCH']
model_list = os.environ['model_list'].split(' ')
model_stats_dir_list = os.environ['model_stats_dir_list'].split(' ')
METviewer_AWS_scripts_dir = os.environ['METviewer_AWS_scripts_dir']
mv_database = os.environ[VERIF_CASE_STEP_abbrev+'_mv_database_name']
mv_group = os.environ[VERIF_CASE_STEP_abbrev+'_mv_database_group']
mv_desc = os.environ[VERIF_CASE_STEP_abbrev+'_mv_database_desc']

# Set up date information
sdate = datetime.datetime(int(start_date[0:4]), int(start_date[4:6]),
                          int(start_date[6:]))
edate = datetime.datetime(int(end_date[0:4]), int(end_date[4:6]),
                          int(end_date[6:]))

# Set up walltime
transfer_walltime = '180'
walltime_seconds = datetime.timedelta(minutes=int(transfer_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(transfer_walltime))).time()

# Create METviewer AWS dir
METviewer_AWS_loading_dir = os.path.join(DATA, VERIF_CASE+'_'+STEP,
                                         'METviewer_AWS_loading')
if not os.path.exists(METviewer_AWS_loading_dir):
    os.makedirs(METviewer_AWS_loading_dir, mode=0o755)
    link_file_dir = os.path.join(METviewer_AWS_loading_dir, 'files')
    os.makedirs(link_file_dir, mode=0o755)

# Create load XML
load_xml_file = os.path.join(METviewer_AWS_loading_dir, 
                             'load_'+mv_database+'.xml')
print("Creating load xml "+load_xml_file)
if os.path.exists(load_xml_file):
    os.remove(load_xml_file)
with open(load_xml_file, 'a') as xml:
    xml.write('<load_spec>\n')
    xml.write('  <connection>\n')
    xml.write('    <host>metviewer-dev-2-cluster.cluster-c0bl5kb6fffo.'
              +'us-east-1.rds.amazonaws.com:3306</host>\n')
    xml.write('    <database>'+mv_database+'</database>\n')
    xml.write('    <user>rds_user</user>\n')
    xml.write('    <password>rds_pwd</password>\n')
    xml.write('    <management_system>aurora</management_system>\n')
    xml.write('  </connection>\n')
    xml.write('\n')
    xml.write('  <verbose>true</verbose>\n')
    xml.write('  <insert_size>1</insert_size>\n')
    xml.write('  <mode_header_db_check>true</mode_header_db_check>\n')
    xml.write('  <stat_header_db_check>true</stat_header_db_check>\n')
    xml.write('  <drop_indexes>false</drop_indexes>\n')
    xml.write('  <apply_indexes>false</apply_indexes>\n')
    xml.write('  <load_stat>true</load_stat>\n')
    xml.write('  <load_mode>true</load_mode>\n')
    xml.write('  <load_mpr>true</load_mpr>\n')
    xml.write('  <load_orank>true</load_orank>\n')
    xml.write('  <force_dup_file>false</force_dup_file>\n')
    xml.write('  <group>'+mv_group+'</group>\n')
    xml.write('  <description>'+mv_desc+'</description>\n')
    xml.write('  <load_files>\n')
for model_idx in range(len(model_list)):
    model = model_list[model_idx]
    model_stats_dir = model_stats_dir_list[model_idx]
    #sdate = sdate - datetime.timedelta(days=28)
    date = sdate
    while date <= edate:
        DATE = date.strftime('%Y%m%d')
        arc_stat_file = os.path.join(
            model_stats_dir,
            'evs.stats.'+model+'.'+RUN+'.'+VERIF_CASE+'.v'
            +DATE+'.stat'
        )
        METviewer_AWS_loading_file = os.path.join(
            link_file_dir,
            model+'_'+RUN+'_'+VERIF_CASE+'_v'
            +DATE+'.stat'
        )
        if os.path.exists(arc_stat_file):
            print("Linking "+arc_stat_file+" to "+METviewer_AWS_loading_file)
            os.symlink(arc_stat_file, METviewer_AWS_loading_file)
            with open(load_xml_file, 'a') as xml:
                xml.write('    <file>/base_dir/'
                          +METviewer_AWS_loading_file.rpartition('/')[2]
                          +'</file>\n')
        date = date + datetime.timedelta(days=1)
with open(load_xml_file, 'a') as xml:
    xml.write('  </load_files>\n')
    xml.write('\n')
    xml.write('</load_spec>')

# Create job card file for:
#   Create database if needed and load data
#   mv_create_db_on_aws.sh agruments:
#      1 - username
#      2 - database name
#   mv_load_to_aws.sh agruments:
#      1 - username
#      2 - base dir
#      3 - XML file
#      4 (opt) - sub dir
AWS_job_filename = os.path.join(METviewer_AWS_loading_dir,
                                NET+'_'+COMPONENT+'_'+RUN+'_'
                                +VERIF_CASE+'_'+STEP
                                +'_load_to_METviewer_AWS.sh')
AWS_job_output = os.path.join(METviewer_AWS_loading_dir,
                              NET+'_'+COMPONENT+'_'+RUN+'_'
                              +VERIF_CASE+'_'+STEP
                              +'_load_to_METviewer_AWS.log')
AWS_job_name = NET+'_'+COMPONENT+'_'+RUN+'_'+VERIF_CASE+'_'+STEP+'_METviewer'
with open(AWS_job_filename, 'a') as AWS_job_file:
    if machine == 'WCOSS2':
        AWS_job_file.write('#PBS -q '+QUEUESERV+'\n')
        AWS_job_file.write('#PBS -A '+ACCOUNT+'\n')
        AWS_job_file.write('#PBS -N '+AWS_job_name+'\n')
        AWS_job_file.write('#PBS -o '+AWS_job_output+'\n')
        AWS_job_file.write('#PBS -e '+AWS_job_output+'\n')
        AWS_job_file.write('#PBS -l walltime='+walltime.strftime('%H:%M:%S')
                           +'\n')
        AWS_job_file.write('#PBS -l debug=true\n')
        AWS_job_file.write('#PBS -l select=1:ncpus=1'+'\n')
        AWS_job_file.write('\n')
        AWS_job_file.write('cd $PBS_O_WORKDIR\n')
    elif machine == 'HERA':
        AWS_job_file.write('#SBATCH --qos='+QUEUESERV+'\n')
        AWS_job_file.write('#SBATCH --account='+ACCOUNT+'\n')
        AWS_job_file.write('#SBATCH --job-name='+AWS_job_name+'\n')
        AWS_job_file.write('#SBATCH --output='+AWS_job_output+'\n')
        AWS_job_file.write('#SBATCH --nodes=1\n')
        AWS_job_file.write('#SBATCH --ntasks-per-node=1\n')
        AWS_job_file.write('#SBATCH --time='+walltime.strftime('%H:%M:%S')
                           +'\n')
    AWS_job_file.write('\n')
    AWS_job_file.write('echo "Creating database on METviewer AWS using '
                       +os.path.join(METviewer_AWS_scripts_dir,
                                     'mv_create_db_on_aws.sh')
                       +'"\n')
    AWS_job_file.write(
        os.path.join(METviewer_AWS_scripts_dir,
                     'mv_create_db_on_aws.sh')+' '
        +os.environ['USER'].lower()+' '
        +mv_database+'\n'
    )
    AWS_job_file.write('echo "Loading data to METviewer AWS using '
                       +os.path.join(METviewer_AWS_scripts_dir,
                                     'mv_load_to_aws.sh')
                       +'"\n')
    AWS_job_file.write(
        os.path.join(METviewer_AWS_scripts_dir, 'mv_load_to_aws.sh')+' '
        +os.environ['USER'].lower()+' '
        +link_file_dir+' '
        +load_xml_file+'\n'
    )
    AWS_job_file.write('echo "Check METviewer AWS database list using '
                       +os.path.join(METviewer_AWS_scripts_dir,
                                     'mv_db_size_on_aws.sh')
                      +'"\n')
    AWS_job_file.write(
        os.path.join(METviewer_AWS_scripts_dir, 'mv_db_size_on_aws.sh')+' '
        +os.environ['USER'].lower()
    )
    if KEEPDATA == 'NO':
        AWS_job_file.write('\n')
        AWS_job_file.write('echo "Removing DATA dir, KEEPDATA = NO"\n')
        AWS_job_file.write('cd '+DATAROOT+'\n')
        AWS_job_file.write('rm -rf '+DATA)

# Submit job card
os.chmod(AWS_job_filename, 0o755)
print("Submitting "+AWS_job_filename+" to "+QUEUESERV)
print("Output sent to "+AWS_job_output)
if machine == 'WCOSS2':
    os.system('qsub  '+AWS_job_filename)
elif machine in ['HERA', 'ORION']:
    os.system('sbatch '+AWS_job_filename)

print("END: "+os.path.basename(__file__))
