#!/bin/bash
###############################################################################
# Name of Script: exevs_nfcens_wave_grid2obs_prep.sh                           
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
#     individual fcst grib2 files                                              
#  Condition codes:                                                            
#     99  - Missing input file                                                 
#  User controllable options: None                                             
###############################################################################

set -x 
# Use LOUD variable to turn on/off trace.  Defaults to YES (on).
export LOUD=${LOUD:-YES}; [[ $LOUD = yes ]] && export LOUD=YES
[[ "$LOUD" != YES ]] && set +x

##############################
## grid2obs NFCENS Model Prep 
##############################

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

###############################################################################
# create today's NFCENS individual fcst grib2 files and add them to the archive
###############################################################################
cycles='00 12'

mkdir -p ${DATA}/gribs
cd ${DATA}/gribs

for cyc in ${cycles} ; do
  # copy the model grib2 files
  filename="HTSGW_mean.t${cyc}z.grib2"
  infile="HTSGW_mean.${INITDATE}.t${cyc}z"
  cp ${COMINmodel}/${MODELNAME}.${INITDATE}/${filename} ${DATA}/gribs/${infile}.grib2
  
  # check to see if you got the file
  set +x
  nc=`ls ${DATA}/gribs/HTSGW_mean.${INITDATE}.t${cyc}z.grib2 | wc -l | awk '{print $1}'`
  echo " Found ${nc} ${infile} "
  [[ "$LOUD" = YES ]] && set -x
  
  if [ "${nc}" = '0' ]
  then
    set +x
    echo ' '
    echo '**************************************** '
    echo '*** FATAL ERROR : NO ${infile} FILE  *** '
    echo '**************************************** '
    echo ' '
    echo "${MODELNAME}_${RUN} $PDYm1 $cycle: HTSGW_mean*grib2 missing."
    [[ "$LOUD" = YES ]] && set -x
    ./postmsg "$jlogfile" "FATAL ERROR : NO HTSGW_mean.*.grib2 OUTPUT FILES"
    err_exit "FATAL ERROR: Could not copy the HTSGW_mean.*.grib2 files"  
  fi
  
  fcst=6
  # create the individual fcst files for every 6hrs
  while (( $fcst <= 240 )); do
    FCST=$(printf "%03d" "$fcst")
    wgrib2 ${infile}.grib2 -match ":${fcst} hour fcst:" -grib ${infile}.f${FCST}.grib2 > /dev/null
    fcst=$(( $fcst+ 6 ))
  done
  # create the f000 from the analysis hour
  wgrib2 ${infile}.grib2 -match ":surface:anl:" -grib ${infile}.f000.grib2 > /dev/null
done

# check to see if the individual fcst files were made
set +x
nc=`ls ${DATA}/gribs/HTSGW_mean.${INITDATE}*.f???.grib2 | wc -l | awk '{print $1}'`
echo " Found ${nc} individual fcst files - should be 82 "
[[ "$LOUD" = YES ]] && set -x

if [ "${nc}" = '0' ]
then
  set +x
  echo ' '
  echo '*********************************************** '
  echo '*** FATAL ERROR : NO ind. fcst grib2 FILES  *** '
  echo '*********************************************** '
  echo ' '
  echo "${MODELNAME}_${RUN} PB2NC $PDYm1 $cycle: HTSGW_mean*f???.grib2 missing."
  [[ "$LOUD" = YES ]] && set -x
  ./postmsg "$jlogfile" "FATAL ERROR : NO HTSGW_mean.*f???.grib2 OUTPUT FILES"
  err_exit "FATAL ERROR: Could not copy the HTSGW_mean.*f???.grib2 files"  
fi

# copy the individual fcst grib2 files to ARCmodel
set +x
echo ' '
echo "Copying ind.fcst grib2 to ${ARCmodel}"
echo '-------------------------------------'
[[ "$LOUD" = YES ]] && set -x

cp ${DATA}/gribs/HTSGW_mean.*.f???.grib2 ${ARCmodel}/.

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

# End of NFCENS grid2obs prep script -------------------------------------- #
