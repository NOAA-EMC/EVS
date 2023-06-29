#!/bin/bash
#PBS -N jevs_hireswarwmem2_grid2obs_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=10:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1
#PBS -l debug=true
#PBS -V

set -x
export model=evs
module reset
export machine=WCOSS2

# ECF Settings
export RUN_ENVIR=nco
export SENDECF=YES
export SENDCOM=YES
export KEEPDATA=YES
export SENDDBN=YES
export SENDDBN_NTC=
export job=${PBS_JOBNAME:-jevs_hireswarwmem2_grid2obs_stats}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export USE_CFP=YES
export nproc=128

# General Verification Settings
export NET="evs"
export STEP="stats"
export COMPONENT="cam"
export RUN="atmos"
export VERIF_CASE="grid2obs"
export MODELNAME="hireswarwmem2"

# EVS Settings
export HOMEevs="/lfs/h2/emc/vpppg/noscrub/$USER/EVS"
export HOMEevs=${HOMEevs:-${PACKAGEROOT}/evs.${evs_ver}}
export config=$HOMEevs/parm/evs_config/cam/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

# Load Modules
source $HOMEevs/versions/run.ver

source /usr/share/lmod/lmod/init/sh
module reset
export HPC_OPT=/apps/ops/prod/libs
export MET_bin_exec="bin"
module load cray-pals/${craypals_ver}
module load PrgEnv-intel/${PrgEnv_intel_ver}
module load craype/${craype_ver}
module load intel/${intel_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load udunits/${udunits_ver}
module load gsl/${gsl_ver}
module load hdf5/${hdf5_ver}
module load python/${python_ver}
module load netcdf/${netcdf_ver}
module load nco/${nco_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load cdo/${cdo_ver}
module use /apps/ops/prod/libs/modulefiles/compiler/intel/${intel_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
export MET_PLUS_PATH="/apps/ops/prod/libs/intel/${intel_ver}/metplus/${metplus_ver}"
export MET_PATH="/apps/ops/prod/libs/intel/${intel_ver}/met/${met_ver}"
export MET_CONFIG="${MET_PLUS_PATH}/parm/met_config"
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH

# Developer Settings
export DATA=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMINccpa=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/prep/$COMPONENT
export COMINmrms=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/prep/$COMPONENT
export COMINspcotlk=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/prep/$COMPONENT
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/$STEP/$COMPONENT
export FIXevs="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix"
export cyc=$(date -d "today" +"%H")
export maillist="marcel.caron@noaa.gov"

# Job Settings and Run
. ${HOMEevs}/jobs/cam/stats/JEVS_CAM_STATS
