#PBS -N jevs_aqm_grid2obs_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l select=1:ncpus=128:mem=500GB
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

source $HOMEevs/modulefiles/aqm/aqm_plots.sh

############################################################
## For dev testing
#############################################################
export cyc=00
export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=aqm
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=aqm
export modsys=aqm
export mod_ver=${aqm_ver}

export config=$HOMEevs/parm/evs_config/aqm/config.evs.aqm.prod
source $config

export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=YES
export SENDMAIL=YES
export SENDDBN=NO
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export cycle=t${cyc}z
#

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export COMINaqm=/lfs/h2/emc/vpppg/noscrub/$USER/evs/v1.0/stats/aqm/aqm

export COMOUT=/lfs/h2/emc/ptmp/$USER/$NET/$evs_ver

export maillist=${maillist:-'perry.shafran@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/JEVS_AQM_PLOTS

fi

######################################################################
## Purpose: This job will generate the grid2obs statistics for the NAM_FIREWXNEST
##          model and generate stat files.
#######################################################################
#
exit

