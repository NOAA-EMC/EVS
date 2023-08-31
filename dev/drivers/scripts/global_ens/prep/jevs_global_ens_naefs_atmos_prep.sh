#PBS -N jevs_global_ens_naefs_atmos_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:30:00
#PBS -l place=vscatter,select=1:ncpus=68:mem=100GB
#PBS -l debug=true


set -x
export OMP_NUM_THREADS=1
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export NET=evs
export RUN=atmos
export STEP=prep
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=naefs


module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh




export KEEPDATA=NO

#This var is only for testing, if not set, then run operational 

export cyc=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}


#export COMINgefs_bc=/lfs/h2/emc/ptmp/bo.cui/com/naefs/v7.0

export maillist='geoffrey.manikin@noaa.gov,binbin.zhou@noaa.gov'

export run_mpi=yes
export get_gefs_bc_apcp24h=yes
export get_model_bc=yes

if [ -z "$maillist" ]; then
   echo "maillist variable is not defined. Exiting without continuing."

else

  ${HOMEevs}/jobs/global_ens/prep/JEVS_GLOBAL_ENS_PREP

fi

