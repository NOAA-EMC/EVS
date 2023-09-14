#PBS -N jevs_global_ens_headline_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=1:mem=10GB
#PBS -l debug=true

set -x

export OMP_NUM_THREADS=1

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

export NET=evs
export RUN=headline
export STEP=prep
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh

export KEEPDATA=NO

export cyc=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export run_mpi=no
export gefs_number=30

########################################
# This is for NAEFS v7
export COMINgefs_bc=/lfs/h2/emc/ptmp/bo.cui/com/${MODELNAME}/${naefs_ver}
########################################

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'

if [ -z "$maillist" ]; then
   echo "maillist variable is not defined. Exiting without continuing."
else
  ${HOMEevs}/jobs/global_ens/prep/JEVS_GLOBAL_ENS_PREP
fi
