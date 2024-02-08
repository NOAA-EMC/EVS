#!/bin/bash 

#PBS -N jevs_narre_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:45:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=16:mem=500GB
#PBS -l debug=true
#PBS -V

set -x

export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver


export envir=prod

export NET=evs
export STEP=stats
export COMPONENT=narre
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=narre

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)


export KEEPDATA=YES
export SENDMAIL=YES

export vhr=${vhr:-00}

export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export MAILTO='alicia.bentley@noaa.gov,binbin.zhou@noaa.gov'

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else

  ${HOMEevs}/jobs/JEVS_NARRE_STATS

fi
