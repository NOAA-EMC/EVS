#PBS -N jevs_global_ens_headline_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=vscatter,select=1:ncpus=2:mem=10GB
#PBS -l debug=true


set -x
export OMP_NUM_THREADS=1
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export NET=evs
export RUN=headline
export STEP=prep
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs


module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh




export KEEPDATA=NO

#This var is only for testing, if not set, then run operational 

#export INITDATE=$1
TODAY=`date +%Y%m%d`
yyyymmdd=${TODAY:0:8}
PAST=`$NDATE -48 ${yyyymmdd}01`
export INITDATE=${INITDATE:-${PAST:0:8}}

#export INITDATE=20230514

echo $INITDATE
export cyc=00
export run_mpi=no

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'
export gefs_number=20

if [ -z "$maillist" ]; then

   echo "maillist variable is not defined. Exiting without continuing."

else

  ${HOMEevs}/jobs/global_ens/prep/JEVS_GLOBAL_ENS_PREP

fi
