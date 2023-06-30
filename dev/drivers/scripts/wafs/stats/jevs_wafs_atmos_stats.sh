#PBS -N jevs_wafs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=4:mem=10GB
#PBS -l debug=true
#PBS -V

##PBS -q debug
##PBS -A GFS-DEV
##PBS -q dev
##PBS -A VERF-DEV

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
module reset
source $HOMEevs/versions/run.ver
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_$STEP.sh

############################################################
# environment variables set
############################################################
export MET_bin_exec=bin

export envir=prod

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/evs/$evs_ver

############################################################
# set up for email alerts of missing data
############################################################
export pid=${PBS_JOBID:-$$}
export job=${PBS_JOBNAME:-jevs_aviation_stats}
export jobid=$job.$pid
export maillist=${maillist:-'geoffrey.manikin@noaa.gov,yali.mao@noaa.gov'}

############################################################
# CALL executable job script here
############################################################
export DATA=/lfs/h2/emc/ptmp/$USER/evs/working/${STEP}.$pid

export KEEPDATA=YES

$HOMEevs/jobs/wafs/stats/JEVS_WAFS_ATMOS_STATS

############################################################
## Purpose: This job generates the grid2grid statistics stat
##          files for GFS WAFS
############################################################
#
exit
