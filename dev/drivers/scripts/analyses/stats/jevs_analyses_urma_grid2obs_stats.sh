#!/bin/bash
 
#PBS -N jevs_analyses_urma_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l select=1:ncpus=1:mem=2GB
#PBS -l debug=true

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

###%include <head.h>
###%include <envir-p1.h>

############################################################
# Load modules
############################################################
set -x

module reset
module load prod_envir/${prod_envir_ver}

## For dev testing
##############################################################

export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=NO
export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=analyses
export RUN=atmos
export VERIF_CASE=grid2obs

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}/${STEP}/${COMPONENT}

export cyc
echo $cyc
export envir=prod

export MODELNAME=urma
export modsys=urma
export mod_ver=${urma_ver}

export maillist="perry.shafran@noaa.gov,alicia.bentley@noaa.gov"

export config=$HOMEevs/parm/evs_config/analyses/config.evs.urma.prod
source $config

# CALL executable job script here
$HOMEevs/jobs/$COMPONENT/$STEP/JEVS_ANALYSES_STATS

######################################################################
## Purpose: This job will generate the grid2obs statistics for the NAM_FIREWXNEST
##          model and generate stat files.
#######################################################################
#
exit
