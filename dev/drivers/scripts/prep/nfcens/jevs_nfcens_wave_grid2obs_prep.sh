#PBS -N jevs_nfcens_wave_grid2obs_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=shared,select=1:ncpus=1:mem=5GB
#PBS -l debug=true

set -x 

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
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

############################################################
# set some variables
############################################################
export envir=prod
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-YES}
export SENDMAIL=${SENDMAIL:-YES}

export MAILTO='alicia.bentley@noaa.gov,samira.ardani@noaa.gov'


## developers directories
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export OUTPUTROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver_2d}
export COMOUT=${OUTPUTROOT}/${NET}/${evs_ver_2d}/${STEP}/${COMPONENT}/${RUN}

export job=${PBS_JOBNAME:-jevs_nfcens_wave_grid2obs_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/JEVS_NFCENS_WAVE_GRID2OBS_PREP

######################################################################
# Purpose: This does the prep work for the NFCENS wave model
######################################################################
