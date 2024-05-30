#PBS -N jevs_rtofs_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=06:00:00
#PBS -l place=shared,select=1:ncpus=1:mem=200GB
#PBS -l debug=true

############################################################
# Load modules
############################################################
set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source $HOMEevs/versions/run.ver

module reset
module load prod_envir/${prod_envir_ver}

export KEEPDATA=YES
export SENDMAIL=YES

# specify environment variables
export envir=prod
export NET=evs
export STEP=prep
export COMPONENT=rtofs

source $HOMEevs/dev/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

# set up COMIN and COMOUT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export MAILTO=${MAILTO:-'alicia.bentley@noaa.gov,samira.ardani@noaa.gov'}

# call j-job
$HOMEevs/jobs/JEVS_RTOFS_PREP

######################################################################
# Purpose: The job and task scripts work together to pre-process RTOFS
#          forecast data into the same spatial and temporal scales
#          as validation data.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
######################################################################
