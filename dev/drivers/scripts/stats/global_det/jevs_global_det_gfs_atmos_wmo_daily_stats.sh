#PBS -N jevs_global_det_gfs_atmos_wmo_daily_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1:mem=175GB
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export SENDMAIL=YES
export KEEPDATA=YES
export job=${PBS_JOBNAME:-jevs_global_det_gfs_atmos_wmo_daily_stats}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export vhr=00

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/global_det/global_det_stats.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export machine=WCOSS2
export USE_CFP=YES
export nproc=128

export MAILTO='alicia.bentley@noaa.gov,mallory.row@noaa.gov'

export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=wmo
export MODELNAME=gfs

export temporal="daily"

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d/$STEP/$COMPONENT

# CALL executable job script here
$HOMEevs/jobs/JEVS_GLOBAL_DET_STATS

######################################################################
# Purpose: This does the daily statistics work for the GFS WMO-required
#          verification
######################################################################
