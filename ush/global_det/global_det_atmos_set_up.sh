#!/bin/sh -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - Global Deterministic Atmospheric
##
## CONTRIBUTORS: Mallory Row, mallory.row@noaa.gov, IMSG @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Set up Global Deterministic Atmospheric 
##          run environment based on user configurations
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

export NET="evs"
export RUN="atmos"
export COMPONENT="global_det"
export RUN_ENVIR="emc"
export envir="dev"
export evs_run_mode="standalone"

# Create output directory and set output related environment variables
if [ -d "$OUTPUTROOT" ] ; then
   echo "OUTPUTROOT ($OUTPUTROOT) ALREADY EXISTS"
   echo "OVERRIDE CURRENT OUTPUTROOT? [yes/no]"
   read override
   case "$override" in
       yes)
           echo "Removing current OUTPUTROOT and making new directory"
           rm -r $OUTPUTROOT
           mkdir -p $OUTPUTROOT
           ;;
       no)
           echo "Please set new OUTPUTROOT"
           exit
           ;;
       *)
           echo "$override is not a valid choice, please choose [yes or no]"
           exit
           ;;
   esac
else
   mkdir -p ${OUTPUTROOT}
fi

echo "Output will be in: $OUTPUTROOT"
export DATAROOT="$OUTPUTROOT/tmp"
export COMROOT="$OUTPUTROOT/$envir/com"
export job=${NET}_${COMPONENT}_${RUN}
export pid=${pid:-$$}
export jobid=$job.$pid
export DATA=${DATA:-${DATAROOT:?}/${jobid:?}}
mkdir -p $DATAROOT $DATA $COMROOT
cd $DATA
echo

# Get machine, set environment variable 'machine', and check that it is a supported machine
python $HOMEevs/ush/global_det/global_det_atmos_get_machine.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Succesfully ran global_det_atmos_get_machine.py"
echo

if [ -s config.machine ]; then
    . $DATA/config.machine
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Succesfully sourced config.machine"
fi

# Set machine specific account, queues, and run settings
if [ $machine = "WCOSS2" ]; then
    export ACCOUNT="GFS-DEV"
    export QUEUE="dev"
    export QUEUESHARED="dev_shared"
    export QUEUESERV="dev_transfer"
    export PARTITION_BATCH=""
    export nproc="128"
    export USE_CFP="YES"
elif [ $machine = "HERA" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
    export PARTITION_BATCH=""
    export nproc="40"
    export USE_CFP="YES"
elif [ $machine = "JET" ]; then
    export ACCOUNT="hfv3gfs"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
    export PARTITION_BATCH="xjet"
    export nproc="10"
    export USE_CFP="YES"
elif [ $machine = "ORION" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
    export PARTITION_BATCH="orion"
    export nproc="40"
    export USE_CFP="YES"
elif [ $machine = "S4" ]; then
    export ACCOUNT="star"
    export QUEUE="s4"
    export QUEUESHARED="s4"
    export QUEUESERV="serial"
    export PARTITION_BATCH="s4"
    export nproc="32"
    export USE_CFP="YES"
fi

echo "END: $(basename ${BASH_SOURCE[0]})"
