#PBS -N jevs_subseasonal_prep_00
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=02:00:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1:mem=140GB
#PBS -l debug=true
#PBS -V

set -x

export model=evs

cd $PBS_O_WORKDIR
module reset

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

versionfile=$HOMEevs/versions/run.ver
. $versionfile

export DATAROOTtmp=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_subseasonal_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOTtmp
export SITE=$(cat /etc/cluster_name)

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

export USER=$USER
export ACCOUNT=VERF-DEV
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=128
export USE_CFP=YES
export WGRIB2=`which wgrib2`
#export cyc=%CYC
export cyc=00
export NET=evs
export evs_ver=${evs_ver}
export STEP=prep
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME="gefs cfs"
export gefs_ver=${gefs_ver}
export cfs_ver=${cfs_ver}
export OBSNAME="gfs ecmwf osi ghrsst umd nam"
export gfs_ver=${gfs_ver}
export ccpa_ver=${ccpa_ver}
export obsproc_ver=${obsproc_ver}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/$STEP/$COMPONENT/$RUN
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.prep

# Call executable job script
$HOMEevs/jobs/subseasonal/prep/JEVS_SUBSEASONAL_PREP

#%include <tail.h>
#%manual
######################################################################
# Purpose: The job and task scripts work together to retrieve the
#          subseasonal data files for the GEFS, CFS, and obs 
#          and copy into the prep directory.
######################################################################
#%end
