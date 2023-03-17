'''
Program Name: run_subseasonal_batch_plots.py
Contact(s): Shannon Shields
Abstract: This script is run by evs_subseasonal.sh.
          It creates a job card for the verification
          script to run and submits it.
'''

import os
import sys

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
machine = os.environ['machine']
NET = os.environ['NET']
RUN = os.environ['RUN']
COMPONENT = os.environ['COMPONENT']
STEP = os.environ['STEP']
VERIF_CASE = os.environ['VERIF_CASE']
HOMEevs = os.environ['HOMEevs']
QUEUE = os.environ['QUEUE']
ACCOUNT = os.environ['ACCOUNT']
PARTITION_BATCH = os.environ['PARTITION_BATCH']
nproc = os.environ['nproc']

#Set up dictionary to write environment variables to job card
env_var_to_job_card_list = [
    'HOMEevs', 'USHevs', 'PARMevs', 'config', 'FIXevs',
    'members', 'HOMEMET', 'HOMEMETplus',
    'NET', 'RUN', 'COMPONENT', 'STEP', 'VERIF_CASE',
    'OUTPUTROOT', 'DATA', 'machine', 'ACCOUNT', 'QUEUE', 'QUEUESERV',
    'PARTITION_BATCH', 'nproc', 'job', 'jobid', 'USE_CFP', 'HOMEMET_bin_exec',
    'MET_version', 'MET_verbosity', 'log_MET_output_to_METplus',
    'METplus_version', 'METPLUS_PATH', 'METplus_verbosity',
    'RM', 'CUT', 'TR', 'NCAP2', 'CONVERT', 'NCDUMP', 'envir'
]

# Get RUN ex script
script = os.path.join(HOMEevs, 'scripts', COMPONENT, STEP,
                      'ex'+NET+'_'+COMPONENT+'_'+STEP+'.sh')

# Create job card directory and file name
cwd = os.getcwd()
batch_job_dir = os.path.join(cwd, 'batch_jobs')
if not os.path.exists(batch_job_dir):
    os.makedirs(batch_job_dir)
job_card_filename = os.path.join(batch_job_dir, NET+'_'
                                 +COMPONENT+'_'+STEP+'.sh')
job_output_filename = os.path.join(batch_job_dir, NET+'_'
                                   +COMPONENT+'_'+STEP+'.out')
job_name = NET+'_'+COMPONENT+'_'+STEP

# Create job card
print("Writing job card to "+job_card_filename)
with open(job_card_filename, 'a') as job_card:
    if machine == 'WCOSS2':
        job_card.write('#!/bin/sh\n')
        job_card.write('#PBS -q '+QUEUE+'\n')
        job_card.write('#PBS -A '+ACCOUNT+'\n')
        job_card.write('#PBS -N '+job_name+'\n')
        job_card.write('#PBS -o '+job_output_filename+'\n')
        job_card.write('#PBS -e '+job_output_filename+'\n')
        job_card.write('#PBS -l walltime=6:00:00\n')
        job_card.write('#PBS -l debug=true\n')
        job_card.write('#PBS -l place=vscatter:exclhost,select=1'
                       +':ncpus='+nproc+'\n')
        job_card.write('\n')
        job_card.write('cd $PBS_O_WORKDIR\n')
    elif machine == 'HERA':
        job_card.write('#!/bin/sh\n')
        job_card.write('#SBATCH --qos='+QUEUE+'\n')
        job_card.write('#SBATCH --account='+ACCOUNT+'\n')
        job_card.write('#SBATCH --job-name='+job_name+'\n')
        job_card.write('#SBATCH --output='+job_output_filename+'\n')
        if RUN in ['grid2grid_step2', 'grid2obs_step2', 'precip_step2',
                   'maps2d', 'mapsda']:
            job_card.write('#SBATCH --mem=10g\n')
        else:
            job_card.write('#SBATCH --mem=3g\n')
        job_card.write('#SBATCH --nodes=1\n')
        job_card.write('#SBATCH --ntasks-per-node='+nproc+'\n')
        job_card.write('#SBATCH --time=6:00:00\n')
    elif machine == 'ORION':
        job_card.write('#!/bin/sh\n')
        job_card.write('#SBATCH --partition='+PARTITION_BATCH+'\n')
        job_card.write('#SBATCH --qos='+QUEUE+'\n')
        job_card.write('#SBATCH --account='+ACCOUNT+'\n')
        job_card.write('#SBATCH --job-name='+job_name+'\n')
        job_card.write('#SBATCH --output='+job_output_filename+'\n')
        job_card.write('#SBATCH --mem=3g\n')
        job_card.write('#SBATCH --nodes=1\n')
        job_card.write('#SBATCH --ntasks-per-node='+nproc+'\n')
        job_card.write('#SBATCH --time=6:00:00\n')
    job_card.write('\n')
    for env_var in env_var_to_job_card_list:
        if env_var in os.environ:
            job_card.write('export '+env_var+'="'+os.environ[env_var]+'"\n')
        else:
            print("ERROR: "+env_var+" NOT IN ENVIRONMENT, "
                  +"check your configuration file")
            sys.exit(1)
    job_card.write('\n')
    job_card.write('. $config\n')
    job_card.write('/bin/sh '+script)

# Submit job card
print("Submitting "+job_card_filename+" to "+QUEUE)
print("Output sent to "+job_output_filename)
if machine == 'WCOSS2':
    os.system('qsub '+job_card_filename)
elif machine in ['HERA', 'ORION']:
    os.system('sbatch '+job_card_filename)

print("END: "+os.path.basename(__file__))
