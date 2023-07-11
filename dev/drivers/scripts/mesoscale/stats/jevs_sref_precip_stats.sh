#!/bin/bash 

#PBS -N jevs_sref_precip_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:30:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=8:mem=100GB
#PBS -l debug=true

export OMP_NUM_THREADS=1
#Total 2 processes

export evs_ver=v1.0
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export NET=evs

export STEP=stats
export COMPONENT=mesoscale
export RUN=atmos
export VERIF_CASE=precip
export MODELNAME=sref

module reset
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
export MET_bin_exec=bin

export KEEPDATA=YES

export cyc=00

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export run_mpi=yes

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else
 ${HOMEevs}/jobs/mesoscale/stats/JEVS_MESOSCALE_STATS
fi

