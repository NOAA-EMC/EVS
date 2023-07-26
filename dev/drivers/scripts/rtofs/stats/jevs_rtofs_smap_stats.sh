#PBS -N jevs_rtofs_smap_stats
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

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/evs_rtofs_module/EVS
source $HOMEevs/versions/run.ver

module reset

# specify environment variables
export NET=evs
export STEP=stats
export RUN=smap
export RUNupper=SMAP
export VERIF_CASE=grid2grid
export VAR=sss
export COMPONENT=rtofs

source $HOMEevs/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

# set up VDATE and COMIN and COMOUT
export VDATE=$(date --date="2 days ago" +%Y%m%d)

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMINobs=/lfs/h1/ops/dev/dcom
export COMINfcst=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}/prep/$COMPONENT
export COMINclimo=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/climos/$COMPONENT
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMOUTfinal=$COMOUT/$STEP/$COMPONENT/$COMPONENT.$VDATE
#export DATA=/lfs/h2/emc/ptmp/$USER/$NET/${evs_ver}
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export CONFIGevs=$HOMEevs/parm/metplus_config/$COMPONENT
export ARCHevs=/lfs/h2/emc/vpppg/noscrub/$USER/stat_archive/RTOFS

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export maillist=${maillist:-'geoffrey.manikin@noaa.gov,lichuan.chen@noaa.gov'}

# call j-job
$HOMEevs/jobs/$COMPONENT/$STEP/JEVS_RTOFS_STATS

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to create stat
#          files for RTOFS forecast verification using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
######################################################################
#%end
