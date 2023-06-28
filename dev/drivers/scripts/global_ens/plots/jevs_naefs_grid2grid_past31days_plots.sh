#!/bin/bash

#PBS -N jevs_naefs_grid2grid_past31days_plots
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=24:mem=100GB
#PBS -l debug=true


export OMP_NUM_THREADS=1

export evs_ver=v1.0
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

source $HOMEevs/versions/run.ver

module reset
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load cray-pals/${craypals_ver}
module load prod_envir/${prod_envir_ver}
module load prod_util/${prod_util_ver}
module load cfp/${cfp_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load udunits/${udunits_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
export MET_bin_exec=bin

module list


export envir=prod

export NET=evs
export STEP=plots
export COMPONENT=global_ens
export RUN=atmos
export VERIF_CASE=grid2grid
export MODELNAME=naefs

export KEEPDATA=YES

export cyc=00
#export VDATE=20221218
export past_days=31

export met_v=${met_ver:0:4}

export valid_time=both

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
#export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/ptmp/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

${HOMEevs}/jobs/global_ens/plots/JEVS_GLOBAL_ENS_PLOTS
