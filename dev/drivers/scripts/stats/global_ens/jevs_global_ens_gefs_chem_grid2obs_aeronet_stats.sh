#PBS -N jevs_global_ens_gefs_chem_grid2obs_aeronet_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs
## export HOMEevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/EVS
## export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVSGefsChem

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo ${evs_ver} | cut -d'.' -f1-2)

############################################################
## Load modules
############################################################
############################################################
## Specify environment variables
############################################################
############################################################
# Load modules
############################################################
module reset

module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/global_ens/global_ens_stats.sh

############################################################
# set some variables
############################################################
export KEEPDATA=YES
export SENDMAIL=YES
export SENDDBN=NO

export NET=${NET:-evs}
export STEP=${STEP:-stats}
export COMPONENT=${COMPONENT:-global_ens}
export RUN=${RUN:-chem}
export VERIF_CASE=${VERIF_CASE:-grid2obs}
export MODELNAME=${MODELNAME:-gefs}
export modsys=${modsys:-gefs}
export mod_ver=${mod_ver:-${gefs_ver}}

export VDATE=$(date --date="3 days ago" +%Y%m%d)
echo "VDATE=${VDATE}"

export DATA_TYPE=aeronet 

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
mkdir -p ${COMIN}
export COMOUT=${COMIN}

export DATAROOT=/lfs/h2/emc/ptmp/${USER}/${NET}/${evs_ver_2d}/${STEP}
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${RUN}_${VERIF_CASE}_${DATA_TYPE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

############################################################
# CALL executable job script here
############################################################
export MAILTO=${MAILTO:-'ho-chun.huang@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$MAILTO" ]; then
    echo "MAILTO variable is not defined. Exiting without continuing."
else
  ## adjust walltime for 01:45:00 ## only for PR testing remove for EMC/parallel and operational
  ## for vhr in 00 03 06 09 12 15 18 21; do  ## only for PR testing remove for EMC/parallel and operational
    export vhr
    echo "vhr = ${vhr}"
    ${HOMEevs}/jobs/JEVS_GLOBAL_ENS_CHEM_GRID2OBS_STATS
  ## done  ## only for PR testing remove for EMC/parallel and operational
fi
######################################################################
## Purpose: This job will generate the grid2obs statistics using AERONET AOD
##          for the GEFS-Aerosol model.
#######################################################################
