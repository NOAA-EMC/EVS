#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_wave_prep.sh
# Developers: Deanna Spindler / Deanna.Spindler@noaa.gov
#             Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: This script is run for the global_det wave prep step
###############################################################################

set -x

cd $DATA
echo "in $0"
echo "Starting ${COMPONENT} ${RUN} prep"
echo "Starting at : `date`"

# Prep model files
for MODEL in $MODELNAME; do
    echo ' '
    echo " *** ${MODELNAME}-${RUN} prep ***"
    mkdir -p ${DATA}/${MODEL}
    # Copy the GFS 0.25 degree wave forecast files
    if [ $MODEL == "gfs" ]; then
        inithours='00 06 12 18'
        lead_hours='000 006 012 018 024 030 036 042 048 054 060 066 072 078
            084 090 096 102 108 114 120 126 132 138 144 150 156 162
            168 174 180 186 192 198 204 210 216 222 228 234 240 246
            252 258 264 270 276 282 288 294 300 306 312 318 324 330
            336 342 348 354 360 366 372 378 384'
        for inithour in ${inithours} ; do
            for hr in ${lead_hours} ; do
                input_filename="${COMINgfs}/${inithour}/wave/gridded/gfswave.t${inithour}z.global.0p25.f${hr}.grib2"
                tmp_filename="${DATA}/${MODEL}/gfswave.${INITDATE}.t${inithour}z.global.0p25.f${hr}.grib2"
                output_filename="${COMOUT}.${INITDATE}/${MODEL}/gfswave.${INITDATE}.t${inithour}z.global.0p25.f${hr}.grib2"
                if [ ! -s $output_filename ] ; then
                    if [ ! -s $input_filename ] ; then
                        echo "WARNING: ${input_filename} does not exist"
                        if [ $SENDMAIL = YES ] ; then
                            export subject="F${hr} GFS Forecast Data Missing for EVS ${COMPONENT}"
                            echo "Warning: No GFS forecast was available for ${INITDATE}${inithour}f${hr}" > mailmsg
                            echo "Missing file is ${input_filename}" >> mailmsg
                            echo "Job ID: $jobid" >> mailmsg
                            cat mailmsg | mail -s "$subject" $MAILTO
                        fi
                    else
                        cp -v $input_filename $tmp_filename
                        if [ $SENDCOM = YES ]; then
                            if [ -s $tmp_filename ]; then
                                 cp -v $tmp_filename $output_filename
                            fi
                        fi
                    fi
                else
                    echo "${output_filename} already exists"
                fi
            done
        done
    fi
done

# Prep the observation files
for OBS in $OBSNAME; do
    echo " *** ${OBSNAME}-${RUN} prep ***"
    mkdir -p ${DATA}/${OBS}
    # Run PB2NC for GDAS prepbufr files
    if [ $OBS == "prepbufr_gdas" ]; then
        for ihour in 00 06 12 18; do
            input_prepbufr_file=${COMINobsproc}/gdas.${INITDATE}/${ihour}/atmos/gdas.t${ihour}z.prepbufr
            tmp_pb2nc_file=${DATA}/${OBS}/gdas.SFCSHP.${INITDATE}${ihour}.nc
            output_pb2nc_file=${COMOUT}.${INITDATE}/${OBS}/gdas.SFCSHP.${INITDATE}${ihour}.nc
            if [ ! -s $output_pb2nc_file ]; then
                if [ ! -s $input_prepbufr_file ]; then
                    echo "WARNING: ${input_prepbufr_file} does not exist"
                    if [ $SENDMAIL = YES ] ; then
                        export subject="GDAS Prepbufr Data Missing for EVS ${COMPONENT}"
                        echo "Warning: No GDAS Prepbufr was available for valid date ${INITDATE}${ihour}" > mailmsg
                        echo "Missing file is $input_prepbufr_file" >> mailmsg
                        echo "Job ID: $jobid" >> mailmsg
                        cat mailmsg | mail -s "$subject" $MAILTO
                    fi
                else
                    export init_hour=${ihour}
                    # Split by subset
                    split_by_subset $input_prepbufr_file
                    export err=$?; err_chk
                    if [ -s ${DATA}/SFCSHP ]; then
                        run_metplus.py \
                        -c ${PARMevs}/metplus_config/machine.conf \
                        -c ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_grid2obs/PB2NC_obsPrepbufrGDAS.conf
                        export err=$?; err_chk
                    fi
                    if [ -s $tmp_pb2nc_file ]; then
                        chmod 640 $tmp_pb2nc_file
                        chgrp rstprod $tmp_pb2nc_file
                        if [ ${SENDCOM} = YES ]; then
                            cp -v ${tmp_pb2nc_file} ${output_pb2nc_file}
                            if [ -s $output_pb2nc_file ]; then
                                chmod 640 $output_pb2nc_file
                                chgrp rstprod $output_pb2nc_file
                            fi
                        fi
                    fi
                fi
            else
                echo "${output_pb2nc_file} already exists"
            fi
        done
    # Trim down the NDBC buoy files and run ASCII2NC
    elif [ $OBS == "ndbc" ]; then
        export INITDATEp1=$($NDATE +24 ${INITDATE}${vhr} | cut -c 1-8)
        input_ndbc_dir=${DCOMINndbc}/${INITDATEp1}/validation_data/marine/buoy
        tmp_ndbc_file=${DATA}/${OBS}/${OBS}.${INITDATE}.nc
        output_ndbc_file=${COMOUT}.${INITDATE}/${OBS}/${OBS}.${INITDATE}.nc
        if [ ! -s $output_ndbc_file ]; then
            ndbc_txt_ncount=$(ls -l ${input_ndbc_dir}/*.txt |wc -l)
            if [[ $ndbc_txt_ncount -eq 0 ]]; then
                echo "WARNING: No NDBC data in ${input_ndbc_dir}"
                if [ $SENDMAIL = YES ] ; then
                    export subject="NDBC Data Missing for EVS ${COMPONENT}"
                    echo "Warning: No NDBC data was available for valid date ${INITDATE}" > mailmsg
                    echo "Missing files are located at ${input_ndbc_dir}" >> msg
                    echo "Job ID: $jobid" >> mailmsg
                    cat mailmsg | mail -s "$subject" $MAILTO
                fi
            else
                python $USHevs/${COMPONENT}/global_det_wave_prep_trim_ndbc_files.py
                export err=$?; err_chk
                trimmed_ndbc_txt_ncount=$(ls -l ${DATA}/ndbc/*.txt |wc -l)
                if [[ $trimmed_ndbc_txt_ncount -eq 0 ]]; then
                    echo "NOTE: No files matching ${DATA}/ndbc/*.txt"
                else
                    export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml
                    run_metplus.py \
                    -c ${PARMevs}/metplus_config/machine.conf \
                    -c ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_grid2obs/ASCII2NC_obsNDBC.conf
                    export err=$?; err_chk
                    if [ ${SENDCOM} = YES ]; then
                        if [ ${tmp_ndbc_file} ]; then
                            cp -v ${tmp_ndbc_file} ${output_ndbc_file}
                        fi
                    fi
                fi
            fi
        else
            echo "$output_ndbc_file already exists"
        fi
    fi
done

echo ' '
echo "Ending ${COMPONENT} ${RUN} prep"
echo "Ending at : `date`"
echo ' '
