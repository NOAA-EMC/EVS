#PBS -N jevs_global_ens_gefs_chem_g2o_aeronet_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q debug
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=1:mpiprocs=1:mem=10G
##PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/EVS
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVSGefsChem

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

############################################################
# Load modules
############################################################
#
module reset

module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/global_ens/global_ens_stats.sh

############################################################
# set some variables
############################################################
export KEEPDATA=YES
export SENDMAIL=NO
export SENDDBN=NO

export NET=${NET:-evs}
export STEP=${STEP:-stats}
export COMPONENT=${COMPONENT:-global_ens}
export RUN=${RUN:-chem}
export VERIF_CASE=${VERIF_CASE:-grid2obs}
export MODELNAME=${MODELNAME:-gefs}
export modsys=${modsys:-gefs}

export VDATE=$(date --date="3 days ago" +%Y%m%d)

export DATA_TYPE=aeronet 

export DATAROOT=/lfs/h2/emc/ptmp/${USER}/EVS/stats
export job=${PBS_JOBNAME:-jevs_gefs_chem_grib2obs_${DATA_TYPE}_stats}
export jobid=$job.${PBS_JOBID:-$$}
## export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export COMIN=/lfs/h2/emc/physics/noscrub/$USER/$NET/${evs_ver_2d}
mkdir -p ${COMIN}
export COMOUT=${COMIN}

############################################################
# CALL executable job script here
############################################################
export MAILTO=${MAILTO:-'ho-chun.huang@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else

   for vhr in 00 03 06 09 12 15 18 21; do
      export vhr
      echo "vhr = ${vhr}"
      $HOMEevs/jobs/JEVS_GLOBAL_ENS_CHEM_GRID2OBS_STATS
   done

fi
#
######################################################################
## Purpose: This job will generate the grid2obs statistics using aeronet aod
##          for the GEFS-Aerosol model.
#######################################################################
