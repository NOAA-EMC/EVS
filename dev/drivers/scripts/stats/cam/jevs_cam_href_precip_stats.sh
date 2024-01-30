#PBS -N jevs_cam_href_precip_stats
#PBS -j oe
#PBS -q dev
#PBS -S /bin/bash
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=88:mem=60GB
#PBS -l debug=true

set -x 

export OMP_NUM_THREADS=1

## 3x7 conus(ccpa) + 3x7 alaska(mrms) + 2 snow = 44 jobs 

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export NET=evs
export STEP=stats
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=precip
export MODELNAME=href
export KEEPDATA=YES
export SENDMAIL=YES

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export vhr=00

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d
export envir=prod
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver_2d/$STEP/$COMPONENT
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}


export prepare=yes
export run_mpi=yes
export verif_precip=yes
export verif_snowfall=yes

export gather=yes

export MAILTO='alicia.bentley@noaa.gov,binbin.zhou@noaa.gov'

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else
  ${HOMEevs}/jobs/JEVS_CAM_STATS
fi

