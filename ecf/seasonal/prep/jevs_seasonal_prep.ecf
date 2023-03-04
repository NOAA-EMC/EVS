#PBS -N jevs_seasonal_prep_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1
#PBS -l debug=true
#PBS -V

set -x

export model=evs

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver

#%include <head.h>
#%include <envir-p1.h>

############################################################
# Load modules
############################################################

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
export HPC_OPT=/apps/ops/prod/libs
module use /apps/ops/prod/libs/modulefiles/compiler/intel/${intel_ver}/
module load intel/${intel_ver}
module load gsl/${gsl_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load netcdf/${netcdf_ver}
module load nco/${nco_ver}
module load grib_util/${grib_util_ver}
module load prod_util/S{prod_util_ver}
module load python/${python_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load cdo/${cdo_ver}

module list

export envir=prod
export RUN_ENVIR=nco
export DATAROOTtmp=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export USE_CFP=YES
export met_ver=${met_ver}
export metplus_ver=${metplus_ver}
#export cyc=%CYC%
export NET=evs
export evs_ver=${evs_ver}
export STEP=prep
export COMPONENT=seasonal
export RUN=atmos
export MODELNAME=cfs
export model_ver=${cfs_ver}
export VERIF_CASE=grid2grid
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export config=$HOMEevs/parm/evs_config/seasonal/config.evs.prod.prep
source $config

# Call executable job script
$HOMEevs/jobs/seasonal/prep/JEVS_SEASONAL_PREP

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to retrieve the
#          seasonal data files for the CFS model 
#          and copy into the prep directory.
######################################################################
#%end
