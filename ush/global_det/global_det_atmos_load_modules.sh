#!/bin/sh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - Global Deterministic Atmospheric
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, IMSG @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Load necessary modules
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

# Load
source ${HOMEevs}/versions/run_global_det_atmos_${machine}.ver
if [ $machine = WCOSS2 ]; then
    source /usr/share/lmod/lmod/init/sh
    module reset
    export HPC_OPT=/apps/ops/para/libs
    export MET_bin_exec="bin"
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    export MET_bin_exec="bin"
elif [ $machine = JET ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    export MET_bin_exec="bin"
elif [ $machine = ORION ]; then
    source /apps/lmod/lmod/init/sh
    module purge
    export MET_bin_exec="bin"
elif [ $machine = S4 ]; then
    source /usr/share/lmod/lmod/init/sh
    module purge
    export MET_bin_exec="bin"
else
    echo "ERROR: $machine is not supported"
    exit 1
fi
module use ${HOMEevs}/modulefiles
module load run.global_det_atmos.${machine}
module list
if [ $machine = WCOSS2 ]; then
    export MET_BASE=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1/share/met
    export MET_ROOT=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1
    export PATH=/apps/ops/para/libs/intel/19.1.3.304/met/10.1.1/bin:${PATH}
fi
echo "END: $(basename ${BASH_SOURCE[0]})"
