#PBS -N jevs_aqm_stats_00
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
module reset

source $HOMEevs/versions/run.ver

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

export MET_bin_exec=bin

export config=$HOMEevs/parm/evs_config/aqm/config.evs.aqm.prod
source $config

########################################################################
## The following setting is for parallel test and need to be removed for operational code
########################################################################
export DATA=/lfs/h2/emc/ptmp/$USER/EVS/${cyc}_${MODELNAME}

rm -rf $DATA
mkdir -p $DATA
cd $DATA

##
## Instruction for Pull-Request testing
##     point COMIN to personal directory
##     output can be found at $COMOUTfinal (defined in JEVS_AQM_STATS based on COMIN setting below)
## 
## "Stats" needs previous three days' PREP for day3 verification
## Default VDATE is PDYm3
## (1) Repeat pull-request prep step for PDYm3, PDYm4, and PDYm5 and
##     "export COMINaqmproc=" to $COMOUT in jevs_aqm_prep.sh
## or (2) Use EVSv1.0 parallel preps archive, 
##     export COMINaqmproc="export COMINaqmproc=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/evs/v1.0/prep/aqm"
##
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
## export COMIN=/lfs/h2/emc/physics/noscrub/$USER/${NET}/${evs_ver}
export COMOUT=${COMIN}/${STEP}/${COMPONENT}

## export COMINaqm=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

## For aqmv7 NRT runs
## export fcst_input_ver=v7
## export COMINaqm=/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/v7.0

## For aqmv6 restrospective runs
## export fcst_input_ver=v6
## export COMINaqm=/lfs/h2/emc/physics/noscrub/$USER/verification/${MODELNAME}/${envir}

## Need VDATE setting
export cycle=t${cyc}z
setpdy.sh
. ./PDY
#
## export KEEPDATA=NO
#
export VDATE=${PDYm3}
#
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



