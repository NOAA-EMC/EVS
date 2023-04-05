#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC VERIFICATION SYSTEM - SUBSEASONAL
##
## CONTRIBUTORS: Shannon Shields, Shannon.Shields@noaa.gov, NCEP/EMC-VPPPGB
## PURPOSE: Load necessary modules
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

## Check versions are supported in evs
if [[ "$MET_version" =~ ^(10.1.1)$ ]]; then
    echo "Requested MET version: $MET_version"
else
    echo "ERROR: $MET_version is not supported in evs"
    exit 1
fi
if [[ "$METplus_version" =~ ^(4.1.1)$ ]]; then
    echo "Requested METplus version: $METplus_version"
else
    echo "ERROR: $METplus_version is not supported in evs"
    exit 1
fi

## Load
source ${HOMEevs}/versions/run_${machine}.ver
if [ $machine = WCOSS2 ]; then
    source /usr/share/lmod/lmod/init/sh
    module reset
    export HPC_OPT=/apps/ops/para/libs
    export HOMEMET="/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1"
    export HOMEMET_bin_exec="bin"
    export HOMEMETplus="${METPLUS_PATH}"
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    export HOMEMET="/contrib/met/10.1.1"
    export HOMEMET_bin_exec="bin"
    export HOMEMETplus="${METPLUS_PATH}"
elif [ $machine = ORION ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    export HOMEMET="/apps/contrib/MET/10.1.1"
    export HOMEMET_bin_exec="bin"
    export HOMEMETplus="${METPLUS_PATH}"
else
    echo "ERROR: $machine is not supported"
    exit 1
fi
module use ${HOMEevs}/modulefiles
module load run.modules.${machine}
module list
#if [ $machine = WCOSS2 ]; then
    #export MET_BASE=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1/share/met
    #export MET_ROOT=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1
    #export PATH=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1/bin:${PATH}
#fi
if [ $machine != "ORION" ]; then
    export RM=`which rm`
    export CUT=`which cut`
    export TR=`which tr`
    export NCAP2=`which ncap2`
    export CONVERT=`which convert`
    export NCDUMP=`which ncdump`
    export HTAR=`which htar`
fi
if [ $machine = "ORION" ]; then
    export RM=`which rm | sed 's/rm is //g'`
    export CUT=`which cut | sed 's/cut is //g'`
    export TR=`which tr | sed 's/tr is //g'`
    export NCAP2=`which ncap2 | sed 's/ncap2 is //g'`
    export CONVERT=`which convert | sed 's/convert is //g'`
    export NCDUMP=`which ncdump | sed 's/ncdump is //g'`
    export HTAR="/null/htar"
fi
#echo "Using HOMEMET=${HOMEMET}"
#echo "Using HOMEMETplus=${HOMEMETplus}"

echo "END: $(basename ${BASH_SOURCE[0]})"
