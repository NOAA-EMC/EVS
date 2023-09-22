#PBS -N jevs_glwu_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=06:00:00
#PBS -l select=1:ncpus=1:mem=500GB
#PBS -l debug=true

#%include <head.h>
#%include <envir-p1.h>

############################################################
# Load modules
############################################################
set -x

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source $HOMEevs/versions/run.ver

module reset
module load prod_envir/$prod_envir_ver
module list

# specify environment variables
export NET=evs
export STEP=prep
export COMPONENT=glwu

# set up VDATE and COMIN and COMOUT
source $HOMEevs/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh
export VDATE=$(date --date="1 days ago" +%Y%m%d)
#export VDATE=20230207

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMINobs=/lfs/h1/ops/dev/dcom
#export COMINglwu=/lfs/h1/ops/$envir/com/$COMPONENT/${glwu_ver}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMOUTprep=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}/$STEP/$COMPONENT
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export maillist=${maillist:-'alicia.bentley@noaa.gov,samira.ardani@noaa.gov'}

# call j-job
$HOMEevs/jobs/$COMPONENT/$STEP/JEVS_GLWU_PREP

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to pre-process NDBC
#          data for GLWU forecast verifications.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
# Modified by: Samira Ardani
######################################################################
#%end

