#PBS -N jevs_global_ens_wave_grid2obs_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l select=1:ncpus=1:mem=15GB
#PBS -l debug=true
#PBS -V

set -x 

##%include <head.h>
##%include <envir-p1.h>

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
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export OUTPUTROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=${OUTPUTROOT}/${NET}/${evs_ver}

######################################
# Correct MET/METplus roots (Aug 2022)
######################################
#export MET_ROOT=/apps/ops/prod/libs/intel/${intel_ver}/met/${met_ver}
#export MET_BASE=${MET_ROOT}/share/met
#export METPLUS_PATH=/apps/ops/prod/libs/intel/${intel_ver}/metplus/${metplus_ver}
#export PATH=${METPLUS_PATH}/ush:${MET_ROOT}/bin:${PATH}

export job=${PBS_JOBNAME:-jevs_global_ens_wave_g2o_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

export metplus_verbosity="INFO"
export met_verbosity="2"
export log_met_output_to_metplus="yes"
export MET_bin_exec=bin

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/global_ens/prep/JEVS_GLOBAL_ENS_WAVE_GRID2OBS_PREP

##%include <tail.h>
##%manual
######################################################################
# Purpose: This does the prep work for the global_ens GEFS-Wave model
######################################################################
##%end
exit
