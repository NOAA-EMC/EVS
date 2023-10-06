#PBS -N jevs_global_det_wave_grid2obs_plots_90days_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=10:mem=30GB
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export KEEPDATA=YES
export SENDDBN=NO
export job=${PBS_JOBNAME:-jevs_global_det_wave_grid2obs_plots_90days}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export cyc=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/global_det/global_det_plots.sh

export machine=WCOSS2
export USE_CFP=YES
export nproc=10

export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=wave
export VERIF_CASE=grid2obs
export NDAYS=90

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver
export COMROOT=/lfs/h2/emc/ptmp/${USER}

# CALL executable job script here
${HOMEevs}/jobs/JEVS_GLOBAL_DET_PLOTS

#########################################################################
# Purpose: This does the plotting work for the global deterministic
#          wave grid-to-obs for last 90 days
#########################################################################
