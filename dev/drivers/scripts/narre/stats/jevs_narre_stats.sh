#!/bin/bash 

#PBS -N jevs_narre_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:45:00
#PBS -l place=vscatter,select=1:ncpus=16:mem=500GB
#PBS -l debug=true
#PBS -V

set -x

export OMP_NUM_THREADS=1

export evs_ver=v1.0
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
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
export MET_bin_exec=bin

export KEEPDATA=YES

export cyc=00

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

  ${HOMEevs}/jobs/narre/stats/JEVS_NARRE_STATS

fi
