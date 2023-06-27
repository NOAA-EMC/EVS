#PBS -N jevs_nfcens_g2o_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=1:mem=5GB
#PBS -l debug=true
#PBS -V

set -x 

##%include <head.h>
##%include <envir-p1.h>

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

############################################################
# read version file and set model_ver
############################################################
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export evs_ver=$evs_ver
export model_ver=$nfcens_ver
export obsproc_ver=$obsproc_ver

############################################################
# Load modules
############################################################
module reset
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load gsl/${gsl_ver}
module load prod_envir/${prod_envir_ver}
module load prod_util/${prod_util_ver}
module load libjpeg/${libjpeg_ver}
module load grib_util/${grib_util_ver}
module load wgrib2/${wgrib2_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
##### load prod_envir sets: OPSROOT, OPSROOTssd, COMROOT, DATAROOT, 
##### DCOOMROOT, PACKAGEROOT, SIPHONROOT
##### load prod_util sets: UTILROOT, MDATE, NDATE, NHOUR, FSYNC, 
##### COMDATEROOT, COMLISTROOT, COMLOGSROOT
###### and prepends path for PATH, PYTHONPATH

module list

############################################################
# set some variables
############################################################
export envir=prod
export SENDCOM=${SENDCOM:-YES}
export SENDECF=${SENDECF:-YES}
export SENDDBN=${SENDDBN:-YES}
export KEEPDATA=${KEEPDATA:-YES}

export MODELNAME=nfcens
export NET=evs
export COMPONENT=nfcens
export STEP=prep
export RUN=wave
export VERIF_CASE=grid2obs
export cycle=t00z

## developers directories
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_output
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export OUTPUTROOT=/lfs/h2/emc/vpppg/noscrub/$USER
export COMIN=${OUTPUTROOT}/${NET}/${evs_ver}

export job=${PBS_JOBNAME:-jevs_nfcens_g2o_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

export metplus_verbosity="INFO"
export met_verbosity="2"
export log_met_output_to_metplus="yes"
export MET_bin_exec=bin

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/nfcens/prep/JEVS_NFCENS_WAVE_GRID2OBS_PREP

##%include <tail.h>
##%manual
######################################################################
# Purpose: This does the prep work for the NFCENS wave model
######################################################################
##%end
exit
