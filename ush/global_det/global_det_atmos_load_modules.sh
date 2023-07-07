#!/bin/bash -xe
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
machine_ver_file=${HOMEevs}/versions/run_global_det_atmos_${machine}.ver
if [ -f "$machine_ver_file" ]; then
    source $machine_ver_file
else
    echo "ERROR: $machine_ver_file does not exist"
    exit 1
fi

if [ $machine = WCOSS2 ]; then
    source /usr/share/lmod/lmod/init/bash
    module reset
    export HPC_OPT=/apps/ops/prod/libs
elif [ $machine = HERA ]; then
    source /apps/lmod/lmod/init/bash
    module purge
elif [ $machine = JET ]; then
    source /apps/lmod/lmod/init/bash
    module purge
elif [ $machine = ORION ]; then
    source /apps/lmod/lmod/init/bash
    module purge
elif [ $machine = S4 ]; then
    source /usr/share/lmod/lmod/init/bash
    module purge
else
    echo "ERROR: $machine is not supported"
    exit 1
fi

machine_module_file=${HOMEevs}/modulefiles/run.global_det_atmos.${machine}.lua
if [ -f $machine_module_file ]; then
    module use ${HOMEevs}/modulefiles
    module load run.global_det_atmos.${machine}
    module list
else
    echo "ERROR: ${machine_module_file} does not exist"
    exit 1
fi

if [ $machine = HERA ]; then
    export MET_ROOT="/contrib/met/${met_ver}"
fi

echo "END: $(basename ${BASH_SOURCE[0]})"
