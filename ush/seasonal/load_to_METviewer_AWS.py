'''
Program Name: load_to_METviewer_AWS.py
Contact(s): Shannon Shields
Abstract: This is run at the end of all stats scripts
          in scripts/.
          This scripts loads data to the METviewer AWS
          server.
              1) Create a temporary directory and
                 link the files that are to be
                 loaded
              2) Create XML that will load files
              3) Create database on AWS server
              4) Listing of METviewer datbases
'''

import datetime
import os
import subprocess

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
KEEPDATA = os.environ['KEEPDATA']
machine = os.environ['machine']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
RUN_abbrev = os.environ['RUN_abbrev']
RUN_type_list = os.environ[RUN_abbrev+'_type_list'].split(' ')
USHevs = os.environ['USHevs']
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
PARTITION_BATCH = os.environ['PARTITION_BATCH']
MET_version = os.environ['MET_version']
model_list = os.environ['model_list'].split(' ')
METviewer_AWS_scripts_dir = os.environ['METviewer_AWS_scripts_dir']
mv_database = os.environ[RUN_abbrev+'_mv_database_name']
mv_group = os.environ[RUN_abbrev+'_mv_database_group']
mv_desc = os.environ[RUN_abbrev+'_mv_database_desc']

# Set up walltime
transfer_walltime = '180'
walltime_seconds = datetime.timedelta(minutes=int(transfer_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(transfer_walltime))).time()

# Check current databases to see if it exists
current_database_info = subprocess.check_output(
    os.path.join(METviewer_AWS_scripts_dir, 'mv_db_size_on_aws.sh')+' '
    +os.environ['USER'].lower(), shell=True, encoding='UTF-8'
)
if mv_database in current_database_info:
    new_or_add = 'add'
else:
    new_or_add = 'new'

# Create linking file dir
link_file_dir = os.path.join(os.getcwd(), 'METviewer_AWS_files')
os.makedirs(link_file_dir, mode=0o755)

# Create load XML
load_xml_file = os.path.join(os.getcwd(), 'load_'+mv_database+'.xml')
print("Creating load xml "+load_xml_file)
if new_or_add == 'new':
    drop_index = 'false'
else:
    drop_index = 'true'
if os.path.exists(load_xml_file):
    os.remove(load_xml_file)
with open(load_xml_file, 'a') as xml:
    xml.write('<load_spec>\n')
    xml.write('  <connection>\n')
    xml.write('    <host>metviewer-dev-cluster.cluster-czbts4gd2wm2.'
              +'us-east-1.rds.amazonaws.com:3306</host>\n')
    xml.write('    <database>'+mv_database+'</database>\n')
    xml.write('    <user>rds_user</user>\n')
    xml.write('    <password>rds_pwd</password>\n')
    xml.write('    <management_system>aurora</management_system>\n')
    xml.write('  </connection>\n')
    xml.write('\n')
    xml.write('  <met_version>V'+MET_version+'</met_version>\n')
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
for RUN_type in RUN_type_list:
    gather_by = os.environ[RUN_abbrev+'_'+RUN_type+'_gather_by']
    for model in model_list:
        gather_by_RUN_type_model_dir = os.path.join(
            DATA, RUN, 'metplus_output', 'gather_by_'+gather_by,
            'stat_analysis', RUN_type, model
        )
        for file_name in os.listdir(gather_by_RUN_type_model_dir):
            os.link(
                os.path.join(gather_by_RUN_type_model_dir, file_name),
                os.path.join(link_file_dir, RUN_type+'_'+file_name)
            )
            with open(load_xml_file, 'a') as xml:
                xml.write('    <file>/base_dir/'
                          +RUN_type+'_'+file_name+'</file>\n')
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
AWS_job_filename = os.path.join(DATA, 'batch_jobs',
                                NET+'_'+RUN+'_load2METviewerAWS.sh')
with open(AWS_job_filename, 'a') as AWS_job_file:
    AWS_job_file.write('#!/bin/sh'+'\n')
    AWS_job_file.write('set -x'+'\n')
    if new_or_add == 'new':
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
        AWS_job_file.write('cd ..\n')
        AWS_job_file.write('rm -rf '+RUN)

# Submit job card
os.chmod(AWS_job_filename, 0o755)
AWS_job_output = AWS_job_filename.replace('.sh', '.out')
AWS_job_name = AWS_job_filename.rpartition('/')[2].replace('.sh', '')
print("Submitting "+AWS_job_filename+" to "+QUEUESERV)
print("Output sent to "+AWS_job_output)
if machine == 'WCOSS_C':
    os.system('bsub -W '+walltime.strftime('%H:%M')+' -q '+QUEUESERV+' '
              +'-P '+ACCOUNT+' -o '+AWS_job_output+' -e '+AWS_job_output+' '
              +'-J '+AWS_job_name+' -R rusage[mem=2048] '+AWS_job_filename)
elif machine in ['HERA', 'ORION']:
    os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
              +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
              +'--output='+AWS_job_output+' '
              +'--job-name='+AWS_job_name+' '+AWS_job_filename)

print("END: "+os.path.basename(__file__))
