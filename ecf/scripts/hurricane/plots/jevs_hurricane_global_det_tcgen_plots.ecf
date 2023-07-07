#PBS -S /bin/bash
#PBS -N jevs_hurricane_global_det_tcgen_plots
#PBS -j oe
#PBS -A ENSTRACK-DEV
#PBS -q dev
#PBS -l select=1:ncpus=2:mem=4GB
##PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1
#PBS -l walltime=00:30:00
#PBS -l debug=true
#PBS -V

#%include <head.h>
#%include <envir-p1.h>

############################################################
# Load modules
############################################################
module reset
export HOMEevs=/lfs/h2/emc/vpppg/save/$USER/EVS
source ${HOMEevs}/versions/run.ver

module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}

module load libjpeg/$libjpeg_ver
module load grib_util/$grib_util_ver
module load prod_util/${produtil_ver}
module load prod_envir/${prodenvir_ver}

module load geos/${geos_ver}
module load proj/${proj_ver}
module load imagemagick/${imagemagick_ver}

module list

export NET=evs
export COMPONENT=hurricane
export RUN=global_det
export STEP=plots
export VERIF_CASE=tcgen

export envir=dev
export cyc=00
export job=jevs_hurricane_global_det_tcgen_plots_${cyc}

#Set PDY to override setpdy.sh called in the j-jobs
export PDY=20221231

#Define the directories of your TC genesis stats files
export COMINstats=/lfs/h2/emc/ptmp/$USER/com/evs/${evs_ver}/${COMPONENT}/${RUN}/${VERIF_CASE}/stats
#Define the directories of your NOAA/NWS logos
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export DATAROOT=/lfs/h2/emc/ptmp/$USER
export COMROOT=${DATAROOT}/com
export KEEPDATA=YES


# CALL executable job script here
$HOMEevs/jobs/hurricane/plots/JEVS_HURRICANE_PLOTS

%include <tail.h>
%manual
######################################################################
# Purpose: This job will generate the grid2obs statistics for the HRRR
#          model and generate stat files.
######################################################################
%end

