#!/bin/bash

#PBS -N jevs_global_ens_profile1_past31days_plots
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:30:00
#PBS -l place=vscatter,select=10:ncpus=88:mem=300GB
#PBS -l debug=true


export OMP_NUM_THREADS=1

#export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/gitworkspace/EVS

source $HOMEevs/versions/run.ver


export NET=evs
export STEP=plots
export COMPONENT=global_ens
export RUN=atmos
export VERIF_CASE=profile1
export MODELNAME=gefs



module reset

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh


export MET_bin_exec=bin



export envir=prod


export KEEPDATA=YES

export cyc=00
#export VDATE=20230115
export past_days=31

export met_v=${met_ver:0:4}
export valid_time=both

#export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMIN=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/$NET/$evs_ver
#export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}


${HOMEevs}/jobs/global_ens/plots/JEVS_GLOBAL_ENS_PLOTS
