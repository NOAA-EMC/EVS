#PBS -N jevs_cam_hireswfv3_severe_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=0:30:00
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

export cyc=${cyc:-${cyc}}


############################################################
# For dev testing
############################################################
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=NO
export VERIF_CASE=severe
export MODELNAME=hireswfv3
export modsys=hiresw
export job=${PBS_JOBNAME:-jevs_${COMPONENT}_${MODELNAME}_${VERIF_CASE}_${STEP}_${cyc}}
export jobid=$job.${PBS_JOBID:-$$}
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver}
export COMINspc=/lfs/h1/ops/dev/dcom
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver}/${STEP}/${COMPONENT}
############################################################

export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-NO}

export maillist=${maillist:-'logan.dawson@noaa.gov,geoffrey.manikin@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/cam/prep/JEVS_CAM_PREP

fi


######################################################################
# Purpose: This job preprocesses HiResW FV3 data for use in
#          CAM severe verification jobs
######################################################################

