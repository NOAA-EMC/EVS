#PBS -N jevs_aqm_prep_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=02:30:00
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

source $HOMEevs/modulefiles/aqm/aqm_prep.sh

export cyc=00
echo $cyc
export NET=evs
export STEP=prep
export COMPONENT=aqm
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=aqm
export modsys=aqm
export mod_ver=${aqm_ver}

export config=$HOMEevs/parm/evs_config/aqm/config.evs.aqm.prod
source $config

########################################################################
## The following setting is for parallel test and need to be removed for operational code
########################################################################
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export cycle=t${cyc}z

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver}/${STEP}/${COMPONENT}/${RUN}

#
export KEEPDATA=NO
#
########################################################################
## VDATE = ${PDYm2} is okay after 01Z today for the default
##               "export airnow_hourly_type=aqobs"
##         VDATE = ${PDYm3} is currrently set as default in
###              /EVS/jobs/aqm/prep/JEVS_AQM_PREP
## VDATE = ${PDYm3} is needed after 00Z and before 01Z today for a
##         option that is not "aqobs", i.e., one is using hourly input
##         HourlyData_yyyymmddhh.dat but not the HourlAQObs_yyyymmddhh.dat
########################################################################
#
## export VDATE=20230513
#
########################################################################

export maillist=${maillist:-'ho-chun.huang@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/aqm/prep/JEVS_AQM_PREP

fi

######################################################################
## Purpose: This job will generate the grid2obs statistics for the AQM
##          model and generate stat files.
#######################################################################
#



