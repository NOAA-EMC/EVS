#!/bin/bash

#PBS -N jevs_narre_past90days_plots
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:10:00
#PBS -l place=vscatter,select=1:ncpus=8:mem=1GB
#PBS -l debug=true


export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver


export met_v=${met_ver:0:4}

export envir=prod

export NET=evs
export STEP=plots
export COMPONENT=narre
export RUN=atmos
export VERIF_CASE=grid2obs
export MODELNAME=narre

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export KEEPDATA=NO

export cyc=00
#export VDATE=20221031
export past_days=90

export run_mpi=yes

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
#export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}


${HOMEevs}/jobs/narre/plots/JEVS_NARRE_PLOTS
