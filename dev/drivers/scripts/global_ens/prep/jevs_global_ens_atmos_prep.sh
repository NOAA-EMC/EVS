#PBS -N jevs_global_ens_atmos_prep
#PBS -j oe 
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=06:00:00
#PBS -l place=vscatter,select=2:ncpus=64:mpiprocs=64:mem=500GB
#PBS -l debug=true


#Total 98 processes: 68(gefs_atmos) + 2(gefs_precip) + 18(cmce_atmos) + 2(cmce_precip) + 1 (ecme_atmos) + 1 (ecme_precip) + 2 (gefs_snow) + 2 (cmce_snow) + 1 (ecme_snow) + 1 (gefs_icec) 
# In which 87 (68 gefs_atmos, + 18 cmce_atmos, + 1 ecme_atmos) are run in parrell, all prepcip, snow and icec are not 
#Total 2x87=174 cpu cores,  cpu cores are assigned to 3 node
#Completed in about 1hr 40min

set -x
export OMP_NUM_THREADS=1
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
source $HOMEevs/versions/run.ver

export NET=evs
export RUN=atmos
export STEP=prep
export COMPONENT=global_ens
export VERIF_CASE=grid2grid
export MODELNAME=gefs


module reset
module load prod_envir/${prod_envir_ver}

source $HOMEevs/modulefiles/$COMPONENT/${COMPONENT}_${STEP}.sh




export KEEPDATA=NO

#This var is only for testing, if not set, then run operational 

export cyc=00
export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver
export DATAROOT=/lfs/h2/emc/stmp/${USER}/evs_test/$envir/tmp

export job=${PBS_JOBNAME:-jevs_${MODELNAME}_${VERIF_CASE}_${STEP}}
export jobid=$job.${PBS_JOBID:-$$}

export maillist='alicia.bentley@noaa.gov,steven.simon@noaa.gov' 


if [ -z "$maillist" ]; then
   echo "maillist variable is not defined. Exiting without continuing."
else
   ${HOMEevs}/jobs/global_ens/prep/JEVS_GLOBAL_ENS_PREP
fi

