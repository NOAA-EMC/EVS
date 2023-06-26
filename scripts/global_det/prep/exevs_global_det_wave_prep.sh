#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_wave_prep.sh                       
# Deanna Spindler / Deanna.Spindler@noaa.gov
# Mallory Row / Mallory.Row@noaa.gov
# Purpose of Script: Run the prep for any global determinstic wave models   
###############################################################################

set -x 

###################################
## Global Wave Model Prep 
###################################

cd $DATA
echo "in $0"
echo "Starting ${COMPONENT} ${RUN} prep"
echo "Starting at : `date`"

for MODEL in $MODELNAME; do
    echo ' '
    echo ' *************************************'
    echo " *** ${MODELNAME}-${RUN} prep ***"
    echo ' *************************************'
    echo ' '
    if [ $MODEL == "gfs" ]; then
        cycles='00 06 12 18'
        lead_hours='000 006 012 018 024 030 036 042 048 054 060 066 072 078
            084 090 096 102 108 114 120 126 132 138 144 150 156 162
            168 174 180 186 192 198 204 210 216 222 228 234 240 246
            252 258 264 270 276 282 288 294 300 306 312 318 324 330 
            336 342 348 354 360 366 372 378 384'
        for cyc in ${cycles} ; do
            for hr in ${lead_hours} ; do
                COMINfilename="${COMINgfs}/${cyc}/wave/gridded/gfswave.t${cyc}z.global.0p25.f${hr}.grib2"
                DATAfilename="${DATA}/gfswave.${INITDATE}.t${cyc}z.global.0p25.f${hr}.grib2"
                COMOUTfilename="$COMOUT.${INITDATE}/${MODEL}/gfswave.${INITDATE}.t${cyc}z.global.0p25.f${hr}.grib2"
                if [ ! -s $COMINfilename ] ; then
                    export subject="F${hr} GFS Forecast Data Missing for EVS ${COMPONENT}"
                    echo "Warning: No GFS forecast was available for ${INITDATE}${cyc}f${hr}" > mailmsg
                    echo “Missing file is ${COMINfilename}” >> mailmsg
                    echo "Job ID: $jobid" >> mailmsg
                    cat mailmsg | mail -s "$subject" $maillist
                else
                    cp -v $COMINfilename $DATAfilename
                    if [ $SENDCOM = YES ]; then
                        cp -v $DATAfilename $COMOUTfilename
                    fi
                fi
            done
        done
    fi 
done

echo ' '
echo "Ending ${COMPONENT} ${RUN} prep"
echo "Ending at : `date`"
echo ' '
