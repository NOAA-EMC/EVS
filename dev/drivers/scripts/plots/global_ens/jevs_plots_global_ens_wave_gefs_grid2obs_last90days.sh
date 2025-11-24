#PBS -N jevs_plots_global_ens_wave_gefs_grid2obs_last90days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=108:mem=110G
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
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

############################################################
# set some variables
############################################################
export envir=prod
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=NO
export KEEPDATA=${KEEPDATA:-NO}
export SENDMAIL=YES

## developers directories
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/ptmp/$USER/${NET}/${evs_ver_2d}
export EVAL_PERIOD="last90days"
export run_mpi='yes'
export gather='yes'


export job=${PBS_JOBNAME:-jevs_plots_global_ens_wave_gefs_grid2obs_last90days}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

############################################################
# CALL executable job script here
############################################################
${HOMEevs}/jobs/JEVS_PLOTS_GLOBAL_ENS

#########################################################################
# Purpose: This job creates the plots for the global_ens GEFS-Wave model
#########################################################################
