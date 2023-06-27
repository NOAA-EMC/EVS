#PBS -N jevs_rap_snowfall_stats_00
#PBS -j oe
#PBS -S /bin/bash
#PBS -q "dev"
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter:exclhost,select=1:ncpus=128:ompthreads=1:mem=25GB
#PBS -l debug=true
#PBS -V

set -x

cd $PBS_O_WORKDIR

export model=evs

export RUN_ENVIR=emc
export SENDECF=YES
export SENDCOM=YES
export KEEPDATA=NO
export SENDDBN=YES
export SENDDBN_NTC=
export job=${PBS_JOBNAME:-jevs_rap_snowfall_stats}
export jobid=$job.${PBS_JOBID:-$$}
export SITE=$(cat /etc/cluster_name)  
export envir="dev"
export NET="evs"
export RUN="atmos"
export cyc=$(date +"%H")
export cycle=t${cyc}z

export HOMEevs=/lfs/h2/emc/vpppg/noscrub/${USER}/EVS
export PARMevs=$HOMEevs/parm
export USHevs=$HOMEevs/ush
export EXECevs=$HOMEevs/exec
export FIXevs="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix"

export VDATE=$(date -d "today -2 day" +"%Y%m%d")
export STEP="stats"
export COMPONENT="mesoscale"
export VERIF_CASE="snowfall"
export MODELNAME="rap" 
export machine=WCOSS2
export USE_CFP=YES
export nproc=128  
export evs_run_mode="production"
export maillist='geoffrey.manikin@noaa.gov,mallory.row@noaa.gov'
export config=$HOMEevs/parm/evs_config/mesoscale/config.evs.prod.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${MODELNAME}

# Load Modules
source $HOMEevs/versions/run.ver
module reset
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load cray-pals/${craypals_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load cfp/${cfp_ver}
module load gsl/${gsl_ver}
module load netcdf/${netcdf_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}
export MET_bin_exec="bin"
module list

export DATAROOT=/lfs/h2/emc/stmp/$USER/evs_test/$envir/tmp
export COMOUT=/lfs/h2/emc/vpppg/noscrub/${USER}/$NET/$evs_ver/$STEP/$COMPONENT

# Job Settings and Run
${HOMEevs}/jobs/mesoscale/stats/JEVS_MESOSCALE_STATS

