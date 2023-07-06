#PBS -N jevs_subseasonal_gefs_prep_00
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=01:30:00
#PBS -l select=1:ncpus=1:mem=120GB
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

export maillist='geoffrey.manikin@noaa.gov,shannon.shields@noaa.gov'

export USER=$USER
export ACCOUNT=VERF-DEV
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=1
export WGRIB2=`which wgrib2`
export cyc=00
export NET=evs
export evs_ver=${evs_ver}
export STEP=prep
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME=gefs
export gefs_ver=${gefs_ver}
export PREP_TYPE=gefs

export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/EVS_Data/$NET/$evs_ver/$STEP/$COMPONENT/$RUN
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.gefs.prep

# Call executable job script
$HOMEevs/jobs/subseasonal/prep/JEVS_SUBSEASONAL_PREP


######################################################################
# Purpose: The job and task scripts work together to retrieve the
#          subseasonal data files for the GEFS model 
#          and copy into the prep directory.
######################################################################
