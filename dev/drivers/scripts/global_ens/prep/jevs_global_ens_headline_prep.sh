#!/bin/bash 
#
#PBS -N jevs_headline_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:05:00
#PBS -l place=vscatter,select=1:ncpus=2:mem=10GB
#PBS -l debug=true


set -x
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
module load cdo/${cdo_ver}
export MET_bin_exec=bin


export NET=evs
export RUN=headline
export STEP=prep
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs

export KEEPDATA=YES

#This var is only for testing, if not set, then run operational 

#export INITDATE=$1
TODAY=`date +%Y%m%d`
yyyymmdd=${TODAY:0:8}
PAST=`$NDATE -48 ${yyyymmdd}01`
export INITDATE=${INITDATE:-${PAST:0:8}}

#export INITDATE=20230514

echo $INITDATE
export cyc=00
export run_mpi=no

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATA=/lfs/h2/emc/stmp/${USER}/evs/tmpnwprd
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'
export gefs_number=20

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

  ${HOMEevs}/jobs/global_ens/prep/JEVS_GLOBAL_ENS_PREP

fi
