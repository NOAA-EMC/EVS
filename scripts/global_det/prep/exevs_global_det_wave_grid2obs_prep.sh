#!/bin/bash
###############################################################################
# Name of Script: exevs_global_det_wave_grid2obs_prep.sh                       
# Deanna Spindler / Deanna.Spindler@noaa.gov                                   
# Purpose of Script: Run the grid2obs data prep for any global wave model      
#                    (deterministic and ensemble: GEFS-Wave, GFS-Wave, NWPS)   
#                                                                              
# Usage:                                                                       
#  Parameters: None                                                            
#  Input files:                                                                
#     gdas.${cycle}.prepbufr                                                   
#  Output files:                                                               
#     gdas.${validdate}.nc                                                     
#     global.0p25.grib2 files for archive                                      
###############################################################################

set -x 
# Use LOUD variable to turn on/off trace.  Defaults to YES (on).
export LOUD=${LOUD:-YES}; [[ $LOUD = yes ]] && export LOUD=YES
[[ "$LOUD" != YES ]] && set +x

###################################
## grid2obs Global Wave Model Prep 
###################################

cd $DATA
echo "in $0 JLOGFILE is $jlogfile"
echo "Starting grid2obs_prep for ${MODELNAME}_${RUN}"

set +x
echo ' '
echo ' *************************************'
echo " *** ${MODELNAME}-${RUN} grid2obs prep ***"
echo ' *************************************'
echo ' '
echo "Starting at : `date`"
echo '-------------'
echo ' '
[[ "$LOUD" = YES ]] && set -x

###############################################
# add today's GFS-Wave grib2 files to archive  
###############################################
cycles='00 06 12 18'
lead_hours='000 006 012 018 024 030 036 042 048 054 060 066 072 078
            084 090 096 102 108 114 120 126 132 138 144 150 156 162
            168 174 180 186 192 198 204 210 216 222 228 234 240 246
            252 258 264 270 276 282 288 294 300 306 312 318 324 330 
            336 342 348 354 360 366 372 378 384'

for cyc in ${cycles} ; do
  for hr in ${lead_hours} ; do
    filename="gfswave.t${cyc}z.global.0p25.f${hr}.grib2"
    newname="gfswave.${INITDATE}.t${cyc}z.global.0p25.f${hr}.grib2"
    cp ${COMINmodel}/${MODELNAME}.${INITDATE}/${cyc}/wave/gridded/${filename} ${ARCgfs}/${newname}
  done
done

############################################
# get the GDAS prepbufr files for yesterday 
############################################
set +x
echo ' '
echo 'Copying GDAS prepbufr files :'
echo '-----------------------------'
[[ "$LOUD" = YES ]] && set -x

for cyc in 00 06 12 18 ; do

  export cycle=t${cyc}z
  echo "cp ${COMINgdas}.${INITDATE}/${cyc}/atmos/gdas.${cycle}.prepbufr ${DATA}/."
  cpreq ${COMINgdas}.${INITDATE}/${cyc}/atmos/gdas.${cycle}.prepbufr ${DATA}/.

  ############################################
  # regular error check                       
  ############################################
  if [ -f "${DATA}/gdas.${cycle}.prepbufr" ]
  then 
    set +x
    echo "Successfully copied the GDAS prepbufr file for ${cycle}"
    [[ "$LOUD" = YES ]] && set -x
  else
    set +x
    echo ' '
    echo '************************************* '
    echo '*** ERROR : NO GDAS PREPBUFR FILE *** '
    echo '************************************* '
    echo ' '
    echo "${MODELNAME}_${RUN} ${INITDATE} ${cycle} : GDAS file missing."
    [[ "$LOUD" = YES ]] && set -x
    ./postmsg "$jlogfile" "FATAL ERROR : NO GDAS PREPBUFR FILE"
    err_exit "FATAL ERROR: Did not copy the GDAS prepbufr file"
  fi

done

############################################
# run PB2NC                                 
############################################
/usr/bin/env
run_metplus.py ${PARMevs}/metplus_config/machine.conf ${PARMevs}/metplus_config/${COMPONENT}/${RUN}_${VERIF_CASE}/${STEP}/PB2NC_wave.conf
export err=$?; err_chk

cat $pgmout

##############################################
# check to see if the nc files have been made 
##############################################
set +x
nc=`ls ${DATA}/ncfiles/gdas.*.nc | wc -l | awk '{print $1}'`
echo " Found ${nc} ${DATA}/ncfiles/gdas.nc files for ${INITDATE} "
[[ "$LOUD" = YES ]] && set -x

if [ "${nc}" = '0' ]
then
  set +x
  echo ' '
  echo '**************************************** '
  echo '*** FATAL ERROR : NO GDAS.*.nc FILES *** '
  echo '**************************************** '
  echo ' '
  echo "${MODELNAME}_${RUN} PB2NC $PDYm1 $cycle: gdas.*.nc missing."
  [[ "$LOUD" = YES ]] && set -x
  ./postmsg "$jlogfile" "FATAL ERROR : NO gdas.*.nc OUTPUT FILES"
  err_exit "FATAL ERROR: PB2NC did not make the gdas.${PDYm1}.nc files"  
fi

###################################
# move the nc files to prep COMOUT 
###################################
set +x
echo ' '
echo "Copying GDAS ncfiles to ${COMOUT}"
echo '----------------------------------'
[[ "$LOUD" = YES ]] && set -x

cpreq ${DATA}/ncfiles/gdas*nc ${COMOUT}.${INITDATE}/${MODELNAME}/${VERIF_CASE}/.

msg="JOB $job HAS COMPLETED NORMALLY."
postmsg "$jlogfile" "$msg"

# --------------------------------------------------------------------------- #
# Ending output                                                                

set +x
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs prep *** "
echo ' '
[[ "$LOUD" = YES ]] && set -x

# End of GFS-Wave grid2obs prep script -------------------------------------- #
