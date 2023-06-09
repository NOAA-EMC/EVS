#!/bin/bash
#PBS -N jevs_rtma_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l select=1:ncpus=1:mem=2GB
#PBS -l debug=true
#PBS -V
 
set -x

cd $PBS_O_WORKDIR

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

############################################################
## Load modules
#############################################################

module reset
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load gsl/${gsl_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load prod_util/${produtil_ver}
module load prod_envir/${prodenvir_ver}


############################################################
## For dev testing
#############################################################

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export KEEPDATA=YES
export envir=prod
export NET=evs
export STEP=stats
export COMPONENT=analyses
export RUN=atmos
export VERIF_CASE=grid2obs

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/${NET}/${evs_ver}
export COMOUT=$COMIN/${STEP}/${COMPONENT}
export COMOUTsmall=${COMOUT}/${RUN}.${VDATE}/${MODELNAME}/${VERIF_CASE}
export COMOUTfinal=${COMOUT}/${MODELNAME}.${VDATE}

export MET_bin_exec=bin
export metplus_verbosity=DEBUG
export met_verbosity=2
export log_met_output_to_metplus=yes

export cyc
echo $cyc

export mod_ver=${rtma_ver}
export modsys=rtma
export MODELNAME=rtma

export maillist=perry.shafran@noaa.gov

export config=$HOMEevs/parm/evs_config/analyses/config.evs.rtma.prod
source $config

# CALL executable job script here
$HOMEevs/jobs/analyses/stats/JEVS_ANALYSES_STATS

######################################################################
## Purpose: This job will generate the grid2obs statistics for the NAM_FIREWXNEST
##          model and generate stat files.
#######################################################################
#
exit
