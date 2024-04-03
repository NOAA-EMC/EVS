#PBS -N jevs_global_ens_chem_g2o_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=shared,select=1:ncpus=1:mem=10GB:prepost=true
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs

## export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVSGefsChem

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

############################################################
# Load modules
############################################################
module reset

module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/global_ens/global_ens_prep.sh

############################################################
## set some variables
#############################################################
export KEEPDATA=NO
export SENDMAIL=YES
export SENDDBN=NO

export NET=${NET:-evs}
export STEP=${STEP:-prep}
export COMPONENT=${COMPONENT:-global_ens}
export RUN=${RUN:-chem}
export VERIF_CASE=${VERIF_CASE:-grid2obs}
export MODELNAME=${MODELNAME:-gefs}

export cyc=00
echo $cyc
export cycle=t${cyc}z

export VDATE=$(date --date="3 days ago" +%Y%m%d)
echo "VDATE=${VDATE}"

## export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export COMIN=/lfs/h2/emc/physics/noscrub/$USER/$NET/${evs_ver_2d}
mkdir -p ${COMIN}
export COMOUT=${COMIN}

export DATAROOT=/lfs/h2/emc/ptmp/${USER}/${NET}/${evs_ver_2d}/${STEP}
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${RUN}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}
mkdir -p ${DATA}

############################################################
## CALL executable job script here
#############################################################
$HOMEevs/jobs/JEVS_GLOBAL_ENS_CHEM_GRID2OBS_PREP

############################################################
## For EMC PARA TESTING
## Each chem.${VDATE} is about 4GB, keep only 10 days from today
############################################################
 
TODAY=`date +%Y%m%d`

export NUM_DAY_BACK=30
let hour_back=${NUM_DAY_BACK}*24
export CLEAN_START=$(${NDATE} -${hour_back} ${TODAY}"00" | cut -c1-8)

export NUM_DAY_BACK=10
let hour_back=${NUM_DAY_BACK}*24
export CLEAN_END=$(${NDATE} -${hour_back} ${TODAY}"00" | cut -c1-8)

cd ${COMOUT}/${STEP}/${COMPONENT}
NOW=${CLEAN_START}
while [ ${NOW} -lt ${CLEAN_END} ]; do
    if [ -d ${RUN}.${NOW} ]; then
        /bin/rm -rf ${RUN}.${NOW}
    fi
    cdate=${NOW}"00"
    NOW=$(${NDATE} +24 ${cdate}| cut -c1-8)
done
 
#######################################################################
# Purpose: This does the prep work for the global_ens GEFS-Chem model
#######################################################################
