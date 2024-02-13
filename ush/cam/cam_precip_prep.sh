#!/bin/bash
#########################################
#
# NAME: cam_precip_prep.sh 
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Prepare data for CAM precipitation verification 
# DEPENDENCIES:
#
########################################

set -x

if [ $STEP == "prep" ]; then
    if [ $COMPONENT == "cam" ]; then
        if [ $VERIF_CASE == "precip" ]; then
            if [ $OBSNAME == "ccpa" ]; then
                subtract_hours_inc=$(echo $OBS_ACC | sed 's/^0*//')
                subtract_hours=0
                max_subtract_hours=$(echo $ACC | sed 's/^0*//')
                while [ $subtract_hours -lt $max_subtract_hours ]; do
                    VDATEHOURm=$($NDATE -$subtract_hours $VDATE$VHOUR)
                    VDATEm=${VDATEHOURm:0:8}
                    VHOURm=${VDATEHOURm:8:10}
                    export COMOUTobs="${DATA}/ccpa.$VDATEm"
                    if [ ! -f $COMOUTobs/ccpa.t${VHOURm}z.${OBS_ACC}h.hrap.conus.gb2 ]; then
                        if [ ! -d $COMOUTobs ]; then
                            mkdir -p $COMOUTobs
                        fi
                        infile=$COMINobs/ccpa.$VDATEm/*/ccpa.t${VHOURm}z.${OBS_ACC}h.hrap.conus.gb2
                        if [ -f $infile ]; then
                            cp $infile $COMOUTobs/.
                        else
                            echo "WARNING: Input $OBSNAME file does not exist: $infile ..."
                            echo "The file may not be available yet, or may have aged out."  
                            echo "This is usually OK: this job runs several times a day to catch such files." 
                            echo "Continuing to the next valid datetime."
                        fi
                    fi
                    subtract_hours=$(( $subtract_hours + $subtract_hours_inc ))
                done
            else
                err_exit "$OBSNAME is not a valid reference data source."
            fi
        else
            err_exit "$VERIF_CASE is not a valid VERIF_CASE for cam_precip_prep.sh (please use 'precip')"
        fi
    else
        err_exit "$COMPONENT is not a valid COMPONENT for cam_precip_prep.sh (please use 'cam')"
    fi
else
    err_exit "$STEP is not a valid STEP for cam_precip_prep.sh (please use 'prep')"
fi
