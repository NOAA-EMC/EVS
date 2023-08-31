#PBS -N jevs_global_det_atmos_ukmet_grid2obs_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A EVS-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=14:ompthreads=1:mem=25GB
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export KEEPDATA=NO
export RUN_ENVIR=nco
export job=${PBS_JOBNAME:-jevs_global_det_atmos_ukmet_grid2obs_stats}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export cyc=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/global_det/global_det_stats.sh

export machine=WCOSS2
export USE_CFP=YES
export nproc=14

export maillist='geoffrey.manikin@noaa.gov,mallory.row@noaa.gov'

export envir=dev
export NET=evs
export STEP=stats
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=ukmet

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOTROOTROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=$COMROOT/$NET/$evs_ver
export COMINukmet=$COMIN/prep/$COMPONENT/$RUN
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT

export config=$HOMEevs/parm/evs_config/global_det/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

# CALL executable job script here
$HOMEevs/jobs/global_det/stats/JEVS_GLOBAL_DET_STATS

######################################################################
# Purpose: This does the statistics work for the global deterministic
#          atmospheric grid-to-observations component for UKMET
######################################################################
