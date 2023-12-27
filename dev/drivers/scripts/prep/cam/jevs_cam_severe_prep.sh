#PBS -N jevs_cam_severe_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=0:15:00
#PBS -l place=shared,select=1:ncpus=1:mem=10GB
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

source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)


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
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d/$STEP/$COMPONENT
############################################################

export vhr=${vhr:-${vhr}}

export SENDMAIL=${SENDMAIL:-YES}
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-NO}

export MAILTO=${MAILTO:-'marcel.caron@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/JEVS_CAM_PREP

fi


######################################################################
# Purpose: This job preprocesses SPC storm reports and outlook
#          areas for use in the CAM severe verification job
######################################################################

