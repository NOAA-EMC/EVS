#PBS -N jevs_cam_severe_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=0:15:00
#PBS -l select=1:ncpus=1:mem=10GB
#PBS -l debug=true
#PBS -V


set -x

cd $PBS_O_WORKDIR


############################################################
# Load modules
############################################################


export model=evs
export NET=evs
export STEP=prep
export COMPONENT=cam
export RUN=atmos

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh


############################################################
# For dev testing
############################################################
export envir=prod
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=YES
export VERIF_CASE=severe
export MODELNAME=cam
export job=${PBS_JOBNAME:-jevs_cam_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver}/${STEP}/${COMPONENT}
############################################################

export vhr=${vhr:-${vhr}}

export SENDMAIL=${SENDMAIL:-YES}
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-NO}

export maillist=${maillist:-'marcel.caron@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/JEVS_CAM_PREP

fi


######################################################################
# Purpose: This job preprocesses SPC storm reports and outlook
#          areas for use in the CAM severe verification job
######################################################################

