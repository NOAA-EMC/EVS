#PBS -N jevs_plots_cam_firewxnest_grid2obs_last31days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=shared,select=1:ncpus=1:mem=50GB
#PBS -l debug=true

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver


############################################################
# Load modules
############################################################
set -x

module reset
module load prod_envir/${prod_envir_ver}

export envir=prod
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=NO
export SENDMAIL=YES
export SENDDBN=NO

export vhr=00
export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=firewxnest

source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export job=${PBS_JOBNAME:-jevs_${STEP}_${MODELNAME}_${VERIF_CASE}}
export jobid=$job.${PBS_JOBID:-$$}

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/ptmp/$USER/$NET/$evs_ver_2d/$STEP/$COMPONENT

# CALL executable job script here
$HOMEevs/jobs/JEVS_PLOTS_CAM

######################################################################
## Purpose: This job will generate the grid2obs plots for the RRFS_FIREWXNEST
##          and other models over the firewxnest domain and generate plots tar files.
#######################################################################
#
exit

