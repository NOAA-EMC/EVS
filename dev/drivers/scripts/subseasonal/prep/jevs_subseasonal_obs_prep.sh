#PBS -N jevs_subseasonal_obs_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l select=1:ncpus=1:mem=5GB
#PBS -l debug=true
#PBS -V

set -x

export model=evs

cd $PBS_O_WORKDIR

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/subseasonal/subseasonal_prep.sh

export envir=prod
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_subseasonal_obs_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)

export maillist='alicia.bentley@noaa.gov,shannon.shields@noaa.gov'

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
export OBSNAME="gfs ecmwf osi ghrsst umd nam"
export gfs_ver=${gfs_ver}
export obsproc_ver=${obsproc_ver}
export PREP_TYPE=obs

export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/$STEP/$COMPONENT/$RUN

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.obs.prep

# Call executable job script
$HOMEevs/jobs/JEVS_SUBSEASONAL_PREP


######################################################################
# Purpose: The job and task scripts work together to retrieve the
#          subseasonal data files for obs 
#          and copy into the prep directory.
######################################################################
