#PBS -N jevs_subseasonal_grid2grid_sea_ice_plots_90days
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:10:00
#PBS -l place=vscatter,select=1:ncpus=34:ompthreads=1:mem=10GB
#PBS -l debug=true
#PBS -V

set -x

export model=evs

cd $PBS_O_WORKDIR

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS

export job=${PBS_JOBNAME:-jevs_subseasonal_grid2grid_sea_ice_plots_90days}
export jobid=$job.${PBS_JOBID:-$$}

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/subseasonal/subseasonal_plots.sh


export USER=$USER
export envir=prod
export KEEPDATA=YES
export SENDDBN=NO
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export ACCOUNT=VERF-DEV
export QUEUE=dev
export QUEUESHARED=dev_shared
export QUEUESERV=dev_transfer
export PARTITION_BATCH=
export nproc=34
export USE_CFP=YES
export met_ver=${met_ver}
export metplus_ver=${metplus_ver}
export cyc=00
export NET=evs
export evs_ver=${evs_ver}
export STEP=plots
export COMPONENT=subseasonal
export RUN=atmos
export MODELNAME="gefs cfs"
export VERIF_CASE=grid2grid
export VERIF_TYPE=sea_ice
export NDAYS=90
export DAYS=91

export COMROOT=/lfs/h2/emc/vpppg/noscrub/$USER

export config=$HOMEevs/parm/evs_config/subseasonal/config.evs.${COMPONENT}.${VERIF_CASE}.${STEP}.${VERIF_TYPE}

# Call executable job script
$HOMEevs/jobs/JEVS_SUBSEASONAL_PLOTS


######################################################################
# Purpose: The job and task scripts work together to generate the
#          subseasonal grid-to-grid sea ice statistical plots
#          for the GEFS and CFS models for past 90 days.
######################################################################
