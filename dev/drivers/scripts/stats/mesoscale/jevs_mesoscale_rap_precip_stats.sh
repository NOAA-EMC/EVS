#PBS -N jevs_mesoscale_rap_precip_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1:mem=150GB
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs

export SENDECF=YES
export SENDCOM=YES
export KEEPDATA=YES
export SENDDBN=NO
export SENDDBN_NTC=
export SENDMAIL=YES
export job=${PBS_JOBNAME:-jevs_rap_precip_stats}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)  
export envir="prod"
export NET="evs"
export RUN="atmos"
export vhr=${vhr:-${vhr}}

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS

export STEP="stats"
export COMPONENT="mesoscale"
export VERIF_CASE="precip"
export MODELNAME="rap" 
export machine=WCOSS2
export USE_CFP=YES
export nproc=128  
export evs_run_mode="production"

export MAILTO="roshan.shrestha@noaa.gov,alicia.bentley@noaa.gov"
# export MAILTO="firstname.lastname@noaa.gov"

export config=$HOMEevs/parm/evs_config/mesoscale/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

source $HOMEevs/versions/run.ver
module reset
module load prod_envir/${prod_envir_ver}
source $HOMEevs/dev/modulefiles/${COMPONENT}/${COMPONENT}_${STEP}.sh
evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

export COMIN=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d
export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver_2d/$STEP/$COMPONENT

# Job Settings and Run
${HOMEevs}/jobs/JEVS_MESOSCALE_STATS

