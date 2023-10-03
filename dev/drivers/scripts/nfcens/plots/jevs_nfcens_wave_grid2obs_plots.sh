#PBS -N jevs_nfcens_grid2obs_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=128:mem=500G
#PBS -l debug=true
#PBS -V

set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/githubworkspc/EVS

export MODELNAME=nfcens
export OBTYPE=GDAS
export NET=evs
export COMPONENT=nfcens
export STEP=plots
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
source $HOMEevs/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

############################################################
# set some variables
############################################################
export envir=prod
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-YES}
export KEEPDATA=${KEEPDATA:-YES}

## developers directories
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export OUTPUTROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/${NET}/${evs_ver}
export COMOUT=${OUTPUTROOT}/${NET}/${evs_ver}/${STEP}/${COMPONENT}/${RUN}

export run_mpi='yes'
export gather='yes'

export job=${PBS_JOBNAME:-jevs_nfcens_grid2obs_plots}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# CALL executable job script here
############################################################
${HOMEevs}/jobs/JEVS_NFCENS_WAVE_GRID2OBS_PLOTS

#########################################################################
# Purpose: This job creates the plots for the NFCENS wave model
#########################################################################
