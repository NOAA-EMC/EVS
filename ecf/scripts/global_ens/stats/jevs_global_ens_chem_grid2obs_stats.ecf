#PBS -N jevs_global_ens_chem_g2o_stats
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=00:15:00
#PBS -l place=vscatter,select=1:ncpus=1:mpiprocs=1:mem=10G
#PBS -l debug=true
#PBS -o g2o_statout.t00z
#PBS -e g2o_staterr.t00z
#PBS -V

##%include <head.h>
##%include <envir-p1.h>

set -x

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVS
source $HOMEevs/versions/run.ver

############################################################
# Load modules
############################################################

module reset
export HPC_OPT=/apps/ops/para/libs
module use /apps/ops/para/libs/modulefiles/compiler/intel/${intel_ver}
module use /apps/dev/modulefiles/
module load ve/evs/${ve_evs_ver}
module load cray-mpich/${craympich_ver}
module load cray-pals/${craypals_ver}
module load libjpeg/${libjpeg_ver}
module load libpng/${libpng_ver}
module load zlib/${zlib_ver}
module load jasper/${jasper_ver}
module load cfp/${cfp_ver}
module load gsl/${gsl_ver}
module load met/${met_ver}
module load metplus/${metplus_ver}
module load prod_util/${prod_util_ver}
module load prod_envir/${prod_envir_ver}

module list

export MET_PLUS_PATH="/apps/ops/para/libs/intel/${intel_ver}/metplus/${metplus_ver}"
export MET_PATH="/apps/ops/para/libs/intel/${intel_ver}/met/${met_ver}"
export MET_CONFIG="${MET_PLUS_PATH}/parm/met_config"
export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH


############################################################
# set some variables
############################################################
export cyc=00
echo $cyc
#export envir=dev

export MODELNAME=gefs
export NET=evs
export COMPONENT=global_ens
export STEP=stats
export RUN=chem
export VERIF_CASE=grid2obs
#export VARS="aod pmtf"
export MET_bin_exec=bin

export VDATE=$(date --date="2 days ago" +%Y%m%d)

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMINobs=/lfs/h1/ops/dev/dcom
export COMINfcst=/lfs/h1/ops/prod/com/gefs/v12.3
export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
export COMOUTprep=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}/$STEP/$COMPONENT
export COMOUTfinal=$COMOUT/$STEP/$COMPONENT/$COMPONENT.$VDATE
export DATA=/lfs/h2/emc/ptmp/$USER/$NET/${evs_ver}
export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
export USHevs=$HOMEevs/ush/$COMPONENT
export CONFIGevs=$HOMEevs/parm/metplus_config/$COMPONENT

export cycle=t${cyc}z

export VDATE=$PDYm2

############################################################
# CALL executable job script here
############################################################
$HOMEevs/jobs/$COMPONENT/$STEP/JEVS_GLOBAL_ENS_CHEM_GRID2OBS_STATS

#%include <tail.h>
#%manual
#######################################################################
# Purpose: This calculates the stats for the global_ens GEFS-Chem model
#######################################################################
#%end

