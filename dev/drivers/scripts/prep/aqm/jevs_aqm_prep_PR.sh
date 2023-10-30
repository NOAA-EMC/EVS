#PBS -N jevs_aqm_prep_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
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

export evs_ver=v1.0.0
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/aqm/aqm_prep.sh

export vhr=00
echo $vhr
export NET=evs
export STEP=prep
export COMPONENT=aqm
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=aqm
export modsys=aqm
export mod_ver=${aqm_ver}
export envir=prod

export config=$HOMEevs/parm/evs_config/aqm/config.evs.aqm.prod
source $config

########################################################################
## The following setting is for parallel test and need to be removed for operational code
########################################################################
## USe this BEFORE the NCO AQMv7 30 day IT Test
export COMINaqm=/lfs/h2/emc/ptmp/jianping.huang/emc.para/com/aqm/v7.0
## USe this AFTER NCO starts the AQMv7 30 day IT Test
## export COMINaqm=/lfs/h1/ops/para/com/aqm/v7.0
#
#
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver_2d}

#
export KEEPDATA=YES
export SENDMAIL=YES
#
export maillist=${maillist:-'ho-chun.huang@noaa.gov,alicia.bentley@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/JEVS_AQM_PREP

fi

######################################################################
## Purpose: This job will generate the grid2obs statistics for the AQM
##          model and generate stat files.
#######################################################################
#



