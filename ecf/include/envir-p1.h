# envir-p1.h
export job=${job:-$PBS_JOBNAME}
export jobid=${jobid:-$job.$PBS_JOBID}

export RUN_ENVIR=nco
export envir=%ENVIR%
export MACHINE_SITE=%MACHINE_SITE%
export RUN=%RUN%

if [[ "$envir" == prod && "$SENDDBN" == YES ]]; then
    export eval=%EVAL:NO%
    if [ $eval == YES ]; then export SIPHONROOT=${UTILROOT}/para_dbn
    else export SIPHONROOT=/lfs/h1/ops/prod/dbnet_siphon
    fi
    if [ "$PARATEST" == YES ]; then export SIPHONROOT=${UTILROOT}/fakedbn; export NODBNFCHK=YES; fi
else
    export SIPHONROOT=${UTILROOT}/fakedbn
fi
# export DBNROOT=$SIPHONROOT
export SIPHONROOT=${UTILROOT}/fakedbn
export DBNROOT=$SIPHONROOT

if [[ ! " prod para test " =~ " ${envir} " && " ops.prod ops.para " =~ " $(whoami) " ]]; then err_exit "ENVIR must be prod, para, or test [envir-p1.h]"; fi

# EVS missing DATA EMAIL configuration
export maillist="first.last@noaa.gov"

# Developer configuration
PTMP=/lfs/h2/emc/ptmp
model=evs
PSLOT=ecflow_evs
#### Lin
#### export COMROOT=${PTMP}/${USER}/${PSLOT}/para/com
#### EVS
export COMROOT=/lfs/h2/emc/vpppg/noscrub/emc.vpppg/com
export COMPATH=${COMROOT}/${model}
if [ -n "%PDY:%" ]; then
  export PDY=${PDY:-%PDY:%}
else
  export PDY=$($NDATE | cut -c1-8)
fi
export CDATE=${PDY}%CYC:%

export COMevs=$(compath.py evs/${evs_ver})
export DATAFS=h1
export DATAROOT=/lfs/h2/emc/stmp/${USER}/${model}/${PSLOT}
export DCOMROOT=/lfs/h1/ops/prod/dcom
mkdir -p ${DATAROOT} # ${COMevs}
