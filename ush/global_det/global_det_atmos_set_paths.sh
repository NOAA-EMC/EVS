#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - Global Deterministic Atmospheric
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, IMSG @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Set paths
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

# Set bases for MET and METplus
#export HOMEmet=$MET_ROOT
#export HOMEmetplus=$METPLUS_PATH
#echo "Using HOMEmet=$HOMEmet"
#echo "Using HOMEmetplus=$HOMEmetplus"

# Set versions
export evs_ver="v1.0"
export ccpa_ver="v4.2"
export obsproc_ver="v1.0"
export cmc_ver="v1.2"
export cfs_ver="v2.3"

# Set paths
export PARMevs=$HOMEevs/parm
export USHevs=$HOMEevs/ush
export EXECevs=$HOMEevs/exec
export DATAROOT=$OUTPUTROOT/tmp
export COMROOT=$OUTPUTROOT/$envir/com
if [ $machine = "WCOSS2" ]; then
    export FIXevs="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix"
    export archive_obs_data_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data"
elif [ $machine = "HERA" ]; then
    export FIXevs=""
    export archive_obs_data_dir=""
elif [ $machine = "JET" ]; then
    export FIXevs=""
    export archive_obs_data_dir=""
elif [ $machine = "ORION" ]; then
    export FIXevs=""
    export archive_obs_data_dir=""
elif [ $machine = "S4" ]; then
    export FIXevs=""
    export archive_obs_data_dir=""
fi

# Set operational directories
export DCOMROOT_PROD=/lfs/h1/ops/prod/dcom
export COMROOT_PROD=/lfs/h1/ops/prod/com

# Set FTP/HTPP paths [TEMPORARY UNTIL IN DATAFLOW]

echo "END: $(basename ${BASH_SOURCE[0]})"
