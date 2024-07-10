#PBS -N jevs_global_det_atmos_long_term_plots_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=shared,select=1:ncpus=1
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export KEEPDATA=YES
export job=${PBS_JOBNAME:-jevs_global_det_atmos_long_term_plots}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export vhr=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/global_det/global_det_plots.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export machine=WCOSS2

export evs_run_mode=production
export envir=dev
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=long_term

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver_2d/$STEP/$COMPONENT/$RUN

export VDATEYYYY=$(date -d "1 month ago" '+%Y')
export VDATEmm=$(date -d "1 month ago" '+%m')

# CALL executable job script here
$HOMEevs/jobs/JEVS_GLOBAL_DET_ATMOS_LONG_TERM_PLOTS

######################################################################
# Purpose: This does the plotting work for the global deterministic
#          atmospheric long term stats
######################################################################
