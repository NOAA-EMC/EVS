#!/bin/bash

#PBS -N jevs_href_precip_stat
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=88:mem=10GB
#PBS -l debug=true

export OMP_NUM_THREADS=1

## 3x7 conus(ccpa) + 3x7 alaska(mrms) + 2 snow = 44 jobs 
##

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

set -x 

export NET=evs
export STEP=stats
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=precip
export MODELNAME=href
export KEEPDATA=YES

export cyc=00

export COMIN=$COMROOT
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks
export MASKS=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix/masks
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}


export prepare=yes
export run_mpi=yes
export verif_precip=yes
export verif_snowfall=yes

export gather=yes

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else
  ${HOMEevs}/jobs/cam/stats/JEVS_CAM_STATS
fi

