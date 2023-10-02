#!/bin/bash

#PBS -N jevs_mesoscale_sref_cnv_past90days_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=vscatter,select=2:ncpus=88:mem=300GB
#PBS -l debug=true


export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver


export met_v=${met_ver:0:4}

export envir=prod

export NET=evs
export STEP=plots
export COMPONENT=mesoscale
export RUN=atmos
export VERIF_CASE=cnv
export MODELNAME=sref

module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export KEEPDATA=YES
export SENDMAIL=YES

export cyc=00
export past_days=90

export run_mpi=yes
export valid_time=both

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMINapcp24mean=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/stats/$COMPONENT
export COMINccpa=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/prep/$COMPONENT/$RUN
export COMINmrms=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/prep/$COMPONENT/$RUN
export COMINspcotlk=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/prep/$COMPONENT/$RUN
export COMOUT=/lfs/h2/emc/stmp/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}


${HOMEevs}/jobs/JEVS_MESOSCALE_PLOTS
