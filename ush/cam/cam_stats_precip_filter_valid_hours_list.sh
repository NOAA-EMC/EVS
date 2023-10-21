#!/bin/bash -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - CAM
##
## CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov, Affiliate @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Filter list of valid hours depending on the current vhr value (precip)
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

if [ -z ${vhr} ]; then
    echo "ERROR: vhr is unset."
    exit 1
fi
if [ -z ${VHOUR_LIST} ]; then
    echo "ERROR: VHOUR_LIST is unset."
    exit 1
fi

echo "REQUESTED LIST OF VALID HOURS: $VHOUR_LIST"
NEW_VHOUR_LIST=""
if [ $vhr -ge 19 ] && [ $vhr -lt 20 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 0 ] && [ $VHOUR -le 5 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 20 ] && [ $vhr -lt 21 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 6 ] && [ $VHOUR -le 11 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 21 ] && [ $vhr -lt 22 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 12 ] && [ $VHOUR -le 17 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 22 ] && [ $vhr -le 23 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 18 ] && [ $VHOUR -le 23 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
fi
echo "FILTERED LIST OF VALID HOURS (BASED ON CYCLE): $NEW_VHOUR_LIST"
export VHOUR_LIST=$NEW_VHOUR_LIST
[[ -z "$VHOUR_LIST" ]] && { echo "All VHOURs were filtered out based on the cycle."; }

echo "END: $(basename ${BASH_SOURCE[0]})"
