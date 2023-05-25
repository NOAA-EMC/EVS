#PBS -N jevs_global_det_atmos_headline_plots_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l select=1:ncpus=1:mem=35GB
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
export job=${PBS_JOBNAME:-jevs_global_det_atmos_headline_plots}
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
export MET_bin_exec=bin
module list

# Set machine
export machine=WCOSS2

# Set cycle
export cyc=00

# Set verification information
export NET=evs
export STEP=plots
export COMPONENT=global_det
export RUN=headline

# Set COM paths
export PDYm1=$(date -d "24 hours ago" '+%Y%m%d')
export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=$COMROOT/$NET/$evs_ver
export COMINdailystats=$COMIN/stats/$COMPONENT
export COMINyearlystats=$COMIN/stats/$COMPONENT/long_term/annual_means
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/$RUN.$PDYm1

# CALL executable job script here
$HOMEevs/jobs/global_det/plots/JEVS_GLOBAL_DET_ATMOS_HEADLINE_PLOTS

######################################################################
# Purpose: This does the plotting work for the global deterministic
#          atmospheric grid-to-grid headline scores
######################################################################
