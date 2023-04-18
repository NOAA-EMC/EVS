#!/bin/bash -e
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------
## NCEP EMC Verification System (EVS) - CAM
##
## CONTRIBUTORS: Marcel Caron, marcel.caron@noaa.gov, Affiliate @ NOAA/NWS/NCEP/EMC-VPPPGB
## PURPOSE: Filter list of valid hours depending on the current cyc value (grid2obs)
##---------------------------------------------------------------------------
##---------------------------------------------------------------------------

echo "BEGIN: $(basename ${BASH_SOURCE[0]})"

if [ -z "${cyc}" ]; then
    echo "ERROR: cyc is unset."
    exit 1
fi
if [ -z "${VHOUR_LIST}" ]; then
    echo "ERROR: VHOUR_LIST is unset."
    exit 1
fi

echo "REQUESTED LIST OF VALID HOURS: $VHOUR_LIST"
NEW_VHOUR_LIST=""
if [ $cyc -ge 0 ] && [ $cyc -le 2 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 0 ] && [ $VHOUR -le 2 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $cyc -ge 3 ] && [ $cyc -le 5 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 3 ] && [ $VHOUR -le 5 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $cyc -ge 6 ] && [ $cyc -le 8 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 6 ] && [ $VHOUR -le 8 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $cyc -ge 9 ] && [ $cyc -le 11 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 9 ] && [ $VHOUR -le 11 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $cyc -ge 12 ] && [ $cyc -le 14 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 12 ] && [ $VHOUR -le 14 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $cyc -ge 15 ] && [ $cyc -le 17 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 15 ] && [ $VHOUR -le 17 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $cyc -ge 18 ] && [ $cyc -le 20 ]; then
    for VHOUR in $VHOUR_LIST; do
        if [ $VHOUR -ge 18 ] && [ $VHOUR -le 20 ]; then
            NEW_VHOUR_LIST+="$VHOUR "
        fi
    done
elif [ $cyc -ge 21 ] && [ $cyc -le 23 ]; then
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
