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
export COMIN=$COMROOT/$NET/$evs_ver
export COMOUT=$COMROOT/$NET/$evs_ver/$STEP/$COMPONENT
if [ $machine = "WCOSS2" ]; then
    export FIXevs="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix"
    export archive_obs_data_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive/obs_data"
    export METviewer_AWS_scripts_dir="/lfs/h2/emc/vpppg/save/emc.vpppg/verification/metplus/metviewer_aws_scripts"
elif [ $machine = "HERA" ]; then
    export FIXevs="/scratch1/NCEPDEV/global/Mallory.Row/VRFY/EVS_fix"
    export archive_obs_data_dir="/scratch1/NCEPDEV/global/Mallory.Row/archive"
    export METviewer_AWS_scripts_dir="/scratch1/NCEPDEV/global/Mallory.Row/VRFY/METviewer_AWS"
elif [ $machine = "JET" ]; then
    #export FIXevs=""
    #export archive_obs_data_dir=""
    export METviewer_AWS_scripts_dir="/lfs4/HFIP/hfv3gfs/Mallory.Row/VRFY/METviewer_AWS"
elif [ $machine = "ORION" ]; then
    #export FIXevs=""
    #export archive_obs_data_dir=""
    export METviewer_AWS_scripts_dir="/gpfs/dell2/emc/verification/noscrub/emc.metplus/METviewer_AWS"
elif [ $machine = "S4" ]; then
    #export FIXevs=""
    #export archive_obs_data_dir=""
    export METviewer_AWS_scripts_dir="/data/prod/glopara/MET_data/METviewer_AWS"
fi

# Set WCOSS2 production paths
export COMINccpa=/lfs/h1/ops/prod/com/ccpa/$ccpa_ver
export COMINnohrsc=/lfs/h1/ops/prod/dcom
export COMINobsproc=/lfs/h1/ops/prod/com/obsproc/$obsproc_ver
export COMINosi_saf=/lfs/h1/ops/prod/com/evs/$evs_ver
export COMINghrsst_median=/lfs/h1/ops/prod/com/evs/$evs_ver
export COMINget_d=/lfs/h1/ops/prod/com/evs/$evs_ver

# Set FTP/HTPP paths [TEMPORARY UNTIL IN DATAFLOW]

echo "END: $(basename ${BASH_SOURCE[0]})"
