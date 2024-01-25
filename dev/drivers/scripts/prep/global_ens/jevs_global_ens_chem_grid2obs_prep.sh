#PBS -N jevs_global_ens_chem_g2o_prep
#PBS -j oe
#PBS -S /bin/bash
#PBS -q dev
#PBS -A VERF-DEV
#PBS -l walltime=01:00:00
#PBS -l place=shared,select=ncpus=1:mem=8GB
#PBS -l debug=true
#PBS -V

##%include <head.h>
##%include <envir-p1.h>

############################################################
# Load modules
############################################################
set -x

cd $PBS_O_WORKDIR

export model=evs
export HOMEevs=/lfs/h2/emc/vpppg/noscrub/$USER/EVSGefsChem

source $HOMEevs/versions/run.ver

module reset

module load prod_envir/${prod_envir_ver}

source $HOMEevs/dev/modulefiles/global_ens/global_ens_prep.sh

evs_ver_2d=$(echo $evs_ver | cut -d'.' -f1-2)

# export MET_PLUS_PATH="/apps/ops/para/libs/intel/${intel_ver}/metplus/${metplus_ver}"
# export MET_PATH="/apps/ops/para/libs/intel/${intel_ver}/met/${met_ver}"
# export MET_CONFIG="${MET_PLUS_PATH}/parm/met_config"
# export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH

export cyc=00
echo $cyc
export KEEPDATA=YES
export NET=evs
export STEP=prep
export COMPONENT=global_ens
export RUN=chem
export VERIF_CASE=grid2obs
export MODELNAME=gefs

######################################
### Correct MET/METplus roots (Aug 2022)
########################################

export COMIN=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
## export COMINobs=/lfs/h1/ops/dev/dcom/${VDATE}
## export COMOUT=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}
## export COMOUTprep=/lfs/h2/emc/vpppg/noscrub/$USER/$NET/${evs_ver}/$STEP/$COMPONENT
export DATA=/lfs/h2/emc/ptmp/$USER/$NET/${evs_ver}/${STEP}
mkdir -p DATA
## export FIXevs=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix
## export USHevs=$HOMEevs/ush/$COMPONENT
## export CONFIGevs=$HOMEevs/parm/metplus_config/$COMPONENT
## export PARMevs=$HOMEevs/parm/metplus_config

## developers directories

export cycle=t${cyc}z

echo ${PDYm1}
export VDATE=$PDYm1
export VDATE=$(date --date="2 days ago" +%Y%m%d)
echo ${VDATE}


############################################################
## CALL executable job script here
#############################################################
$HOMEevs/jobs/$COMPONENT/$STEP/JEVS_GLOBAL_ENS_CHEM_GRID2OBS_PREP

#%include <tail.h>
#%manual
#######################################################################
# Purpose: This does the prep work for the global_ens GEFS-Chem model
#######################################################################
#%end
