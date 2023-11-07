#PBS -N jevs_subseasonal_gefs_grid2grid_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A EVS-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter,select=1:ncpus=59:ompthreads=1:mem=70GB
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
source $HOMEevs/dev/modulefiles/subseasonal/subseasonal_stats.sh

export evs_ver=v1.0.0
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)


export USER=$USER
export ACCOUNT=EVS-DEV
export envir=prod
export KEEPDATA=YES
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=59
export USE_CFP=YES
export met_ver=${met_ver}
export metplus_ver=${metplus_ver}
export vhr=00
export NET=evs
export STEP=stats
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME=gefs
export gefs_ver=${gefs_ver}
export VERIF_CASE=grid2grid

export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}/$STEP/$COMPONENT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}/prep/$COMPONENT/$RUN

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.gefs.grid2grid.stats

# Call executable job script
$HOMEevs/jobs/JEVS_SUBSEASONAL_STATS


######################################################################
# Purpose: The job and task scripts work together to generate the
#          subseasonal verification grid-to-grid statistics for the GEFS model#          and create the stat files in the databases.
######################################################################
