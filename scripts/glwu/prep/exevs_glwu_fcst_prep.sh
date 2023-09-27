#!/bin/bash
###############################################################################
# Name of Script: exevs_glwu_fcst_prep.sh
# Purpose of Script: To pre-process glwu forecast data into the same spatial
#    and temporal scales as validation data.
# Author: Samira Ardani (samira.ardani@noaa.gov)
###############################################################################

set -x

echo "***** START PROCESSING GLWU FORECASTS on `date` *****"

# n024 is nowcast = f000 forecast
mkdir -p $COMOUTprep/glwu.$VDATE/$RUN
mkdir -p $DATA/glwu.$VDATE/$RUN

echo 'Copying GLWU wave grib2 and nc files'

cycles='00 06 12 18'
lead_hours='000 006 012 018 024 030 036 042 048 054 060 066 072 078
            084 090 096 102 108 114 120 126 132 138 144 150 156 162
	    168 174 180 186 192 198 204 210 216 222 228 234 240 246
	    252 258 264 270 276 282 288 294 300 306 312 318 324 330 
	    336 342 348 354 360 366 372 378 384'

mtype='glwu glwu_lc grlc_2p5km grlc_2p5km_lc grlc_2p5km_lc_sr grlc_2p5km_sr grlr_500m grlr_500m_lc'


if [[ ${mtype} == "glwu" || ${mtype} == "glwu_lc" ]];then
  for cyc in ${cycles} ; do
     for hr in ${lead_hours} ; do
	filename="glwu.${mtype}.t${cyc}z.nc"
	newname="glwu.${mtype}.${INITDATE}.t${cyc}z.nc"
	if [ ! -s glwu.${INITDATE}/${filename} ]; then
	   export subject="F${hr} GLWU Forecast Data Missing for EVS ${COMPONENT}"
	   echo "Warning: No GLWU forecast was available for ${INITDATE}${cyc}f${hr}" > mailmsg
	   echo "Missing file is glwu.${INITDATE}/${filename}" >> mailmsg
	   echo "Job ID: $jobid" >> mailmsg
	   cat mailmsg | mail -s "$subject" $maillist
        else
	   if [ ! -s ${ARCglwu}/${newname} ]; then
	      cp -v glwu.${INITDATE}/${filename} $DATA/glwu_nc/${newname}/
	      if [ $SENDCOM = YES ]; then
		 cp -v $DATA/glwu_nc/ ${ARCglwu}/glwu_nc/${newname}/
	      fi
	   fi
	fi
   done
  done
else
  for cyc in ${cycles} ; do
     for hr in ${lead_hours} ; do	   
	filename="glwu.${mtype}.t${cyc}z.grib2"
	if [ ! -s glwu.${INITDATE}/${filename} ]; then
	    export subject="F${hr} GLWU Forecast Data Missing for EVS ${COMPONENT}"
	    echo "Warning: No GLWU forecast was available for ${INITDATE}${cyc}f${hr}" > mailmsg
	    echo "Missing file is glwu.${INITDATE}/${filename}" >> mailmsg
	    echo "Job ID: $jobid" >> mailmsg
	    cat mailmsg | mail -s "$subject" $maillist
        else
	    if [ ! -s ${ARCglwu}/${newname} ]; then
	       cp -v glwu.${INITDATE}/${filename} $DATA/glwu_grib2/${newname}/
	       if [ $SENDCOM = YES ]; then
		  cp -v $DATA/glwu_grib2/ ${ARCglwu}/glwu_grib2/${newname}/
	       fi
	    fi
	fi
   done
  done
fi


# Just keep these following block if you need to use cdo remapbil
#if [ $RUN = 'argo' ] ; then
#  for ftype in t s; do
#    cdo remapbil,$FIXevs/cdo_grids/rtofs_$RUN.grid \
#    $COMOUTprep/rtofs.$VDATE/rtofs_glo_3dz_n024_daily_3z${ftype}io.nc \
#    $DATA/rtofs.$VDATE/$RUN/rtofs_glo_3dz_f000_daily_3z${ftype}io.$RUN.nc
#    if [ $SENDCOM = "YES" ]; then
#     cp $DATA/rtofs.$VDATE/$RUN/rtofs_glo_3dz_f000_daily_3z${ftype}io.$RUN.nc $COMOUTprep/rtofs.$VDATE/$RUN
#    fi
#  done
#fi


# Create the masks
 
$HOMEevs/scripts/$COMPONENT/$STEP/glwu_regions.sh

echo "********** COMPLETED SUCCESSFULLY on `date` **********"
exit

################################ END OF SCRIPT ################################
