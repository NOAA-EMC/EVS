#!/bin/bash

#PBS -N jevs_href_precip_spatial_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=2:mem=100GB
#PBS -l debug=true


export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver


export met_v=${met_ver:0:4}

export envir=prod

export NET=evs
export STEP=plots
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=precip_spatial
export MODELNAME=href

module reset
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh
export MET_bin_exec=bin

export KEEPDATA=YES

export cyc=00

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMINspatial=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
#export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}



${HOMEevs}/jobs/cam/plots/JEVS_CAM_PLOTS
