#!/bin/sh
##############################################################################
# Script Name: evs_global_det_aviation_stats.sh
# Purpose:  This script prepares unified templates for UK, GFS and blended forecasts
# History:  Yali Mao Aug 2022
###############################################################################
set -x

# Since WAFS verification is up to 36/48 hours, link only 2 days in the past
for past_day in 0 1 2 ; do
   hour=$((past_day*24))
   past=`$NDATE -$hour ${VDATE}00`
   day=${past:0:8}
   # cc=${past:8:2}
   cc=$valid_beg
   while [ $cc -le $valid_end ] ; do
       for ff in $FHOURS ; do
	   if [ $CENTER = "uk" ] ; then
	       if [ $RESOLUTION = "0P25" ] ; then
		   sourcefile=$COMINuk/$day/wgrbbul/ukmet_wafs/EGRR_WAFS_0p25_icing_unblended_${day}_${cc}z_t${ff}.grib2
	       elif [ $RESOLUTION = "1P25" ] ; then
		   sourcefile=$COMINuk/$day/wgrbbul/ukmet_wafs/EGRR_WAFS_unblended_${day}_${cc}z_t${ff}.grib2
	       fi
	   elif [ $CENTER = "us" ] ; then
	       if [ $RESOLUTION = "0P25" ] ; then
		   sourcefile=$COMINgfs/gfs.$day/$cc/atmos/gfs.t${cc}z.wafs_0p25_unblended.f${ff}.grib2
	       elif [ $RESOLUTION = "1P25" ] ; then
		   sourcefile=$COMINgfs/gfs.$day/$cc/atmos/gfs.t${cc}z.wafs_grb45f${ff}.grib2
	       fi
	   elif [ $CENTER = "blend" ] ; then
               if [ $RESOLUTION = "0P25" ] ; then
		   sourcefile=$COMINgfs/gfs.$day/$cc/atmos/WAFS_0p25_blended_${day}${cc}f${ff}.grib2
	       elif [ $RESOLUTION = "1P25" ] ; then
		   sourcefile=$COMINgfs/gfs.$day/$cc/atmos/WAFS_blended_${day}${cc}f${ff}.grib2
	       fi
	   fi

	   if [ $RESOLUTION = "0P25" ] ; then
	       if [[ -f $sourcefile ]] ; then
		   ln -sf $sourcefile $INPUT_BASE/$CENTER.${day}${cc}.f${ff}.grib2
	       fi
	   elif [ $RESOLUTION = "1P25" ] ; then
	       if [[ -f $sourcefile ]] ; then
		   $WGRIB2 $sourcefile | grep ICIP | grep ave | $WGRIB2 -i $sourcefile -grib ave.$CENTER.${day}${cc}.f${ff}.grib2
		   $WGRIB2 $sourcefile | grep ICIP | grep max | $WGRIB2 -i $sourcefile -grib max.$CENTER.${day}${cc}.f${ff}.grib2.tmp
		   $WGRIB2 max.$CENTER.${day}${cc}.f${ff}.grib2.tmp -if "var0_[0-9]+_[0-9]+_[0-9]+_19_20" -set_var ALBDO -grib max.$CENTER.${day}${cc}.f${ff}.grib2
		   cat ave.$CENTER.${day}${cc}.f${ff}.grib2 max.$CENTER.${day}${cc}.f${ff}.grib2 > combo.$CENTER.${day}${cc}.f${ff}.grib2
		   $WGRIB2 combo.$CENTER.${day}${cc}.f${ff}.grib2 -set_pdt +0 -grib $INPUT_BASE/$CENTER.${day}${cc}.f${ff}.grib2
		   rm *.$CENTER.${day}${cc}.f${ff}.grib2* combo.$CENTER.${day}${cc}.f${ff}.grib2
	       fi
	   fi
       done
       cc=$(( cc + $valid_inc ))
       cc="$(printf "%02d" $(( 10#$cc )) )"
   done
done

exit

