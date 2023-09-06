#PBS -N jevs_nfcens_wave_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=vscatter,select=1:ncpus=36:mem=10G
#PBS -l debug=true
#PBS -V

set -x 

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export MODELNAME=nfcens
export OBTYPE=GDAS
export NET=evs
export COMPONENT=nfcens
export STEP=stats
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
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

############################################################
# set some variables
############################################################
export envir=prod
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-YES}
export KEEPDATA=${KEEPDATA:-NO}

## developers directories
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export FIXevs='/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix'
export OUTPUTROOT="/lfs/h2/emc/vpppg/noscrub/$USER"
export COMIN=${OUTPUTROOT}/${NET}/${evs_ver}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver}/${STEP}/${COMPONENT}

export run_mpi='yes'
export gather='yes'

export job=${PBS_JOBNAME:-jevs_nfcens_wave_grid2obs_stats}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/${COMPONENT}/${STEP}/JEVS_NFCENS_WAVE_GRID2OBS_STATS

#######################################################################
# Purpose: This calculates the stats for the NFCENS wave model
#######################################################################
