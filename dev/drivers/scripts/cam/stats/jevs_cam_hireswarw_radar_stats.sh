#PBS -N jevs_cam_hireswarw_radar_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=0:30:00
#PBS -l place=vscatter,select=1:ncpus=12:mem=500GB
#PBS -l debug=true
#PBS -V


set -x

cd $PBS_O_WORKDIR


############################################################
# Load modules
############################################################


export model=evs
export NET=evs
export STEP=stats
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
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export COMROOT=/lfs/h2/emc/vpppg/noscrub/${USER}
export KEEPDATA=NO
export VERIF_CASE=radar
export MODELNAME=hireswarw
export modsys=hiresw
export job=${PBS_JOBNAME:-jevs_${COMPONENT}_${MODELNAME}_${VERIF_CASE}_${STEP}_${cyc}}
export jobid=$job.${PBS_JOBID:-$$}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/$STEP/$COMPONENT
export USE_CFP=YES
export nproc=3
############################################################

export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-NO}

export maillist=${maillist:-'marcel.caron@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/cam/stats/JEVS_CAM_STATS

fi


######################################################################
# Purpose: This job generates radar verification statistics
#          for the HiResW ARW
######################################################################

