#PBS -N jevs_plots_cam_radar_nbrcnt_last31days_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=0:15:00
#PBS -l select=1:ncpus=64:ompthreads=1:mem=50GB
#PBS -l debug=true


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

source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
export evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)


############################################################
# For dev testing
############################################################
export envir=prod
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export VERIF_CASE=radar
export MODELNAME=${COMPONENT}
export EVAL_PERIOD=last31days
export LINE_TYPE=nbrcnt
export job=${PBS_JOBNAME:-jevs_${STEP}_${MODELNAME}_${VERIF_CASE}_${LINE_TYPE}}
export jobid=$job.${PBS_JOBID:-$$}
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver_2d/$STEP/$COMPONENT
export nproc=64
export ncpu=64
############################################################

export vhr=${vhr:-00}

export SENDMAIL=${SENDMAIL:-YES}
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-NO}
export USE_CFP=${USE_CFP:-YES}

source $HOMEevs/dev/drivers/set_MAILTO.sh

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/JEVS_PLOTS_CAM

fi


######################################################################
# Purpose: This job generates radar NBRCNT verification graphics
#          for the CAM component (deterministic and ensemble CAMs)
#          over the last 31 days
######################################################################

