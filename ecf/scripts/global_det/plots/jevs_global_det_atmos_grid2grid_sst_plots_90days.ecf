#PBS -N jevs_global_det_atmos_grid2grid_sst_plots_90days_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=vscatter,select=1:ncpus=32:ompthreads=1:mem=30GB
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
export job=${PBS_JOBNAME:-jevs_global_det_atmos_grid2grid_sst_plots_90days}
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
export nproc=32

# Set cycle
export cyc=00

# Set verification information
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=atmos
export VERIF_CASE=grid2grid
export VERIF_TYPE=sst
export NDAYS=90

# Set COM paths
export PDYm1=$(date -d "24 hours ago" '+%Y%m%d')
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
#export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER/evs_global_det_atmos_test/$envir/com
export COMIN=$COMROOT/$NET/$evs_ver
export COMINcfs=$COMIN/stats/$COMPONENT/cfs
export COMINgfs=$COMIN/stats/$COMPONENT/gfs
export COMINcmc=$COMIN/stats/$COMPONENT/cmc
export COMINecmwf=$COMIN/stats/$COMPONENT/ecmwf
export COMINfnmoc=$COMIN/stats/$COMPONENT/fnmoc
export COMINimd=$COMIN/stats/$COMPONENT/imd
export COMINjma=$COMIN/stats/$COMPONENT/jma
export COMINukmet=$COMIN/stats/$COMPONENT/ukmet
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/$RUN.$PDYm1

# Set config file
export config=$HOMEevs/parm/evs_config/global_det/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${VERIF_TYPE}
echo $config

# CALL executable job script here
$HOMEevs/jobs/global_det/plots/JEVS_GLOBAL_DET_PLOTS

######################################################################
# Purpose: This does the plotting work for the global deterministic
#          atmospheric grid-to-grid sst for past 90 days
######################################################################
