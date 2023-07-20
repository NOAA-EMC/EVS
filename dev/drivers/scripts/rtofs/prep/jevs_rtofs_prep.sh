#PBS -N jevs_rtofs_prep
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

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/evs_rtofs_module/EVS
source $HOMEevs/versions/run.ver

module reset

# specify environment variables
export NET=evs
export STEP=prep
export COMPONENT=rtofs

source $HOMEevs/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

# set up VDATE and COMIN and COMOUT
export VDATE=$(date --date="2 days ago" +%Y%m%d)

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMINobs=/lfs/h1/ops/dev/dcom
export COMINrtofs=/lfs/h1/ops/$envir/com/$COMPONENT/${rtofs_ver}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMOUTprep=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}/$STEP/$COMPONENT
#export DATA=/lfs/h2/emc/ptmp/$USER/$NET/${evs_ver}
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/cdo_grids
export USHevs=$HOMEevs/ush/$COMPONENT
export CONFIGevs=$HOMEevs/parm/metplus_config/$COMPONENT

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export maillist=${maillist:-'geoffrey.manikin@noaa.gov,lichuan.chen@noaa.gov'}

# call j-job
$HOMEevs/jobs/$COMPONENT/$STEP/JEVS_RTOFS_PREP

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to pre-process RTOFS
#          forecast data into the same spatial and temporal scales
#          as validation data.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
######################################################################
#%end
