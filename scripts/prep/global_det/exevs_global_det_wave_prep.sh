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
                tmp_filename="${DATA}/gfswave.${INITDATE}.t${inithour}z.global.0p25.f${hr}.grib2"
                output_filename="$COMOUT.${INITDATE}/${MODEL}/gfswave.${INITDATE}.t${inithour}z.global.0p25.f${hr}.grib2"
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
                    if [ ! -s $output_filename ] ; then
                        cp -v $input_filename $tmp_filename
                        if [ $SENDCOM = YES ]; then
                            if [ -f $tmp_filename ]; then
                                cp -v $tmp_filename $output_filename
                            fi
                        fi
                    fi
                fi
            done
        done
    fi
done

# Prep the observation files
for OBS in $OBSNAME; do
    echo " *** ${OBSNAME}-${RUN} prep ***"
    # Trim down the NDBC buoy files
    if [ $OBS == "ndbc" ]; then
        export INITDATEp1=$($NDATE +24 ${INITDATE}${vhr} | cut -c 1-8)
        nbdc_txt_ncount=$(ls -l $DCOMINndbc/${INITDATEp1}/validation_data/marine/buoy/*.txt |wc -l)
        if [[ $nbdc_txt_ncount -eq 0 ]]; then
            echo "WARNING: No NDBC data in $DCOMINndbc/${INITDATEp1}/validation_data/marine/buoy"
            if [ $SENDMAIL = YES ] ; then
                export subject="NDBC Data Missing for EVS ${COMPONENT}"
                echo "Warning: No NDBC data was available for valid date ${VDATE}" > mailmsg
                echo "Missing files are located at $DCOMINndbc/${INITDATEp1}/validation_data/marine/buoy" >> msg
                echo "Job ID: $jobid" >> mailmsg
                cat mailmsg | mail -s "$subject" $MAILTO
            fi
        else
            python $USHevs/${COMPONENT}/global_det_wave_prep_trim_ndbc_files.py
            export err=$?; err_chk
        fi
    fi
done

echo ' '
echo "Ending ${COMPONENT} ${RUN} prep"
echo "Ending at : `date`"
echo ' '
