#PBS -N jevs_global_det_atmos_prep_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev_transfer
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l select=1:ncpus=1:mem=30GB
#PBS -l debug=true
#PBS -V

set -x 

export model=evs

############################################################
# For dev testing
############################################################
cd $PBS_O_WORKDIR
echo $PBS_O_WORKDIR
module reset
#export HOMEevs=$(eval "cd ../../../;pwd")
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export evs_ver=$evs_ver
export envir=dev
export SENDCOM=YES
export KEEPDATA=NO
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_global_det_atmos_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_global_det_atmos_prep}
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
module load prod_envir/${prod_envir_ver}
module load prod_util/${prod_util_ver}
module load libjpeg/${libjpeg_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load cdo/${cdo_ver}
module load udunits/${udunits_ver}
module load nco/${nco_ver}
module list

export cyc=00

export maillist='geoffrey.manikin@noaa.gov,mallory.row@noaa.gov'

export NET=evs
export STEP=prep
export COMPONENT=global_det
export RUN=atmos

#export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/evs_global_det_atmos_test/$envir/com/$NET/$evs_ver/$STEP/$COMPONENT/$RUN
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/$STEP/$COMPONENT/$RUN

export MODELNAME="cfs cmc cmc_regional dwd ecmwf fnmoc imd jma metfra ukmet"
export OBSNAME="osi_saf ghrsst_ospo"

# CALL executable job script here
$HOMEevs/jobs/global_det/prep/JEVS_GLOBAL_DET_PREP

######################################################################
# Purpose: This does the prep work for the global deterministic atmospheric
######################################################################
