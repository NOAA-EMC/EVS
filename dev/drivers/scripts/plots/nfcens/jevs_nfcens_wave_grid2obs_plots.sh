#PBS -N jevs_nfcens_wave_grid2obs_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter:exclhost,select=2:ncpus=128:mem=500G
#PBS -l debug=true

set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

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

## developers directories
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export OUTPUTROOT=/lfs/h2/emc/ptmp/$USER
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver_2d}
export COMOUT=${OUTPUTROOT}/${NET}/${evs_ver_2d}

export run_mpi='yes'
export gather='yes'

export job=${PBS_JOBNAME:-jevs_nfcens_wave_grid2obs_plots}
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
