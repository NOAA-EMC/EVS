#PBS -N jevs_cam_radar_plots_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=1:50:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=64
#PBS -l debug=true
#PBS -V


set -x

cd $PBS_O_WORKDIR


############################################################
# Load modules
############################################################


export model=evs
export NET=evs
export COMPONENT=cam
export STEP=plots
export RUN=atmos

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh


############################################################
# For dev testing
############################################################
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=NO
export VERIF_CASE=radar
export MODELNAME=${COMPONENT}
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${LINE_TYPE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/$STEP/$COMPONENT
export nproc=64
############################################################

export cyc=${cyc:-${cyc}}
export EVAL_PERIOD=${EVAL_PERIOD:-${EVAL_PERIOD}}
export LINE_TYPE=${LINE_TYPE:-${LINE_TYPE}}

export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-NO}

export maillist=${maillist:-'marcel.caron@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/cam/plots/JEVS_CAM_PLOTS

fi


######################################################################
# Purpose: This job generates radar verification graphics
#          for the CAM component (deterministic and ensemble CAMs)
######################################################################

