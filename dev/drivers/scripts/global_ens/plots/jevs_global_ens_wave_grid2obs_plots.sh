#PBS -N jevs_global_ens_wave_grid2obs_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:15:00
#PBS -l place=vscatter,select=1:ncpus=128:mem=500G
#PBS -l debug=true
#PBS -V

set -x

#%include <head.h>
#%include <envir-p1.h>

#export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/gitworkspace/EVS

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
export STEP=plots
export RUN=wave
export VERIF_CASE=grid2obs

############################################################
## Load modules
#############################################################
module reset
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
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export OUTPUTROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=${OUTPUTROOT}/${NET}/${evs_ver}
export COMOUT=${OUTPUTROOT}/${NET}/${evs_ver}

######################################
# Correct MET/METplus roots (Aug 2022)
######################################
#export MET_ROOT=/apps/ops/prod/libs/intel/${intel_ver}/met/${met_ver}
#export MET_BASE=${MET_ROOT}/share/met
#export METPLUS_PATH=/apps/ops/prod/libs/intel/${intel_ver}/metplus/${metplus_ver}
#export PATH=${METPLUS_PATH}/ush:${MET_ROOT}/bin:${PATH}

export run_mpi='yes'
export gather='yes'

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
${HOMEevs}/jobs/global_ens/plots/JEVS_GLOBAL_ENS_WAVE_GRID2OBS_PLOTS

#%include <tail.h>
#%manual
#########################################################################
# Purpose: This job creates the plots for the global_ens GEFS-Wave model
#########################################################################
#%end
