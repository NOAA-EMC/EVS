#PBS -N jevs_subseasonal_cfs_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:40:00
#PBS -l place=vscatter,select=1:ncpus=8:ompthreads=1:mem=60GB
#PBS -l debug=true
#PBS -V

set -x

export model=evs

cd $PBS_O_WORKDIR

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export job=${PBS_JOBNAME:-jevs_subseasonal_cfs_grid2obs_stats}
export jobid=$job.${PBS_JOBID:-$$}

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/subseasonal/subseasonal_stats.sh


export USER=$USER
export envir=prod
export KEEPDATA=YES
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export ACCOUNT=VERF-DEV
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=8
export USE_CFP=YES
export met_ver=${met_ver}
export metplus_ver=${metplus_ver}
export cyc=00
export NET=evs
export evs_ver=${evs_ver}
export STEP=stats
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME=cfs
export cfs_ver=${cfs_ver}
export VERIF_CASE=grid2obs

export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.cfs.grid2obs.stats

# Call executable job script
$HOMEevs/jobs/JEVS_SUBSEASONAL_STATS


######################################################################
# Purpose: The job and task scripts work together to generate the
#          subseasonal verification grid-to-obs statistics for the CFS model 
#          and create the stat files in the databases.
######################################################################
