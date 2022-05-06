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
export FIXevs=$HOMEevs/fix
export DATAROOT=$OUTPUTROOT/tmp
export COMROOT=$OUTPUTROOT/$envir/com
if [ $machine = "WCOSS2" ]; then
    export era_interim_climo_files="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/climo/new_climo_files/era_interim"
elif [ $machine = "HERA" ]; then
    export era_interim_climo_files=""
elif [ $machine = "JET" ]; then
    export era_interim_climo_files=""
elif [ $machine = "ORION" ]; then
    export era_interim_climo_files=""
elif [ $machine = "S4" ]; then
    export era_interim_climo_files=""
fi

# Set operational directories
export DCOMROOT_PROD=/lfs/h1/ops/prod/dcom
export COMROOT_PROD=/lfs/h1/ops/prod/com

# Set FTP/HTPP paths [TEMPORARY UNTIL IN DATAFLOW]

echo "END: $(basename ${BASH_SOURCE[0]})"
