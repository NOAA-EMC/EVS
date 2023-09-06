#!/bin/bash
#PBS -N jevs_cam_nam_firewxnest_grid2obs_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l select=1:ncpus=1:mem=2GB
#PBS -l debug=true

export model=evs

cd $PBS_O_WORKDIR

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

############################################################
# Load modules
############################################################
set -x

module reset
module load prod_envir/${prod_envir_ver}

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=NO

export cyc
export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=nam_firewxnest
export modsys=nam
export mod_ver=${nam_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export COMOUT=$COMIN/${STEP}/${COMPONENT}

export maillist=perry.shafran@noaa.gov

export config=$HOMEevs/parm/evs_config/cam/config.evs.cam_nam_firewxnest.prod
source $config

# CALL executable job script here
$HOMEevs/jobs/cam/stats/JEVS_CAM_STATS

######################################################################
## Purpose: This job will generate the grid2obs statistics for the NAM_FIREWXNEST
##          model and generate stat files.
#######################################################################
#
exit

