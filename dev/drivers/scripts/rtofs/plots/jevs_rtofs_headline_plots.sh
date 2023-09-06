#PBS -N jevs_rtofs_headline_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
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
module load prod_envir/${prod_envir_ver}

# specify environment variables
export NET=evs
export STEP=plots
export COMPONENT=rtofs
export RUN=headline

source $HOMEevs/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

# set up VDATE and COMIN and COMOUT
export VDATE=$(date --date="4 days ago" +%Y%m%d)

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMINstats=$COMIN/stats/$COMPONENT
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMOUTplots=$COMOUT/$STEP/$COMPONENT/$COMPONENT.$VDATE
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/logos
export USHevs=$HOMEevs/ush/$COMPONENT
export CONFIGevs=$HOMEevs/parm/metplus_config/$COMPONENT

# call j-job
$HOMEevs/jobs/$COMPONENT/$STEP/JEVS_RTOFS_HEADLINE_PLOTS

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to create headline
#    score plots for RTOFS forecast verifications using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
######################################################################
#%end
