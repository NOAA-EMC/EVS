#!/bin/bash
#PBS -N jevs_analyses_rtma_ru_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=shared,select=1:ncpus=1:mem=10GB
#PBS -l debug=true

set -x

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

###%include <head.h>
###%include <envir-p1.h>

############################################################
# Load modules
############################################################

module reset
module load prod_envir/${prod_envir_ver}

############################################################
### For dev testing
##############################################################

export envir=prod
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=YES
export SENDMAIL=YES
export NET=evs
export STEP=stats
export COMPONENT=analyses
export RUN=atmos
export VERIF_CASE=grid2obs

source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}


export vhr
echo $vhr

export mod_ver=${rtma_ver}
export modsys=rtma
export MODELNAME=rtma_ru

export MAILTO="perry.shafran@noaa.gov,alicia.bentley@noaa.gov"

# CALL executable job script here
$HOMEevs/jobs/JEVS_ANALYSES_STATS

######################################################################
## Purpose: This job will generate the grid2obs statistics for the NAM_FIREWXNEST
##          model and generate stat files.
#######################################################################
#
exit
