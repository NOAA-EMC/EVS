#PBS -N jevs_cam_href_severe_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=0:30:00
#PBS -l select=1:ncpus=5:mem=500MB
#PBS -l debug=true
#PBS -V


set -x

cd $PBS_O_WORKDIR



############################################################
# Load modules
############################################################

module reset

export model=evs
export NET=evs
export STEP=stats
export COMPONENT=cam
export RUN=atmos

export HOMEevs=/lfs/h2/emc/vpppg/save/${USER}/EVS
source $HOMEevs/versions/run.ver

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

############################################################
# For dev testing
############################################################
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=YES
export VERIF_CASE=severe
export MODELNAME=href
export modsys=href
export job=${PBS_JOBNAME:-jevs_${COMPONENT}_${MODELNAME}_${VERIF_CASE}_${STEP}_${cyc}}
export jobid=$job.${PBS_JOBID:-$$}
export COMINfcst=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/prep/$COMPONENT
export COMINspclsr=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/prep/$COMPONENT
export COMINspcotlk=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/prep/$COMPONENT
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
############################################################

export cyc=${cyc:-${cyc}}

export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-NO}

export maillist=${maillist:-'logan.dawson@noaa.gov,geoffrey.manikin@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/cam/stats/JEVS_CAM_STATS

fi


######################################################################
# Purpose: This job generates severe verification statistics
#          for the HREF
######################################################################

