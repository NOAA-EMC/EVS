#PBS -N jevs_mesoscale_sref_precip_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter,select=1:ncpus=28:mem=30GB
#PBS -l debug=true

set -x
export OMP_NUM_THREADS=1

export NET=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export envir=prod
export STEP=stats
export COMPONENT=mesoscale
export RUN=atmos
export VERIF_CASE=precip
export MODELNAME=sref

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export KEEPDATA=YES
export SENDMAIL=YES
export SENDCOM=YES

export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export run_mpi=yes

export MAILTO='andrew.benjamin@noaa.gov,binbin.zhou@noaa.gov'

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else
 ${HOMEevs}/jobs/JEVS_MESOSCALE_STATS
fi

