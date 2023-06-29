#PBS -N jevs_jma_atmos_grid2grid_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=31:ompthreads=1:mem=5GB
#PBS -l debug=true
#PBS -V

set -x

export model=evs

############################################################
# For dev testing
############################################################
cd $PBS_O_WORKDIR
module reset
#export HOMEevs=$(eval "cd ../../../;pwd")
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export evs_ver=$evs_ver
export envir=dev
export RUN_ENVIR=nco
export SENDCOM=YES
export KEEPDATA=NO
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_global_det_atmos_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_jma_atmos_grid2grid_stats}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)
############################################################

############################################################
# Load modules
############################################################
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
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

# Set machine
export machine=WCOSS2

# Set job information
export USE_CFP=YES
export nproc=31

# Set cycle
export cyc=00

# Set mail list
export maillist='geoffrey.manikin@noaa.gov,mallory.row@noaa.gov'

# Set verification information
export NET=evs
export STEP=stats
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=grid2grid
export MODELNAME=jma

# Set COM paths
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
#export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER/evs_global_det_atmos_test/$envir/com
export COMIN=$COMROOT/$NET/$evs_ver
export COMINjma=$COMIN/prep/$COMPONENT/$RUN
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/$STEP/$COMPONENT
#export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/evs_global_det_atmos_test/$envir/com/$NET/$evs_ver/$STEP/$COMPONENT

# Set config file
export config=$HOMEevs/parm/evs_config/global_det/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

# CALL executable job script here
$HOMEevs/jobs/global_det/stats/JEVS_GLOBAL_DET_STATS

######################################################################
# Purpose: This does the statistics work for the global deterministic
#          atmospheric grid-to-grid component for JMA
######################################################################
