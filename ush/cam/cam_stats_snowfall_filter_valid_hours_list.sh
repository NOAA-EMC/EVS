#!/bin/bash -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - CAM
##
## CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov, Affiliate @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Filter list of valid hours depending on the current vhr value (precip)
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

set -x

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

if [ -z "${vhr}" ]; then
    err_exit "vhr is unset."
fi
if [ -z "${VHOUR_LIST}" ]; then
    err_exit "VHOUR_LIST is unset."
fi

echo "REQUESTED LIST OF VALID HOURS: $VHOUR_LIST"
NEW_VHOUR_LIST=""
if [ $vhr -ge 0 ] && [ $vhr -lt 6 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 0 ] && [ $VHOUR -le 5 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 6 ] && [ $vhr -lt 12 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 6 ] && [ $VHOUR -le 11 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 12 ] && [ $vhr -lt 18 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 12 ] && [ $VHOUR -le 17 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 18 ] && [ $vhr -le 23 ]; then
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
