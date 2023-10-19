#!/bin/bash 

#PBS -N jevs_mesoscale_sref_precip_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=02:30:00
#PBS -l place=vscatter,select=1:ncpus=8:mem=100GB
#PBS -l debug=true

export OMP_NUM_THREADS=1
#Total 2 processes

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=mesoscale
export RUN=atmos
export VERIF_CASE=precip
export MODELNAME=sref

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export KEEPDATA=YES
export SENDMAIL=YES
export SENDCOM=YES

export cyc=00

export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export run_mpi=yes

export maillist='alicia.bentley@noaa.gov,binbin.zhou@noaa.gov'

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else
 ${HOMEevs}/jobs/JEVS_MESOSCALE_STATS
fi

