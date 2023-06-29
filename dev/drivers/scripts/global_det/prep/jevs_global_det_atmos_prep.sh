#PBS -N jevs_global_det_atmos_prep_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l select=1:ncpus=1:mem=30GB
#PBS -l debug=true
#PBS -V

set -x 

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export SENDCOM=YES
export KEEPDATA=NO
export RUN_ENVIR=nco
export job=${PBS_JOBNAME:-jevs_global_det_atmos_prep}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)
export cyc=00

module reset
source $HOMEevs/versions/run.ver
source $HOMEevs/modulefiles/global_det/global_det_prep.sh

export maillist='geoffrey.manikin@noaa.gov,mallory.row@noaa.gov'

export envir=dev
export NET=evs
export STEP=prep
export COMPONENT=global_det
export RUN=atmos

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export TMPDIR=$DATAROOT
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/$STEP/$COMPONENT/$RUN

export MODELNAME="cfs cmc cmc_regional dwd ecmwf fnmoc imd jma metfra ukmet"
export OBSNAME="osi_saf ghrsst_ospo"

# CALL executable job script here
$HOMEevs/jobs/global_det/prep/JEVS_GLOBAL_DET_PREP

######################################################################
# Purpose: This does the prep work for the global deterministic atmospheric
######################################################################
