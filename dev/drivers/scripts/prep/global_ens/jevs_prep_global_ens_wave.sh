#PBS -N jevs_prep_global_ens_wave
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=shared,select=1:ncpus=1:mem=15GB
#PBS -l debug=true

set -x 

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

############################################################
# read version file and set model_ver
############################################################
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export model_ver=$gefs_ver
export MODELNAME=gefs
export NET=evs
export COMPONENT=global_ens
export STEP=prep
export RUN=wave
export VERIF_CASE=grid2obs

############################################################
# Load modules
############################################################
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

############################################################
# set some variables
############################################################
export envir=prod
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-YES}
export KEEPDATA=${KEEPDATA:-NO}
#export SENDMAIL=YES
source $HOMEevs/dev/drivers/set_MAILTO.sh

## developers directories
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}

export job=${PBS_JOBNAME:-jevs_prep_global_ens_wave}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/JEVS_PREP_GLOBAL_ENS

######################################################################
# Purpose: This does the prep work for the global_ens GEFS-Wave model
######################################################################
