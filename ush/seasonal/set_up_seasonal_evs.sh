#!/bin/ksh -xe
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC VERIFICATION SYSTEM
##
## CONTRIBUTORS: Shannon Shields, Shannon.Shields@noaa.gov, NWS/NCEP/EMC-VPPGB
## PURPOSE: Set up environment based on user configurations
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: set_up_seasonal_evs.sh"

export NET="evs"
export RUN_ENVIR="emc"
export envir="dev"

## Create output directory and set output related environment variables
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
export COMROOT="$OUTPUTROOT/com"
export NWGESROOT="$OUTPUTROOT/nwges"
export DCOMROOT="$OUTPUTROOT/dcom"
export PCOMROOT="$OUTPUTROOT/pcom"
export DATAROOT="$OUTPUTROOT/tmpnw${envir}"
export job=${job:-$LSB_JOBNAME}
export jobid=${jobid:-$$}
export DATA=${DATAROOT}/$NET.$jobid
mkdir -p $COMROOT $NWGESROOT $DCOMROOT $PCOMROOT $DATAROOT $DATA
mkdir -p $COMROOT/$NET/$envir
mkdir -p $COMROOT/logs/jlogfiles
mkdir -p $COMROOT/output/$envir/today
mkdir -p $COMROOT/output/$envir/$(date +%Y%m%d)
export DCOM=${DCOM:-$DCOMROOT/$NET}
export PCOM=${PCOM:-$PCOMROOT/$NET}
export GESIN=${GESIN:-$GESROOT/$envir}
export GESOUT=${GESOUT:-$GESROOT/$envir}
mkdir -p $DCOM $PCOM
cd $DATA
echo

## Get machine, set environment variable 'machine', and check that it is a supported machine
python $HOMEevs/ush/seasonal/get_machine.py
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully ran get_machine.py"
echo

if [ -s config.machine ]; then
    . $DATA/config.machine
    status=$?
    [[ $status -ne 0 ]] && exit $status
    [[ $status -eq 0 ]] && echo "Successfully sourced config.machine"
fi

if [[ "$machine" =~ ^(HERA|ORION|WCOSS_C|WCOSS_DELL_P3)$ ]]; then
   echo
else
    echo "ERROR: $machine is not a supported machine"
    exit 1
fi

## Load modules, set paths to MET and METplus, and some executables
. $HOMEevs/ush/seasonal/load_modules.sh
status=$?
[[ $status -ne 0 ]] && exit $status
[[ $status -eq 0 ]] && echo "Successfully loaded modules"
echo

## Set paths for evs, MET, and METplus
export HOMEevs=$HOMEevs
export PARMevs=$HOMEevs/parm
export USHevs=$HOMEevs/ush
export UTILevs=$HOMEevs/util
export EXECevs=$HOMEevs/exec
export HOMEMET=$HOMEMET
export HOMEMETplus=$HOMEMETplus
export PARMMETplus=$HOMEMETplus/parm
export USHMETplus=$HOMEMETplus/ush
export PATH="${USHMETplus}:${PATH}"
export PYTHONPATH="${USHMETplus}:${PYTHONPATH}"

## Set machine specific fix directory
if [ $machine = "HERA" ]; then
    export FIXevs="/scratch1/NCEPDEV/global/glopara/fix/fix_verif"
elif [ $machine = "ORION" ]; then
    export FIXevs="/work/noaa/global/glopara/fix/fix_verif"
elif [ $machine = "WCOSS_C" ] ; then
    export FIXevs="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/EVS_fix"
    export members="4"
elif [ $machine = "WCOSS_DELL_P3" ]; then
    export FIXevs="/gpfs/dell2/emc/modeling/noscrub/emc.glopara/git/fv3gfs/fix/fix_verif"
    export BinClim_Path="/gpfs/dell2/emc/verification/noscrub/Binbin.Zhou/grid2grid/EMC_verif-gefs.v1.0.0/fix"
    export maskpath="/gpfs/dell2/emc/modeling/noscrub/emc.glopara/git/fv3gfs/fix/fix_verif/vx_mask_files/grid2obs"
    #export maskpath="/gpfs/dell2/emc/verification/noscrub/Binbin.Zhou/grid2grid/EMC_verif-gefs.v1.0.0/parm/mask"
    #export copygb=${copygb:-/gpfs/dell1/nco/ops/nwprod/grib_util.v1.1.1/exec/copygb}
    export members="30"
fi

