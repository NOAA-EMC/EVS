#PBS -N jevs_subseasonal_gefs_prep
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

source $HOMEevs/versions/run.ver
source $HOMEevs/modulefiles/subseasonal/subseasonal_prep.sh

export DATAROOTtmp=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_subseasonal_gefs_prep}
export jobid=$job.${PBS_JOBID:-$$}
export TMPDIR=$DATAROOTtmp
export SITE=$(cat /etc/cluster_name)

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

export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/$evs_ver/$STEP/$COMPONENT/$RUN
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.subseasonal.gefs.prep

# Call executable job script
$HOMEevs/jobs/subseasonal/prep/JEVS_SUBSEASONAL_PREP


######################################################################
# Purpose: The job and task scripts work together to retrieve the
#          subseasonal data files for the GEFS model 
#          and copy into the prep directory.
######################################################################
