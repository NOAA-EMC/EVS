#!/bin/bash
##############################################################################
# Script Name: evs_wafs_atmos_stats_preparedata.sh
# Purpose:  This script prepares unified templates for UK, GFS and blended forecasts
# History:  Yali Mao Aug 2022
###############################################################################
set -x

inithours="00 06 12 18"

# Since WAFS verification is up to 36/48 hours, link only 2 days in the past
for past_day in 0 1 2 ; do
   hour=$((past_day*24))
   past=`$NDATE -$hour ${VDATE}00`
   day=${past:0:8}
   # cc=${past:8:2}
   for cc in $inithours ; do
       for ff in $FHOURS ; do
	   if [ $CENTER = "uk" ] ; then
	       if [ $RESOLUTION = "0P25" ] ; then
		   sourcefile=$COMINuk/$day/wgrbbul/ukmet_wafs/EGRR_WAFS_0p25_icing_unblended_${day}_${cc}z_t${ff}.grib2
	       fi
	   elif [ $CENTER = "us" ] ; then
	       if [ $RESOLUTION = "0P25" ] ; then
		   sourcefile=$COMINgfs/gfs.$day/$cc/atmos/gfs.t${cc}z.wafs_0p25_unblended.f${ff}.grib2
	       fi
	   elif [ $CENTER = "blend" ] ; then
               if [ $RESOLUTION = "0P25" ] ; then
		   sourcefile=$COMINgfs/gfs.$day/$cc/atmos/WAFS_0p25_blended_${day}${cc}f${ff}.grib2
	       fi
	   elif [ $CENTER = "gfs" ] ; then
	       if [ $RESOLUTION = "1P25" ] ; then
		   sourcefile=$COMINgfs/gfs.$day/$cc/atmos/gfs.t${cc}z.wafs_grb45f${ff}.grib2
	       fi
	   fi

	   if [[ $RESOLUTION = "1P25" ]] && [[ $OBSERVATION = "GFS" ]] ; then
	       if [[ -f $sourcefile ]] ; then
		   # Convert tempalte 4.15 to 4.0
                   $WGRIB2 $sourcefile -set_pdt +0 -grib $GRID_STAT_INPUT_BASE/$CENTER.${day}${cc}.f${ff}.grib2
               fi
	   else
	       if [[ -f $sourcefile ]] ; then
		   ln -sf $sourcefile $GRID_STAT_INPUT_BASE/$CENTER.${day}${cc}.f${ff}.grib2
	       fi
	   fi
       done
   done
done

# GCIP data
if [[ $OBSERVATION = "GCIP" ]] ; then
    for cc in $inithours ; do
	sourcedir=$COMINgfs/gfs.$VDATE/$cc/atmos

	targetdir=$GRID_STAT_INPUT_BASE/gfs.$VDATE/$cc/atmos
	sourcefile=$sourcedir/gfs.t${cc}z.gcip.f00.grib2
	if [[ -f $sourcefile ]] ; then
	    mkdir -p $targetdir
	    ln -sf $sourcefile $targetdir/.
	else
	    if [ $SENDMAIL = YES ] ; then
		export subject="GCIP Analysis Data Missing for EVS ${COMPONENT}"
		echo "Warning: No GCIP analysis was available for valid date ${VDATE}${cc}" > mailmsg
		echo “Missing file is $sourcefile” >> mailmsg
		echo "Job ID: $jobid" >> mailmsg
		cat mailmsg | mail -s "$subject" $maillist
	    fi
	fi
	
	cc2=$(( 10#$cc + 3 ))
	cc2="$(printf "%02d" $(( 10#$cc2 )) )"
	targetdir=$GRID_STAT_INPUT_BASE/gfs.$VDATE/$cc2/atmos
	sourcefile=$sourcedir/gfs.t${cc2}z.gcip.f00.grib2
	if [[ -f $sourcefile ]] ; then
            mkdir -p $targetdir
            ln -sf $sourcefile $targetdir/.
	else
	    if [ $SENDMAIL = YES ] ; then
		export subject="GCIP Analysis Data Missing for EVS ${COMPONENT}"
		echo "Warning: No GCIP analysis was available for valid date ${VDATE}${cc2}" > mailmsg
		echo “Missing file is $sourcefile” >> mailmsg
		echo "Job ID: $jobid" >> mailmsg
		cat mailmsg | mail -s "$subject" $maillist
	    fi
        fi
    done
elif [[ $OBSERVATION = "GFS" ]] ; then
    for cc in $inithours ; do
        sourcedir=$COMINgfs/gfs.$VDATE/$cc/atmos
	sourcefile=$sourcedir/gfs.t${cc}z.pgrb2.0p25.anl
	if [[ ! -f $sourcefile ]] ; then
	    if [ $SENDMAIL = YES ] ; then
		export subject="GFS Analysis Data Missing for EVS ${COMPONENT}"
		echo "Warning: No GFS analysis was available for valid date ${VDATE}${cc}" > mailmsg
		echo “Missing file is $sourcefile” >> mailmsg
		echo "Job ID: $jobid" >> mailmsg
		cat mailmsg | mail -s "$subject" $maillist
	    fi
	fi
    done    
fi

exit

