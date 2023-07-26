#PBS -N jevs_nfcens_grid2obs_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=1:mem=5GB
#PBS -l debug=true
#PBS -V

set -x 

##%include <head.h>
##%include <envir-p1.h>

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export MODELNAME=nfcens
export NET=evs
export COMPONENT=nfcens
export STEP=prep
export RUN=wave
export VERIF_CASE=grid2obs

############################################################
# read version file and set model_ver
############################################################
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export model_ver=$nfcens_ver

############################################################
# Load modules
############################################################
module reset
source $HOMEevs/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

############################################################
# set some variables
############################################################
export envir=prod
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-YES}
export KEEPDATA=${KEEPDATA:-YES}

export cycle=t00z

## developers directories
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_output
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export OUTPUTROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=${OUTPUTROOT}/${NET}/${evs_ver}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}

export job=${PBS_JOBNAME:-jevs_nfcens_grid2obs_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/${COMPONENT}/${STEP}/JEVS_NFCENS_WAVE_GRID2OBS_PREP

##%include <tail.h>
##%manual
######################################################################
# Purpose: This does the prep work for the NFCENS wave model
######################################################################
##%end
exit
