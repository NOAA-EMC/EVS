'''
Program Name: run_seasonal_batch.py
Contact(s): Shannon Shields
Abstract: This script is run by evs_seasonal.sh.
          It creates a job card for the verification
          script to run and submits it.
'''

import os

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
machine = os.environ['machine']
NET = os.environ['NET']
RUN = os.environ['RUN']
HOMEevs = os.environ['HOMEevs']
QUEUE = os.environ['QUEUE']
ACCOUNT = os.environ['ACCOUNT']
PARTITION_BATCH = os.environ['PARTITION_BATCH']
nproc = os.environ['nproc']

# Get RUN ex script
script = os.path.join(HOMEevs, 'scripts', 'seasonal', STEP,
                      'exevs_seasonal_'+STEP+'.sh')

# Create job card directory and file name
cwd = os.getcwd()
batch_job_dir = os.path.join(cwd, 'batch_jobs')
if not os.path.exists(batch_job_dir):
    os.makedirs(batch_job_dir)
job_card_filename = os.path.join(batch_job_dir,
                                 NET+'_'+RUN+'.sh')
job_output_filename = os.path.join(batch_job_dir,
                                   NET+'_'+RUN+'.out')
job_name = NET+'_'+RUN

# Create job card
print("Writing job card to "+job_card_filename)
with open(job_card_filename, 'a') as job_card:
    if machine in ['WCOSS_C']:
        job_card.write('#!/bin/sh\n')
        job_card.write('#PBS -q '+QUEUE+'\n')
        job_card.write('#PBS -A '+ACCOUNT+'\n')
        job_card.write('#PBS -N '+job_name+'\n')
        job_card.write('#PBS -j '+job_output_filename+'\n')
        job_card.write('#PBS -l walltime=8:00:00\n')
        #job_card.write('#BSUB -M 3000\n')
        job_card.write('#PBS -l place=vscatter:exclhost,select=1:ncpus=128\n')
        #if machine == 'WCOSS_C':
            #job_card.write("#PBS -extsched 'CRAYLINUX[]' -R '1*"
                           #"{select[craylinux && !vnode]} + "
                           #+nproc+"*{select[craylinux && vnode]"
                           #"span[ptile=24] cu[type=cabinet]}'")
        #elif machine == 'WCOSS_DELL_P3':
            #if RUN in ['grid2grid_step2']:
                #job_card.write('#BSUB -n '+str(int(nproc)*3)+'\n')
            #elif RUN in ['grid2obs_step2', 'maps2d']:
                #job_card.write('#BSUB -n '+str(int(nproc)*4)+'\n')
            #else:
                #job_card.write('#BSUB -n '+nproc+'\n')
            #job_card.write('#BSUB -R "span[ptile='+nproc+']"\n')
            #job_card.write('#BSUB -R affinity[core(1):distribute=balance]\n')
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
    job_card.write('/bin/sh '+script)

# Submit job card
print("Submitting "+job_card_filename+" to "+QUEUE)
print("Output sent to "+job_output_filename)
if machine in ['WCOSS_C']:
    os.system('qsub '+job_card_filename)
elif machine in ['HERA', 'ORION']:
    os.system('sbatch '+job_card_filename)

print("END: "+os.path.basename(__file__))
