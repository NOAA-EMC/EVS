#PBS -N jevs_subseasonal_plots
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1
#PBS -l debug=true
#PBS -V

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

#%include <head.h>
#%include <envir-p1.h>

############################################################
# Load modules
############################################################
set -x

module load envvar/${envvar_ver}
module load intel/${intel_ver}
module load PrgEnv-intel/${PrgEnvintel_ver}
module load craype/${craype_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load cfp/${cfp_ver}
module load g2c/${g2c_ver}
module load wgrib2/${wgrib2_ver}
module load proj/${proj_ver}
module load geos/${geos_ver}
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/19.1.3.304/
module load intel/${intel_ver}
module load gsl/${gsl_ver}
module load libpng/${libpng_ver}
module load libjpeg/${libjpeg_ver}
module load netcdf/${netcdf_ver}
module load nco/${nco_ver}
module load grib_util/${grib_util_ver}
module load prod_util/S{prod_util_ver}
module load python/${python_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load cdo/${cdo_ver}

module list

export DATAROOTtmp=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export USE_CFP=YES
#export cyc=%CYC%
export NET=evs
export evs_ver=${evs_ver}
export STEP=plots
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME=gefs cfs
export model_ver=${gefs_ver} ${cfs_ver}
export VERIF_CASE=grid2grid

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.plots

# Call executable job script
$HOMEevs/jobs/subseasonal/plots/JEVS_SUBSEASONAL_PLOTS

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to generate the
#          subseasonal verification statistical plots
#          for the GEFS and CFS models.
######################################################################
#%end
