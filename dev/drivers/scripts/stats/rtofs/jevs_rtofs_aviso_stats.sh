#PBS -N jevs_rtofs_aviso_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A EVS-DEV
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=1:mem=500GB
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
export STEP=stats
export RUN=aviso
export VERIF_CASE=grid2grid
export COMPONENT=rtofs

source $HOMEevs/dev/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

export evs_ver=v1.0.0
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

# set up COMIN and COMOUT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export maillist=${maillist:-'alicia.bentley@noaa.gov,samira.ardani@noaa.gov'}

# call j-job
$HOMEevs/jobs/JEVS_RTOFS_STATS

######################################################################
# Purpose: The job and task scripts work together to create stat
#          files for RTOFS forecast verification using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
######################################################################
