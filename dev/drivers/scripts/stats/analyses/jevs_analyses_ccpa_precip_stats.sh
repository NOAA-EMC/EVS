#!/bin/bash
#PBS -N jevs_analyses_ccpa_precip_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=shared,select=1:ncpus=1:mem=10GB
#PBS -l debug=true
#PBS -V
 
set -x

cd $PBS_O_WORKDIR

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

############################################################
## Load modules
#############################################################

module reset
module load prod_envir/${prod_envir_ver}


############################################################
## For dev testing
#############################################################

export envir=prod
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=YES
export SENDMAIL=YES
export NET=evs
export STEP=stats
export COMPONENT=analyses
export RUN=atmos
export VERIF_CASE=precip

source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}
export EVSINccpa=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/${NET}/${evs_ver_2d}/prep/cam
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}

export vhr
echo $vhr

export mod_ver=${ccpa_ver}
export modsys=ccpa
export MODELNAME=ccpa

export MAILTO="perry.shafran@noaa.gov,alicia.bentley@noaa.gov"

# CALL executable job script here
$HOMEevs/jobs/JEVS_ANALYSES_STATS

######################################################################
## Purpose: This job will generate the grid2obs statistics for the NAM_FIREWXNEST
##          model and generate stat files.
#######################################################################
#
exit
