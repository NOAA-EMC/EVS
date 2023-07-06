#PBS -N jevs_aqm_grid2obs_plots_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
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
module reset

source $HOMEevs/versions/run.ver

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
export mod_ver=${aqm}

export MET_bin_exec=bin

export config=$HOMEevs/parm/evs_config/aqm/config.evs.aqm.prod
source $config

########################################################################
## The following setting is for parallel test and need to be removed for operational code
########################################################################
##
## Instruction for Pull-Request testing
##     point COMIN to personal directory
##     output can be found at $COMOUTplot (defined in JEVS_AQM_PLOTS based on COMIN setting below)
## 
## (1) input from the pull-request stats output (see example (a) below)
## or (2) Use EVSv1.0 parallel stats archive (see example (b) below)
##
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=YES
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export cycle=t${cyc}z
#

##
## Note plot step in general needs previous 31 days of data (it is okay for missing days)
##
## Example a
## setting to use stats generated from pull-request stats testing
## USE THE SAME "export COMIN=" as in stats step during pull-request testing
## export COMINaqm=${COMIN}/stats/${COMPONENT}/${MODELNAME}
#
## Example b
## setting to use stats from EVSv1.0 parallel output directory
#
## setting to produce output to personal directory
## export COMIN=/lfs/h2/emc/physics/noscrub/$USER/${NET}/${evs_ver}
## export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export COMIN=/lfs/h2/emc/ptmp/$USER/${NET}/${evs_ver}
mkdir -p ${COMIN}
export COMINaqm=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/evs/v1.0/stats/aqm/aqm

export COMOUT=${COMIN}/${STEP}/${COMPONENT}
#
## export KEEPDATA=NO
#
########################################################################

export maillist=${maillist:-'perry.shafran@noaa.gov,geoffrey.manikin@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/aqm/plots/JEVS_AQM_PLOTS

fi

######################################################################
## Purpose: This job will generate the grid2obs statistics for the NAM_FIREWXNEST
##          model and generate stat files.
#######################################################################
#
exit

