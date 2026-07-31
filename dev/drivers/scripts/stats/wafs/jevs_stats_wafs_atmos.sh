#PBS -N jevs_stats_wafs_atmos
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:25:00
#PBS -l place=shared,select=1:ncpus=5:mem=10GB
#PBS -l debug=true

set -x

export OMP_NUM_THREADS=1

export HOMEevs=${HOMEevs:-/lfs/h2/emc/vpppg/noscrub/$USER/EVS}

############################################################
# Basic environment variables
############################################################
export NET=evs
export STEP=stats
export COMPONENT=wafs
export RUN=atmos
export VERIF_CASE=grid2grid

############################################################
# Load modules
############################################################
source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_$STEP.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

############################################################
# environment variables set
############################################################
export envir=prod
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/$evs_ver_2d

############################################################
# set up for email alerts of missing data
############################################################
export pid=${PBS_JOBID:-$$}
export job=${PBS_JOBNAME:-jevs_stats_wafs_atmos}
export jobid=$job.$pid

source $HOMEevs/dev/drivers/set_MAILTO.sh
export SENDMAIL=${SENDMAIL:-YES}

############################################################
# CALL executable job script here
############################################################
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export KEEPDATA=NO

$HOMEevs/jobs/JEVS_STATS_WAFS

############################################################
## Purpose: This job generates the grid2grid statistics stat
##          files for WAFS
############################################################
#
exit
