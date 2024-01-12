#!/bin/bash -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - MESOSCALE
##
## CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov, Affiliate @ NOAA/NWS/NCEP/EMC-VPPPGB
## CONTRIBUTORS: RS, roshan.shrestha@noaa.gov, Affiliate @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Filter list of valid hours depending on the current vhr value (grid2obs)
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

set -x

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

if [ -z "${vhr}" ]; then
    err_exit "ERROR: vhr is unset."
fi
if [ -z "${VHOUR_LIST}" ]; then
    err_exit "ERROR: VHOUR_LIST is unset."
fi

echo "REQUESTED LIST OF VALID HOURS: $VHOUR_LIST"
NEW_VHOUR_LIST=""
if [ $vhr -ge 0 ] && [ $vhr -le 2 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 0 ] && [ $VHOUR -le 2 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 3 ] && [ $vhr -le 5 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 3 ] && [ $VHOUR -le 5 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 6 ] && [ $vhr -le 8 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 6 ] && [ $VHOUR -le 8 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 9 ] && [ $vhr -le 11 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 9 ] && [ $VHOUR -le 11 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 12 ] && [ $vhr -le 14 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 12 ] && [ $VHOUR -le 14 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 15 ] && [ $vhr -le 17 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 15 ] && [ $VHOUR -le 17 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 18 ] && [ $vhr -le 20 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 18 ] && [ $VHOUR -le 20 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $vhr -ge 21 ] && [ $vhr -le 23 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 21 ] && [ $VHOUR -le 23 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
fi
echo "FILTERED LIST OF VALID HOURS (BASED ON CYCLE): $NEW_VHOUR_LIST"
export VHOUR_LIST=$NEW_VHOUR_LIST
[[ -z "$VHOUR_LIST" ]] && { echo "All VHOURs were filtered out based on the cycle."; }

echo "END: $(basename ${BASH_SOURCE[0]})"
