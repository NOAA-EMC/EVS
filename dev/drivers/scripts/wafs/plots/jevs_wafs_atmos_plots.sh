#PBS -N jevs_wafs_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=40:mem=200GB
#PBS -l debug=true
#PBS -V

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
export envir=dev

export NET=evs
export STEP=plots
export COMPONENT=wafs
export RUN=atmos
export VERIF_CASE=grid2grid

export COMIN=${COMIN:-/lfs/h2/emc/vpppg/noscrub/$USER/evs/$evs_ver}

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export USH_DIR=$HOMEevs/ush/$COMPONENT
export DAYS_LIST=${DAYS_LIST:-"90 31"}

############################################################
# CALL executable job script here
############################################################
export KEEPDATA=YES

export pid=${pid:-$$}
export DATA=/lfs/h2/emc/ptmp/$USER/evs/working/${STEP}.$pid

$HOMEevs/jobs/wafs/plots/JEVS_WAFS_ATMOS_PLOTS

############################################################
## Purpose: This job generates the grid2grid statistics stat
##          files for GFS WAFS
############################################################
#

exit

