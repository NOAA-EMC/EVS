#PBS -N jevs_global_det_atmos_headline_plots_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A EVS-DEV
#PBS -l walltime=00:10:00
#PBS -l select=1:ncpus=1:mem=35GB
#PBS -l debug=true
#PBS -V


set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export KEEPDATA=YES
export SENDDBN=NO
export job=${PBS_JOBNAME:-jevs_global_det_atmos_headline_plots}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export vhr=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/global_det/global_det_plots.sh

export evs_ver=v1.0.0
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export machine=WCOSS2

export envir=prod
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=headline

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
today=$(cut -c7-14 ${COMROOT}/date/t${vhr}z)
export VDATE_END=$(finddate.sh $today d-1)
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver_2d/$STEP/$COMPONENT/$RUN.$VDATE_END

# CALL executable job script here
$HOMEevs/jobs/JEVS_GLOBAL_DET_PLOTS

######################################################################
# Purpose: This does the plotting work for the global deterministic
#          atmospheric grid-to-grid headline scores
######################################################################
