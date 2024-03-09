#PBS -N jevs_global_ens_gefs_chem_g2o_aeronet_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs

## export HOMEevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/EVS
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVSGefsChem

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo ${evs_ver} | cut -d'.' -f1-2)

############################################################
# Load modules
############################################################
module reset

module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/global_ens/global_ens_stats.sh

############################################################
# set some variables
############################################################
export KEEPDATA=NO
export SENDMAIL=YES
export SENDDBN=NO

export NET=${NET:-evs}
export STEP=${STEP:-stats}
export COMPONENT=${COMPONENT:-global_ens}
export RUN=${RUN:-chem}
export VERIF_CASE=${VERIF_CASE:-grid2obs}
export MODELNAME=${MODELNAME:-gefs}
export modsys=${modsys:-gefs}

export VDATE=$(date --date="3 days ago" +%Y%m%d)
echo "VDATE=${VDATE}"

export DATA_TYPE=aeronet 

## export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export COMIN=/lfs/h2/emc/physics/noscrub/$USER/$NET/${evs_ver_2d}
mkdir -p ${COMIN}
export COMOUT=${COMIN}

export DATAROOT=/lfs/h2/emc/ptmp/${USER}/$}NET}/${evs_ver_2d}/${STEP}
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${RUN}_${VERIF_CASE}_${DATA_TYPE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}
mkdir -p ${DATA}

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
############################################################
## For EMC PARA TESTING
## Keep only 35 days from today
############################################################
 
TODAY=`date +%Y%m%d`

export NUM_DAY_BACK=60
let hour_back=${NUM_DAY_BACK}*24
export CLEAN_START=$(${NDATE} -${hour_back} ${TODAY}"00" | cut -c1-8)

export NUM_DAY_BACK=35
let hour_back=${NUM_DAY_BACK}*24
export CLEAN_END=$(${NDATE} -${hour_back} ${TODAY}"00" | cut -c1-8)

cd ${COMOUT}/${STEP}/${COMPONENT}
NOW=${CLEAN_START}
while [ ${NOW} -lt ${CLEAN_END} ]; do
    if [ -d ${RUN}.${NOW} ]; then
        /bin/rm -rf ${RUN}.${NOW}
    fi
    if [ -d ${MODELNAME}.${NOW} ]; then
        /bin/rm -rf ${MODELNAME}.${NOW}
    fi
    cdate=${NOW}"00"
    NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
######################################################################
## Purpose: This job will generate the grid2obs statistics using aeronet aod
##          for the GEFS-Aerosol model.
#######################################################################
