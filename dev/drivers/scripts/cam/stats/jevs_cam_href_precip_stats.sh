#PBS -N jevs_cam_href_precip_stats
#PBS -j oe
#PBS -q dev
#PBS -S /bin/bash
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter,select=1:ncpus=88:mem=10GB
#PBS -l debug=true

export OMP_NUM_THREADS=1

## 3x7 conus(ccpa) + 3x7 alaska(mrms) + 2 snow = 44 jobs 
##

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

set -x 

export NET=evs
export STEP=stats
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=precip
export MODELNAME=href
export KEEPDATA=YES

module reset
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export cyc=00

export COMIN=$COMROOT
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks
export MASKS=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}


export prepare=yes
export run_mpi=yes
export verif_precip=yes
export verif_snowfall=yes

export gather=yes

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else
  ${HOMEevs}/jobs/cam/stats/JEVS_CAM_STATS
fi

