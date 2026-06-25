#PBS -N jevs_stats_cam_rrfs_chem_grid2obs_airnow_pm10
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:40:00
#PBS -l place=shared,select=1:ncpus=1:mem=10GB
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo ${evs_ver} | cut -d'.' -f1-2)

############################################################
# Load modules
############################################################

module reset

module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/cam/cam_stats.sh

############################################################
# set some variables
############################################################
export KEEPDATA=NO
export SENDMAIL=YES
export SENDDBN=NO

export envir=prod
export NET=${NET:-evs}
export STEP=${STEP:-stats}
export COMPONENT=${COMPONENT:-cam}
export RUN=${RUN:-chem}
export VERIF_CASE=${VERIF_CASE:-grid2obs}
export MODELNAME=${MODELNAME:-rrfs}

export DATA_TYPE=airnow_pm10

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}/${STEP}/${COMPONENT}

export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/${envir}/tmp
export job=${PBS_JOBNAME:-jevs_${STEP}_${COMPONENT}_${MODELNAME}_${RUN}_${VERIF_CASE}_${DATA_TYPE}}
export jobid=$job.${PBS_JOBID:-$$}

############################################################
# CALL executable job script here
############################################################
export MAILTO=${MAILTO:-'ho-chun.huang@noaa.gov,andrew.benjamin@noaa.gov'}

if [ -z "$MAILTO" ]; then
   echo "MAILTO variable is not defined. Exiting without continuing."
else
    export vhr
    echo "vhr = ${vhr}"
    ${HOMEevs}/jobs/JEVS_STATS_CAM
fi
######################################################################
## Purpose: This job will generate the grid2obs statistics using AirNOW PM10
##          for the RRFS-Smoke_Dust model.
#######################################################################
