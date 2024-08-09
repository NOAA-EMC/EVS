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
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

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

export envir=prod
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
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}

export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/${envir}/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${RUN}_${VERIF_CASE}_${DATA_TYPE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

############################################################
# CALL executable job script here
############################################################
export MAILTO=${MAILTO:-'ho-chun.huang@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$MAILTO" ]; then
    echo "MAILTO variable is not defined. Exiting without continuing."
else
    export vhr
    echo "vhr = ${vhr}"
    ${HOMEevs}/jobs/JEVS_GLOBAL_ENS_CHEM_GRID2OBS_STATS
fi
######################################################################
## Purpose: This job will generate the grid2obs statistics using AERONET AOD
##          for the GEFS-Aerosol model.
#######################################################################
