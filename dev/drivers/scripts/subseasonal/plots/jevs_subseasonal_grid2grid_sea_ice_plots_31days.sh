#PBS -N jevs_subseasonal_grid2grid_sea_ice_plots_31days_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=vscatter,select=1:ncpus=34:ompthreads=1:mem=10GB
#PBS -l debug=true
#PBS -V

set -x

export model=evs

cd $PBS_O_WORKDIR
module reset

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

#%include <head.h>
#%include <envir-p1.h>

############################################################
# Load modules
############################################################

module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}/
export HPC_OPT=/apps/ops/para/libs
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load prod_envir/${prod_envir_ver}
module load prod_util/${prod_util_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}
module load g2c/${g2c_ver}
module load wgrib2/${wgrib2_ver}
module load libpng/${libpng_ver}
module load libjpeg/${libjpeg_ver}
module load udunits/${udunits_ver}
module load nco/${nco_ver}
module load grib_util/${grib_util_ver}
module load cdo/${cdo_ver}

export MET_bin_exec=bin

module list

export USER=$USER
export DATAROOTtmp=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export ACCOUNT=VERF-DEV
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=34
export USE_CFP=YES
export met_ver=${met_ver}
export metplus_ver=${metplus_ver}
export cyc=00
export NET=evs
export evs_ver=${evs_ver}
export STEP=plots
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME="gefs cfs"
export VERIF_CASE=grid2grid
export VERIF_TYPE=sea_ice
export NDAYS=31

export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=$COMROOT/$NET/$evs_ver
export COMINcfs=$COMIN/stats/$COMPONENT/cfs
export COMINgefs=$COMIN/stats/$COMPONENT/gefs
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export VDATE_START=$(date -d "today -32 day" +"%Y%m%d")
export VDATE_END=$(date -d "today -2 day" +"%Y%m%d")
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT/$RUN.$VDATE_END

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.${COMPONENT}.${VERIF_CASE}.${STEP}.${VERIF_TYPE}

# Call executable job script
$HOMEevs/jobs/subseasonal/plots/JEVS_SUBSEASONAL_PLOTS

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to generate the
#          subseasonal grid-to-grid sea ice statistical plots
#          for the GEFS and CFS models for past 31 days.
######################################################################
#%end
