#PBS -N jevs_gefs_subseasonal_grid2grid_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:40:00
#PBS -l place=vscatter,select=1:ncpus=61:ompthreads=1:mem=60GB
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

module list

export MET_ROOT=/apps/ops/para/libs/intel/${intel_ver}/met/${met_ver}
export MET_BASE=${MET_ROOT}/share/met
export PATH=${MET_ROOT}/bin:${PATH}
export MET_bin_exec=bin
export METviewer_AWS_scripts_dir=/lfs/h2/emc/vpppg/save/emc.vpppg/verification/metplus/metviewer_aws_scripts


export USER=$USER
export DATAROOTtmp=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export ACCOUNT=VERF-DEV
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=61
export USE_CFP=YES
export met_ver=${met_ver}
export metplus_ver=${metplus_ver}
#export cyc=%CYC
export cyc=00
export NET=evs
export evs_ver=${evs_ver}
export STEP=stats
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME=gefs
export gefs_ver=${gefs_ver}
export VERIF_CASE=grid2grid

export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER
#export COMIN=$COMROOT/$NET/$evs_ver
export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/prep/$COMPONENT/$RUN
export COMINobs=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/prep/$COMPONENT/$RUN
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export COMINclimo=$FIXevs/climos/atmos
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/$STEP/$COMPONENT
#export VDATE=$(date -d "today -22 day" +"%Y%m%d")

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.gefs.grid2grid.stats

# Call executable job script
$HOMEevs/jobs/subseasonal/stats/JEVS_SUBSEASONAL_STATS

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to generate the
#          subseasonal verification grid-to-grid statistics for the GEFS model#          and create the stat files in the databases.
######################################################################
#%end
