#PBS -N jevs_subseasonal_cfs_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:20:00
#PBS -l select=1:ncpus=1:mem=10GB
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
export job=${PBS_JOBNAME:-jevs_subseasonal_cfs_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOT
export SITE=$(cat /etc/cluster_name)
export KEEPDATA=YES
export SENDMAIL=YES

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
export MODELNAME=cfs
export cfs_ver=${cfs_ver}
export PREP_TYPE=cfs


export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.cfs.prep

# Call executable job script
$HOMEevs/jobs/JEVS_SUBSEASONAL_PREP


######################################################################
# Purpose: The job and task scripts work together to retrieve the
#          subseasonal data files for the CFS model 
#          and copy into the prep directory.
######################################################################
