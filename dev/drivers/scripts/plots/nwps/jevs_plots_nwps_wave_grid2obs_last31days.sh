#PBS -N jevs_plots_nwps_wave_grid2obs_last31days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=2:ncpus=100:mem=100G
#PBS -l debug=true

set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export MODELNAME=nwps
export OBTYPE=NDBC_STANDARD
export NET=evs
export COMPONENT=nwps
export STEP=plots
export RUN=wave
export VERIF_CASE=grid2obs

############################################################
# read version file and set model_ver
############################################################
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export model_ver=$nwps_ver

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
export KEEPDATA=${KEEPDATA:-NO}

## developers directories
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export OUTPUTROOT=/lfs/h2/emc/ptmp/$USER
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}_devonly/${evs_ver_2d}
export COMOUT=${OUTPUTROOT}/${NET}_devonly/${evs_ver_2d}
export EVAL_PERIOD="last31days"

export run_mpi='yes'
export gather='yes'

export job=${PBS_JOBNAME:-jevs_${STEP}_${COMPONENT}_${RUN}_${VERIF_CASE}_${EVAL_PERIOD}}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# CALL executable job script here
############################################################
${HOMEevs}/jobs/JEVS_PLOTS_NWPS

#########################################################################
# Purpose: This job creates the plots for the NWPS wave model
# Author: Samira ardani (samira.ardani@noaa.gov)
#########################################################################
