#!/bin/bash
#PBS -N jevs_nam_grid2obs_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=4:59:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1:mem=32GB
#PBS -l debug=true
#PBS -V

set -x
  export model=evs
  export machine=WCOSS2

# ECF Settings
# export RUN_ENVIR=nco
  export RUN_ENVIR=emc
  export SENDECF=YES
  export SENDCOM=YES
  export KEEPDATA=YES
  export SENDDBN=YES
  export SENDDBN_NTC=
  export job=${PBS_JOBNAME:-jevs_mesoscale_grid2obs_stats}
  export jobid=$job.${PBS_JOBID:-$$}
  export SITE=$(cat /etc/cluster_name)
  export USE_CFP=YES
  export nproc=128

# General Verification Settings
  export NET="evs"
  export STEP="stats"
  export COMPONENT="mesoscale"
  export RUN="atmos"
  export VERIF_CASE="grid2obs"
  export MODELNAME="nam" 

# export envir="dev"
  export envir="prod"
  export evs_run_mode="standalone"

  export ACCOUNT=VERF-DEV
  export QUEUESERV="dev_transfer"
  export QUEUE="dev"
  export QUEUESHARED="dev_shared"
  export PARTITION_BATCH=""

# EVS Settings
  export HOMEevs="/lfs/h2/emc/vpppg/noscrub/${USER}/verification/EVS"
# export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

# Subdirectories to EVS Home Directory
  export PARMevs=$HOMEevs/parm
  export USHevs=$HOMEevs/ush
  export EXECevs=$HOMEevs/exec
  export FIXevs="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix"
  export SCRIPTSevs=$HOMEevs/scripts
  export MET_PLUS_CONF="${PARMevs}/metplus_config/mesoscale/grid2obs/stats"

# EVS configuration
  export config=$HOMEevs/parm/evs_config/mesoscale/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

# Load Modules

source $HOMEevs/versions/run.ver

source /usr/share/lmod/lmod/init/sh
module reset
export HPC_OPT=/apps/ops/para/libs
export MET_bin_exec="bin"

module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}

module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load udunits/${udunits_ver}
module load gsl/${gsl_ver}
module load nco/${nco_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
module load cdo/${cdo_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

export MET_PLUS_PATH="/apps/ops/para/libs/intel/${intel_ver}/metplus/${metplus_ver}"
export MET_PATH="/apps/ops/para/libs/intel/${intel_ver}/met/${met_ver}"
export MET_CONFIG="${MET_PLUS_PATH}/parm/met_config"
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH

# In production the following will be deleted (DATAROOT will be used instead, which already exists in the environment)
  export DATAROOTtmp=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
  export DATA=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp

# in production the following will be set to yesterday's date
  export VDATE=$(date -d "today -1 day" +"%Y%m%d")

# Developer Settings
  export COMINspcotlk=/lfs/h2/emc/vpppg/noscrub/logan.dawson/evs/v1.0/prep/cam
  export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/$STEP/$COMPONENT
  export COMOUTsmall=${COMOUT}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}

  export cyc=$(date -d "today" +"%H")
  export maillist="roshan.shrestha@noaa.gov,geoffrey.manikin@noaa.gov"

# Job Settings and Run
. ${HOMEevs}/jobs/mesoscale/stats/JEVS_MESOSCALE_STATS

