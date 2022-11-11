#!/bin/bash -l

VDATEp1=$(date -d "${VDATE} + 1 day" +%Y%m%d)
VDATEm1=$(date -d "${VDATE} - 1 day" +%Y%m%d)
VDATEm2=$(date -d "${VDATE} - 2 day" +%Y%m%d)
VDATEm3=$(date -d "${VDATE} - 3 day" +%Y%m%d)
if [[ ${DAY} == 1 ]]; then
    declare -a OTLKs=("0100" "1200" "1300" "1630" "2000")
elif [[ ${DAY} == 2 ]]; then
    declare -a OTLKs=("0600" "0700" "1730")
elif [[ ${DAY} == 3 ]]; then
    declare -a OTLKs=("0730" "0830")
fi

for OTLK in "${OTLKs[@]}"; do
    if [[ ${DAY} == 1 ]]; then
        if [[ ${VHOUR_GROUP} == "LT1200" ]]; then
            V2DATE=${VDATE}
            [ "${OTLK}" -lt "1200" ] && V1DATE=${VDATE} || V1DATE=${VDATEm1}
            V1HOUR=${OTLK}
            [ "${OTLK}" -lt "1200" ] && IDATE=${VDATE} || IDATE=${VDATEm1}
        elif [[ ${VHOUR_GROUP} == "GE1200" ]]; then
            V1DATE=${VDATE}
            [ "${OTLK}" -lt "1200" ] && V2DATE=${VDATE} || V2DATE=${VDATEp1}
            V1HOUR=${OTLK}
            IDATE=${VDATE}
        fi
    elif [[ ${DAY} == 2 ]]; then
        if [[ ${VHOUR_GROUP} == "LT1200" ]]; then
            V1DATE=${VDATEm1}
            V2DATE=${VDATE}
            V1HOUR="1200"
            IDATE=${VDATEm2}
        elif [[ ${VHOUR_GROUP} == "GE1200" ]]; then
            V1DATE=${VDATE}
            V2DATE=${VDATEp1}
            V1HOUR="1200"
            IDATE=${VDATEm1}
        fi
    elif [[ ${DAY} == 3 ]]; then
        if [[ ${VHOUR_GROUP} == "LT1200" ]]; then
            V1DATE=${VDATEm1}
            V2DATE=${VDATE}
            V1HOUR="1200"
            IDATE=${VDATEm3}
        elif [[ ${VHOUR_GROUP} == "GE1200" ]]; then
            V1DATE=${VDATE}
            V2DATE=${VDATEp1}
            V1HOUR="1200"
            IDATE=${VDATEm2}
        fi
    fi
    V2HOUR="1200"
    YYYY=${IDATE:0:4}
    ZIP_FILE="day${DAY}otlk_${IDATE}_${OTLK}-shp.zip"
    URL="${URL_HEAD}/${YYYY}/${ZIP_FILE}"
    if [[ `wget -S --spider ${URL} 2>&1 | grep 'HTTP/1.1 200 OK'` ]]; then
        wget ${URL} -P ${TEMP_DIR}
        unzip ${TEMP_DIR}/${ZIP_FILE}
        export SHP_FILE=day${DAY}otlk_${IDATE}_${OTLK}_cat
      
        N_REC=`gis_dump_dbf ${TEMP_DIR}.dbf | grep n_records | cut -d'=' -f2 | tr -d ' '`
        echo "Processing $N_REC records."
      
        # This only prints that there are no defined general thunderstorm areas ... the next loop is skipped automatically
        if [[ $N_REC == 0 ]]; then
            echo "No Day ${DAY} Outlook areas issued on ${IDATE}"
        fi
      
        # If N_REC > 0, loop over records and create a new mask for each, otherwise skip
        N_REC_MINUS_1=$(($N_REC - 1))
        for REC in $(seq 0 $N_REC_MINUS_1); do
            export REC=$REC
            NAME=`gis_dump_dbf ${TEMP_DIR}/${SHP_FILE}.dbf | egrep -A 5 "^Record ${REC}" | tail -1 | cut -d'"' -f2`
            echo "Processing Record Number $REC: $NAME"
            
            export MASK_FNAME="spc_otlk_d${DAY}_${OTLK}_v${V1DATE}${V1HOUR}-${V2DATE}${V2HOUR}"

            if [[ ${DAY} == 3 ]]; then
                export MASK_NAME=DAY${DAY}_${NAME}
            else
                export MASK_NAME=DAY${DAY}_${OTLK}_${NAME}
            fi
            ${metplus_launcher} -c ${MET_PLUS_CONF}/GenVxMask_SPC_OTLK.conf
        done
    fi
done


# ====================== COMMANDS TO PUT IN SCRIPTS DIR ======================
# Copy CONUS vx masks to ptmp directory
# Allows METplus to search for mask files in ptmp
# Rather than creating large archive of SPC masks in noscrub
#for TOGRID in $GRIDS; do
#
#   cp ${OUTPUT_BASE}/*.nc $COMOUT/$OBS_DIR/.
#
#done 
# ============================================================================

exit
