#!/bin/bash
#########################################
#
# NAME: cam_precip_prep.sh 
# CONTRIBUTOR(S): Marcel Caron, marcel.caron@noaa.gov, NOAA/NWS/NCEP/EMC-VPPPGB
# PURPOSE: Prepare data for CAM precipitation verification 
# DEPENDENCIES:
#
########################################

if [ $STEP == "prep" ]; then
    if [ $COMPONENT == "cam" ]; then
        if [ $VERIF_CASE == "precip" ]; then
            if [ $OBSNAME == "ccpa" ]; then
                VDATEHOUR=$(date -d "$( date -d $VDATE +'%Y-%m-%d' ) $VHOUR:00:00" "+%Y-%m-%d %H:%M:%S UTC")
                subtract_hours_inc=$(echo $OBS_ACC | sed 's/^0*//')
                subtract_hours=0
                max_subtract_hours=$(echo $ACC | sed 's/^0*//')
                while [ $subtract_hours -lt $max_subtract_hours ]; do
                    VDATEm=$(date -d "$VDATEHOUR -$subtract_hours hours" +"%Y%m%d")
                    VHOURm=$(date -d "$VDATEHOUR -$subtract_hours hours" +"%H")
                    export COMOUTobs="${DATA}/ccpa.$VDATEm"
                    if [ ! -f $COMOUTobs/ccpa.t${VHOURm}z.${OBS_ACC}h.hrap.conus.gb2 ]; then
                        if [ ! -d $COMOUTobs ]; then
                            mkdir -p $COMOUTobs
                        fi
                        infile=$COMINobs/ccpa.$VDATEm/*/ccpa.t${VHOURm}z.${OBS_ACC}h.hrap.conus.gb2
                        if [ -f $infile ]; then
                            cp $infile $COMOUTobs/.
                        else
                            echo "Input $OBSNAME file does not exist: $infile ... Continuing to the next valid datetime."
                        fi
                    fi
                    subtract_hours=$(( $subtract_hours + $subtract_hours_inc ))
                done
            else
                echo "$OBSNAME is not a valid reference data source."
                exit 1
            fi
        else
            echo "$VERIF_CASE is not a valid VERIF_CASE for cam_precip_prep.sh (please use 'precip')"
            exit 1
        fi
    else
        echo "$COMPONENT is not a valid COMPONENT for cam_precip_prep.sh (please use 'cam')"
        exit 1
    fi
else
    echo "$STEP is not a valid STEP for cam_precip_prep.sh (please use 'prep')"
    exit 1
fi
exit 0
