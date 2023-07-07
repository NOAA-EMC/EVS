#PBS -N jevs_global_det_atmos_grid2obs_sfc_plots_90days_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter:exclhost,select=5:ncpus=128:ompthreads=1:mem=200GB
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export RUN_ENVIR=nco
export SENDCOM=YES
export KEEPDATA=NO
export job=${PBS_JOBNAME:-jevs_global_det_atmos_grid2obs_sfc_plots_90days}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export cyc=00

module reset
source $HOMEevs/versions/run.ver
source $HOMEevs/modulefiles/global_det/global_det_plots.sh

export machine=WCOSS2
export USE_CFP=YES
export nproc=128

export envir=dev
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=grid2obs
export VERIF_TYPE=sfc
export NDAYS=90

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=$COMROOT/$NET/$evs_ver
export VDATE_END=$(date -d "24 hours ago" '+%Y%m%d')
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/$RUN.$VDATE_END

# Set config file
export config=$HOMEevs/parm/evs_config/global_det/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${VERIF_TYPE}
echo $config

# CALL executable job script here
$HOMEevs/jobs/global_det/plots/JEVS_GLOBAL_DET_PLOTS

######################################################################
# Purpose: This does the plotting work for the global deterministic
#          atmospheric grid-to-observations sfc for past 90 days
######################################################################
