#!/bin/bash
###############################################################################
# Name of Script: exevs_global_ens_wave_grid2obs_prep.sh                       
# Deanna Spindler / Deanna.Spindler@noaa.gov                                  
# Mallory Row / mallory.row@noaa.gov 
# Purpose of Script: Run the grid2obs data prep for any global wave model      
#                    (deterministic and ensemble: GEFS-Wave, GFS-Wave, NWPS)   
#                                                                              
# Usage:                                                                       
#  Parameters: None                                                            
#  Input files:                                                                
#     gdas.${inithour}.prepbufr
#  Output files:                                                               
#     gdas.${validdate}.nc                                                     
#     global.0p25.grib2 files for archive                                      
###############################################################################

set -x

###################################
## grid2obs Global Wave Model Prep 
###################################

cd $DATA
echo "Starting grid2obs_prep for ${MODELNAME}_${RUN}"

echo ' '
echo ' *************************************'
echo " *** ${MODELNAME}-${RUN} grid2obs prep ***"
echo ' *************************************'
echo ' '
echo "Starting at : `date`"
echo '-------------'
echo ' '

###############################################
# add today's GEFS-Wave grib2 files to archive 
###############################################
echo 'Copying GEFS wave grib2 files'

mkdir -p $DATA/gefs_wave_grib2

inithours='00 06 12 18'
lead_hours='000 006 012 018 024 030 036 042 048 054 060 066 072 078
            084 090 096 102 108 114 120 126 132 138 144 150 156 162
            168 174 180 186 192 198 204 210 216 222 228 234 240 246
            252 258 264 270 276 282 288 294 300 306 312 318 324 330 
            336 342 348 354 360 366 372 378 384'

for ihour in ${inithours} ; do
  for hr in ${lead_hours} ; do
    filename="gefs.wave.t${ihour}z.mean.global.0p25.f${hr}.grib2"
    newname="gefs.wave.${INITDATE}.t${ihour}z.mean.global.0p25.f${hr}.grib2"
    if [ ! -s ${COMINgefs}/${MODELNAME}.${INITDATE}/${ihour}/wave/gridded/${filename} ]; then
        echo "WARNING: ${COMINgefs}/${MODELNAME}.${INITDATE}/${ihour}/wave/gridded/${filename} is not available"
	if [ $SENDMAIL = YES ]; then
          export subject="F${hr} GEFS Forecast Data Missing for EVS ${COMPONENT}"
          echo "Warning: No GEFS forecast was available for ${INITDATE}${ihour}f${hr}" > mailmsg
          echo "Missing file is ${COMINgefs}/${MODELNAME}.${INITDATE}/${ihour}/wave/gridded/${filename}" >> mailmsg
          echo "Job ID: $jobid" >> mailmsg
          cat mailmsg | mail -s "$subject" $MAILTO
	fi
    else
        if [ ! -s ${COMOUTgefs}/${newname} ]; then
            cpreq -v ${COMINgefs}/${MODELNAME}.${INITDATE}/${ihour}/wave/gridded/${filename} $DATA/gefs_wave_grib2/${newname}
            if [ $SENDCOM = YES ]; then
                if [ -s $DATA/gefs_wave_grib2/${newname} ]; then 
                    cp -v $DATA/gefs_wave_grib2/${newname} ${COMOUTgefs}/${newname}
                fi
            fi
        fi
    fi
  done
done

############################################
# get the GDAS prepbufr files for yesterday 
############################################
echo 'Copying GDAS prepbufr files'

for ihour in 00 06 12 18 ; do

  export inithour=t${ihour}z
  if [ ! -s ${COMINobsproc}.${INITDATE}/${ihour}/atmos/gdas.${inithour}.prepbufr ]; then
      echo "WARNING: ${COMINobsproc}.${INITDATE}/${ihour}/atmos/gdas.${inithour}.prepbufr is not available"
      if [ $SENDMAIL = YES ]; then
        export subject="GDAS Prepbufr Data Missing for EVS ${COMPONENT}"
        echo "Warning: No GDAS Prepbufr was available for init date ${INITDATE}${ihour}" > mailmsg
        echo "Missing file is ${COMINobsproc}.${INITDATE}/${ihour}/atmos/gdas.${inithour}.prepbufr" >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
  else
      cpreq -v ${COMINobsproc}.${INITDATE}/${ihour}/atmos/gdas.${inithour}.prepbufr ${DATA}/gdas.${INITDATE}${ihour}.prepbufr
      chmod 640 ${DATA}/gdas.${INITDATE}${ihour}.prepbufr
      chgrp rstprod ${DATA}/gdas.${INITDATE}${ihour}.prepbufr
  fi

done

############################################
# run PB2NC                                 
############################################
echo 'Run pb2nc'

mkdir $DATA/ncfiles

for ihour in 00 06 12 18 ; do
    export ihour=$ihour
    export inithour=t${ihour}z
    if [ -s ${DATA}/gdas.${INITDATE}${ihour}.prepbufr ]; then
        if [ ! -s ${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/gdas.${INITDATE}${ihour}.nc ]; then
            run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${STEP}/${COMPONENT}/${RUN}_${VERIF_CASE}/PB2NC_wave.conf
            export err=$?; err_chk
            chmod 640 $DATA/ncfiles/gdas.${INITDATE}${ihour}.nc
            chgrp rstprod $DATA/ncfiles/gdas.${INITDATE}${ihour}.nc
            if [ $SENDCOM = YES ]; then
                if [ -s $DATA/ncfiles/gdas.${INITDATE}${ihour}.nc ]; then
                    cp -v $DATA/ncfiles/gdas.${INITDATE}${ihour}.nc ${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/.
                    chmod 640 ${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/gdas.${INITDATE}${ihour}.nc
                    chgrp rstprod ${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/gdas.${INITDATE}${ihour}.nc
                fi
            fi
        fi
    fi
done

echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs prep *** "
echo ' '

# End of GEFS-Wave grid2obs prep script -------------------------------------- #
