#PBS -N jevs_subseasonal_gefs_grid2grid_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=61:ompthreads=1:mem=70GB
#PBS -l debug=true
#PBS -V

set -x

export model=evs

cd $PBS_O_WORKDIR

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export job=${PBS_JOBNAME:-jevs_subseasonal_gefs_grid2grid_stats}
export jobid=$job.${PBS_JOBID:-$$}

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/subseasonal/subseasonal_stats.sh

export MET_ROOT=/apps/ops/prod/libs/intel/${intel_ver}/met/${met_ver}
export MET_BASE=${MET_ROOT}/share/met
export PATH=${MET_ROOT}/bin:${PATH}

export USER=$USER
export envir=prod
export KEEPDATA=YES
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export ACCOUNT=VERF-DEV
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=61
export USE_CFP=YES
export met_ver=${met_ver}
export metplus_ver=${metplus_ver}
export cyc=00
export NET=evs
export evs_ver=${evs_ver}
export STEP=stats
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME=gefs
export gefs_ver=${gefs_ver}
export VERIF_CASE=grid2grid

export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.gefs.grid2grid.stats

# Call executable job script
$HOMEevs/jobs/JEVS_SUBSEASONAL_STATS


######################################################################
# Purpose: The job and task scripts work together to generate the
#          subseasonal verification grid-to-grid statistics for the GEFS model#          and create the stat files in the databases.
######################################################################
