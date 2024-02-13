#PBS -N jevs_global_ens_headline_gefs_grid2grid_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=shared,select=1:ncpus=1:mem=5GB
#PBS -l debug=true

#************************************************************************
#Note: (1) This headline plot generation driver script should be run 
#           on Jan 16th of each year. 
#      (2) If run it on the othe day, set "export VDATE=YYYY0116" in this file
#          But must run it after 16th in Jan
#      (3) For testing  generation of plot over incompleted days 
#          (non-entire year), it can be run on any day. But should set
#          follwoing "export run_entire_yea=no". See below.        
#************************************************************************

set -x
export OMP_NUM_THREADS=1
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver

export envir=prod
export NET=evs
export RUN=headline
export STEP=plots
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export KEEPDATA=YES
export SENDDBN=NO

export vhr=00
export run_mpi=no

#************************************************************************
# Note (1):
# If just for testing, run_entire_year is set to "no"
#    In this case, the plot will cover all days bwetween Jan 1 and VDATE
# Note (2):
# If calculate_acc0p6_days=no, the calculation of day when ACC drops to 0.6 
#    will not be executed
# ***********************************************************************
export run_entire_year=yes
export calculate_acc0p6_days=yes


export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export SENDMAIL=YES 
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

${HOMEevs}/jobs/JEVS_GLOBAL_ENS_PLOTS
