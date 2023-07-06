#PBS -N jevs_global_det_wave_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l select=1:ncpus=1:mem=10GB
#PBS -l debug=true
#PBS -V

set -x 

##%include <head.h>
##%include <envir-p1.h>

export model=evs

############################################################
# For dev testing
############################################################
cd $PBS_O_WORKDIR
echo $PBS_O_WORKDIR
module reset
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
versionfile=$HOMEevs/versions/run.ver
. $versionfile
export evs_ver=$evs_ver
export envir=dev
export SENDCOM=YES
export KEEPDATA=NO
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_output/$envir/tmp
export job=${PBS_JOBNAME:-jevs_global_det_wave_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)
############################################################

############################################################
# Load modules
############################################################
module reset
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load prod_envir/${prod_envir_ver}
module load prod_util/${prod_util_ver}
module list

export cyc=00

export maillist='geoffrey.manikin@noaa.gov,mallory.row@noaa.gov'

export NET=evs
export STEP=prep
export COMPONENT=global_det
export RUN=wave

export MODELNAME="gfs"
export OBSNAME=""

export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/$STEP/$COMPONENT/$RUN

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/global_det/prep/JEVS_GLOBAL_DET_PREP

##%include <tail.h>
##%manual
#####################################################################
# Purpose: This does the prep work for the global deterministic wave
#####################################################################
##%end
