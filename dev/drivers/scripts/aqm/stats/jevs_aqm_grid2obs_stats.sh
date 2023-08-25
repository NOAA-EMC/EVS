#PBS -N jevs_aqm_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l select=1:ncpus=1:mem=2GB
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

###%include <head.h>
###%include <envir-p1.h>

############################################################
# Load modules
############################################################

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/aqm/aqm_stats.sh

export cyc
echo $cyc
export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=aqm
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=aqm
export modsys=aqm
export mod_ver=${aqm_ver}

export config=$HOMEevs/parm/evs_config/aqm/config.evs.aqm.prod
source $config

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export COMOUT=${COMIN}/${STEP}/${COMPONENT}

## export COMINaqm=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export cycle=t${cyc}z

export COMOUT=$COMIN/${STEP}/${COMPONENT}
export COMOUTsmall=${COMOUT}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}
export COMOUTfinal=${COMOUT}/${MODELNAME}.${VDATE}
########################################################################

export maillist=${maillist:-'ho-chun.huang@noaa.gov,geoffrey.manikin@noaa.gov'}
## export maillist=${maillist:-'perry.shafran@noaa.gov,geoffrey.manikin@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/aqm/stats/JEVS_AQM_STATS

fi

######################################################################
## Purpose: This job will generate the grid2obs statistics for the AQM
##          model and generate stat files.
#######################################################################
#



