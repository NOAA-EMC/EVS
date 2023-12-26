#PBS -N jevs_rtofs_headline_grid2grid_last90days_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=shared,select=1:ncpus=1:mem=5GB
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
export SENDDBN=NO

# specify environment variables
export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=rtofs
export RUN=headline
export VERIF_CASE=grid2grid

source $HOMEevs/dev/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

# set up COMIN and COMOUT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/ptmp/$USER/$NET/${evs_ver_2d}
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_rtofs_headline_grid2grid_last90days_plots}
export jobid=$job.${PBS_JOBID:-$$}

# call j-job
$HOMEevs/jobs/JEVS_RTOFS_PLOTS

######################################################################
# Purpose: The job and task scripts work together to create plots
#          for RTOFS forecast verification using MET/METplus.
# Author: L. Gwen Chen (lichuan.chen@noaa.gov)
######################################################################
