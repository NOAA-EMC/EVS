#!/bin/bash -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - CAM
##
## CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov, Affiliate @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Filter list of initialization hours depending on the current vhr value (precip)
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

set -x

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

if [ -z "${vhr}" ]; then
    err_exit "vhr is unset."
fi
if [ -z "${IHOUR_LIST}" ]; then
    err_exit "IHOUR_LIST is unset."
fi

echo "REQUESTED LIST OF INIT HOURS: $IHOUR_LIST"
NEW_IHOUR_LIST=""
if [ $vhr -ge 00 ] && [ $vhr -lt 06 ]; then
    for IHOUR in $IHOUR_LIST; do
        if [ $IHOUR -ge 0 ] && [ $IHOUR -le 5 ]; then
            NEW_IHOUR_LIST+="$IHOUR "
        fi
    done
elif [ $vhr -ge 06 ] && [ $vhr -lt 12 ]; then
    for IHOUR in $IHOUR_LIST; do
        if [ $IHOUR -ge 6 ] && [ $IHOUR -le 11 ]; then
            NEW_IHOUR_LIST+="$IHOUR "
        fi
    done
elif [ $vhr -ge 12 ] && [ $vhr -lt 18 ]; then
    for IHOUR in $IHOUR_LIST; do
        if [ $IHOUR -ge 12 ] && [ $IHOUR -le 17 ]; then
            NEW_IHOUR_LIST+="$IHOUR "
        fi
    done
elif [ $vhr -ge 18 ] && [ $vhr -le 23 ]; then
    for IHOUR in $IHOUR_LIST; do
        if [ $IHOUR -ge 18 ] && [ $IHOUR -le 23 ]; then
            NEW_IHOUR_LIST+="$IHOUR "
        fi
    done
fi
echo "FILTERED LIST OF INIT HOURS (BASED ON CYCLE): $NEW_IHOUR_LIST"
export IHOUR_LIST=$NEW_IHOUR_LIST
[[ -z "$IHOUR_LIST" ]] && { echo "All IHOURs were filtered out based on the cycle."; }

echo "END: $(basename ${BASH_SOURCE[0]})"
