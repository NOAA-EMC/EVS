#PBS -N jevs_global_ens_wave_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:20:00
#PBS -l place=vscatter,select=1:ncpus=36:mem=25G
#PBS -l debug=true
#PBS -V

set -x 

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
############################################################
# read version file and set model_ver
############################################################
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export model_ver=$gefs_ver
export MODELNAME=gefs
export OBTYPE=GDAS
export NET=evs
export COMPONENT=global_ens
export STEP=stats
export RUN=wave
export VERIF_CASE=grid2obs


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
export KEEPDATA=${KEEPDATA:-YES}


## developers directories
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_output
export FIXevs='/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix'
export OUTPUTROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=${OUTPUTROOT}/${NET}/${evs_ver}
export COMOUT=${OUTPUTROOT}/${NET}/${evs_ver}/${STEP}/${COMPONENT}

export run_mpi='yes'
export gather='yes'

export job=${PBS_JOBNAME:-jevs_global_ens_wave_grid2obs_stats}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# CALL executable job script here
############################################################
${HOMEevs}/jobs/global_ens/stats/JEVS_GLOBAL_ENS_WAVE_GRID2OBS_STATS

#######################################################################
# Purpose: This calculates the stats for the global_ens GEFS-Wave model
#######################################################################
