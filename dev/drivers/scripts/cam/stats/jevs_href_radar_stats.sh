#!/bin/bash
#PBS -N jevs_href_radar_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=0:30:00
#PBS -l place=vscatter,select=1:ncpus=18:mem=500GB
#PBS -l debug=true
#PBS -V


set -x

cd $PBS_O_WORKDIR

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/save/${USER}/EVS
source $HOMEevs/versions/run.ver


############################################################
# Load modules
############################################################
module reset

export HPC_OPT=/apps/ops/para/libs
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
module load cfp/${cfp_ver}
module load gsl/${gsl_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}

module list


############################################################
# For dev testing
############################################################
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=YES
export NET=evs
export STEP=stats
export COMPONENT=cam
export RUN=atmos
export VERIF_CASE=radar
export MODELNAME=href
export modsys=href
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}
export COMINmrms=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/prep/$COMPONENT
export COMINspcotlk=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/prep/$COMPONENT
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export USE_CFP=YES
export nproc=9

export MET_bin_exec=bin
export metplus_verbosity=DEBUG
export met_verbosity=2
export log_met_output_to_metplus=yes
############################################################

export cyc=${cyc:-${cyc}}

export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-NO}
export KEEPDATA=${KEEPDATA:-NO}

export maillist=logan.dawson@noaa.gov
export maillist=${maillist:-'logan.dawson@noaa.gov,geoffrey.manikin@noaa.gov'}

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/cam/stats/JEVS_CAM_STATS

fi


######################################################################
# Purpose: This job generates radar verification statistics
#          for the HREF
######################################################################