## Set machine specific account, queues, and run settings
if [ $machine = "HERA" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
    export PARTITION_BATCH=""
    export nproc="40"
    export MPMD="YES"
elif [ $machine = "ORION" ]; then
    export ACCOUNT="fv3-cpu"
    export QUEUE="batch"
    export QUEUESHARED="batch"
    export QUEUESERV="service"
    export PARTITION_BATCH="orion"
    export nproc="40"
    export MPMD="YES"
elif [ $machine = "WCOSS_C" -o $machine = "WCOSS_DELL_P3" ]; then
    export ACCOUNT="GFS-DEV"
    export QUEUE="dev"
    export QUEUESHARED="dev_shared"
    export QUEUESERV="dev_transfer"
    export PARTITION_BATCH=""
    if [ $machine = "WCOSS_C" ]; then
        export nproc="24"
    elif [ $machine = "WCOSS_DELL_P3" ]; then
        export nproc="28"
    fi
    export MPMD="YES"
fi

## Set machine and user specific directories
if [ $machine = "HERA" ]; then
    export NWROOT="/scratch1/NCEPDEV/global/glopara/nwpara"
    export HOMEDIR="/scratch1/NCEPDEV/global/$USER"
    export STMP="/scratch1/NCEPDEV/stmp2/$USER"
    export PTMP="/scratch1/NCEPDEV/stmp4/$USER"
    export NOSCRUB="/scratch1/NCEPDEV/global/$USER"
    export global_archive="/scratch1/NCEPDEV/global/Mallory.Row/archive"
    export prepbufr_arch_dir="/scratch1/NCEPDEV/global/Mallory.Row/prepbufr"
    export obdata_dir="/scratch1/NCEPDEV/global/Mallory.Row/obdata"
    export ccpa_24hr_arch_dir="/scratch1/NCEPDEV/global/Mallory.Row/obdata/ccpa_accum24hr"
    export METviewer_AWS_scripts_dir="/scratch1/NCEPDEV/global/Mallory.Row/VRFY/METviewer_AWS"
elif [ $machine = "ORION" ]; then
    export NWROOT=${NWROOT:-"/work/noaa/global/glopara/nwpara"}
    export HOMEDIR="/work/noaa/nems/$USER"
    export STMP="/work/noaa/stmp/$USER"
    export PTMP="/work/noaa/stmp/$USER"
    export NOSCRUB="/work/noaa/nems/$USER"
    export global_archive="/work/noaa/ovp/mrow/archive"
    export prepbufr_arch_dir="/work/noaa/ovp/mrow/prepbufr"
    export obdata_dir="/work/noaa/ovp/mrow/obdata"
    export ccpa_24hr_arch_dir="/work/noaa/ovp/mrow/obdata/ccpa_accum24hr"
    export METviewer_AWS_scripts_dir="/work/noaa/ovp/mrow/VRFY/METviewer_AWS"
elif [ $machine = "WCOSS_C" ]; then
    export NWROOT=${NWROOT:-"/lfs/h1/nco"}
    export HOMEDIR="/lfs/h2/emc/vpppg/noscrub/$USER"
    export STMP="/lfs/h2/emc/stmp/$USER"
    export PTMP="/lfs/h2/emc/ptmp/$USER"
    export NOSCRUB="/lfs/h2/emc/vpppg/noscrub/$USER"
    export global_archive="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive_wcoss2"
    export prepbufr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive_wcoss2/obs_data/prepbufr"
    export obdata_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive_wcoss2/obs_data"
    export ccpa_24hr_arch_dir="/lfs/h2/emc/vpppg/noscrub/emc.vpppg/verification/global/archive_wcoss2/obs_data/ccpa_accum24hr"
    export METviewer_AWS_scripts_dir="/lfs/h2/emc/vpppg/save/emc.vpppg/verification/metplus/metviewer_aws_scripts"
elif [ $machine = "WCOSS_DELL_P3" ]; then
    export NWROOT=${NWROOT:-"/gpfs/dell1/nco/ops/nwprod"}
    export HOMEDIR="/gpfs/dell2/emc/modeling/noscrub/$USER"
    export STMP="/gpfs/dell3/stmp/$USER"
    export PTMP="/gpfs/dell3/ptmp/$USER"
    export NOSCRUB="/gpfs/dell2/emc/modeling/noscrub/$USER"
    export global_archive="/gpfs/dell2/emc/verification/noscrub/emc.verif/global/archive"
    export prepbufr_arch_dir="/gpfs/dell2/emc/verification/noscrub/emc.verif/global/archive/prepbufr"
    export obdata_dir="/gpfs/dell2/emc/verification/noscrub/emc.verif/global/archive"
    export ccpa_24hr_arch_dir="/gpfs/dell2/emc/verification/noscrub/emc.verif/global/archive/ccpa_accum24hr"
    export METviewer_AWS_scripts_dir="/gpfs/dell2/emc/verification/noscrub/emc.metplus/METviewer_AWS"
fi

## Set operational directories
export prepbufr_prod_upper_air_dir="/lfs/h1/ops/prod/com/gfs/v16.2"
export prepbufr_prod_conus_sfc_dir="/lfs/h1/ops/prod/com/obsproc/v1.0"
export ccpa_24hr_prod_dir="/lfs/h1/ops/prod/com/ccpa/v4.2"
#export nhc_atcfnoaa_bdeck_dir="/gpfs/dell2/nhc/noscrub/data/atcf-noaa/btk"
#export nhc_atcfnoaa_adeck_dir="/gpfs/dell2/nhc/noscrub/data/atcf-noaa/aid_nws"
#export nhc_atcfnavy_bdeck_dir="/gpfs/dell2/nhc/noscrub/data/atcf-navy/btk"
#export nhc_atcfnavy_adeck_dir="/gpfs/dell2/nhc/noscrub/data/atcf-navy/aid"

## Set online and FTP sites
export nhc_atcf_bdeck_ftp="ftp://ftp.nhc.noaa.gov/atcf/btk/"
export nhc_atcf_adeck_ftp="ftp://ftp.nhc.noaa.gov/atcf/aid_public/"
export nhc_atfc_arch_ftp="ftp://ftp.nhc.noaa.gov/atcf/archive/"
export navy_atcf_bdeck_ftp="https://www.metoc.navy.mil/jtwc/products/best-tracks/"
export iabp_ftp="http://iabp.apl.washington.edu/Data_Products/Daily_Full_Res_Data"
export ghrsst_ncei_avhrr_anl_ftp="https://podaac-opendap.jpl.nasa.gov/opendap/allData/ghrsst/data/GDS2/L4/GLOB/NCEI/AVHRR_OI/v2.1"
export ghrsst_ospo_geopolar_anl_ftp="https://podaac-opendap.jpl.nasa.gov/opendap/hyrax/allData/ghrsst/data/GDS2/L4/GLOB/OSPO/Geo_Polar_Blended/v1"

echo "END: set_up_verif_global.sh"
