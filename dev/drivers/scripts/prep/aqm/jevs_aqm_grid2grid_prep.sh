#PBS -N jevs_aqm_grid2grid_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=shared,select=1:ncpus=1:mem=100GB:prepost=true
#PBS -l debug=true

set -x

cd $PBS_O_WORKDIR

export model=evs
export COMPONENT=aqm

## export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVSAQMaod

############################################################
# Load modules
############################################################

source $HOMEevs/versions/run.ver

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/aqm/aqm_prep.sh

export vhr=00
echo $vhr
export NET=evs
export STEP=prep
export RUN=atmos
export VERIF_CASE=grid2grid
export MODELNAME=aqm
export modsys=aqm
export mod_ver=${aqm_ver}
export envir=prod

export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix

export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export KEEPDATA=YES
export SENDMAIL=YES
export SENDDBN=NO

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver_2d}
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/${NET}/${evs_ver_2d}
#
export DATA_TYPE=abi
export GOES_EAST=g16
export GOES_WEST=g18
export AOD_SCAN_TYPE=AODC
export ADP_SCAN_TYPE=ADPC
export AOD_QC_NAME=high
#
export MAILTO=${MAILTO:-'ho-chun.huang@noaa.gov,andrew.benjamin@noaa.gov'}

if [ -z "$MAILTO" ]; then

   echo "MAILTO variable is not defined. Exiting without continuing."

else

   # CALL executable job script here
   $HOMEevs/jobs/JEVS_AQM_PREP

fi

######################################################################
## Purpose: This job will generate the grid2obs statistics for the AQM
##          model and generate stat files.
#######################################################################
#



