#!/bin/bash
##############################################################################
# Script Name: evs_wafs_atmos_stats_preparedata.sh
# Purpose:  This script prepares unified templates for UK, GFS and blended forecasts,
#           then runs stat file at the end
# History:  Yali Mao Aug 2022
###############################################################################
set -x

if [[ "$wgrib2_ver" < "3." ]] ; then
    end_wgrib2="fi"
else
    end_wgrib2="endif"
fi

icao2023=yes
runMETplus=yes

#Re-define FHOURS_EVSlist
export FHOURS_EVSlist=""
for ff in $FHOURS ; do
    past=`$NDATE -$ff ${VDATE}${cc}`
    day=${past:0:8}
    ccfcst=${past:8:2}

    if [ $CENTER = "uk" ] ; then
	if [ $RESOLUTION = "0P25" ] ; then
	    sourcefile=$DCOMINuk/$day/wgrbbul/ukmet_wafs/EGRR_WAFS_0p25_icing_unblended_${day}_${ccfcst}z_t${ff}.grib2
	fi
    elif [ $CENTER = "us" ] ; then
	if [ $RESOLUTION = "0P25" ] ; then
	    sourcefile=$COMINgfs/gfs.$day/$ccfcst/atmos/gfs.t${ccfcst}z.wafs_0p25_unblended.f${ff}.grib2
	fi
    elif [ $CENTER = "blend" ] ; then
        if [ $RESOLUTION = "0P25" ] ; then
	    sourcefile=$COMINgfs/gfs.$day/$ccfcst/atmos/WAFS_0p25_blended_${day}${ccfcst}f${ff}.grib2
	fi
    elif [ $CENTER = "gfs" ] ; then
	if [ $RESOLUTION = "1P25" ] ; then
	    sourcefile=$COMINgfs/gfs.$day/$ccfcst/atmos/gfs.t${ccfcst}z.wafs_grb45f${ff}.grib2
	fi
    fi

    targetfile=$GRID_STAT_INPUT_BASE/$CENTER.${day}${ccfcst}.f${ff}.grib2

    if [[ $RESOLUTION = "1P25" ]] && [[ $OBSERVATION = "GFS" ]] ; then
	if [[ -f $sourcefile ]] ; then
	    FHOURS_EVSlist="$FHOURS_EVSlist,$ff"

	    targetfile=$GRID_STAT_INPUT_BASE/$CENTER.${day}${ccfcst}.f${ff}.grib2
	    # Convert tempalte 4.15 to 4.0		   
            # $WGRIB2 $sourcefile -set_pdt +0 -grib $GRID_STAT_INPUT_BASE/$CENTER.${day}${ccfcst}.f${ff}.grib2
	    # For WAFS after implementation 2023-2024
	    $WGRIB2 $sourcefile -match ":(843.1|696.8|595.2|506|392.7|300.9|250|196.8|147.5|100.4) mb" \
		    -match ":(UGRD|VGRD|TMP):"\
		    -if ":843.1 mb" -set_lev "850 mb" -$end_wgrib2 \
		    -if ":696.8 mb" -set_lev "700 mb" -$end_wgrib2 \
		    -if ":595.2 mb" -set_lev "600 mb" -$end_wgrib2 \
		    -if ":506 mb" -set_lev "500 mb" -$end_wgrib2 \
		    -if ":392.7 mb" -set_lev "400 mb" -$end_wgrib2 \
		    -if ":300.9 mb" -set_lev "300 mb" -$end_wgrib2 \
		    -if ":196.8 mb" -set_lev "200 mb" -$end_wgrib2 \
		    -if ":147.5 mb" -set_lev "150 mb" -$end_wgrib2 \
		    -if ":100.4 mb" -set_lev "100 mb" -$end_wgrib2 \
		    -grib $targetfile
	    # For WAFS before implementation 2023-2024
	    nrecords=`$WGRIB2 $targetfile | wc -l`
	    if [[ $nrecords -le 10 ]] ; then
		icao2023=no
		$WGRIB2 $sourcefile -match ":(850|700|600|500|400|300|250|200|150|100) mb" \
			-match ":(UGRD|VGRD|TMP):"\
			-grib $targetfile
	    fi
        fi
    else
	if [[ -f $sourcefile ]] ; then
            FHOURS_EVSlist="$FHOURS_EVSlist,$ff"
	    ln -sf $sourcefile $targetfile
	fi
    fi
done

export FHOURS_EVSlist=`echo $FHOURS_EVSlist | sed 's/^,//'`
if [ -z $FHOURS_EVSlist ] ; then
    if [[ $SENDMAIL = YES ]] ; then
        export subject="All forecast files are missing for EVS ${COMPONENT}"
        echo "Warning: All $CENTER forecasts are missing for $OBSERVATION valid date ${VDATE}${cc}. METplus will not run." > mailmsg.$OBSERVATION.$CENTER.$RESOLUTION
        echo "Job ID: $jobid" >> mailmsg.$OBSERVATION.$CENTER.$RESOLUTION
	cat mailmsg.$OBSERVATION.$CENTER.$RESOLUTION | mail -s "$subject" $MAILTO
    fi
    runMETplus=no
fi

# GCIP data
if [[ $OBSERVATION = "GCIP" ]] ; then
    ccdir=$(( 10#$cc / 6 * 6 ))
    ccdir="$(printf "%02d" $(( 10#$ccdir )) )"
    sourcedir=$COMINgfs/gfs.$VDATE/$ccdir/atmos
    sourcefile=$sourcedir/gfs.t${cc}z.gcip.f00.grib2

    targetdir=$GRID_STAT_INPUT_BASE
    targetfile=$GRID_STAT_INPUT_BASE/gfs.t${cc}z.gcip.f00.grib2

    if [[ ! -f $targetfile ]] ; then
	if [[ -f $sourcefile ]] ; then
	    # For WAFS after implementation 2023-2024
	    $WGRIB2 $sourcefile -match ":(812|696.8|595.2|506|392.7) mb" \
		    -match "(parm=37:|ICESEV)" \
		    -if ":812 mb" -set_lev "800 mb" -$end_wgrib2 \
		    -if ":696.8 mb" -set_lev "700 mb" -$end_wgrib2 \
		    -if ":595.2 mb" -set_lev "600 mb" -$end_wgrib2 \
		    -if ":506 mb" -set_lev "500 mb" -$end_wgrib2 \
		    -if ":392.7 mb" -set_lev "400 mb" -$end_wgrib2 \
		    -grib $targetfile
	    # For WAFS before implementation 2023-2024
	    nrecords=`$WGRIB2 $targetfile | wc -l`
	    if [[ $nrecords -le 4 ]] ; then
		$WGRIB2 $sourcefile -match ":(800|700|600|500|400) mb" \
			-match "(parm=37:|ICESEV)" \
			-grib $targetfile
	    fi
	else
	    if [ $SENDMAIL = YES ] ; then
		export subject="$OBSERVATION Analysis Data Missing for EVS ${COMPONENT}"
		echo "Warning: $OBSERVATION analysis is missing for $CENTER valid date ${VDATE}${cc}" > mailmsg.$OBSERVATION.$CENTER.$RESOLUTION
		echo "Missing file is $sourcefile" >> mailmsg.$OBSERVATION.$CENTER.$RESOLUTION
		echo "Job ID: $jobid" >> mailmsg.$OBSERVATION.$CENTER.$RESOLUTION
		cat mailmsg.$OBSERVATION.$CENTER.$RESOLUTION | mail -s "$subject" $MAILTO
	    fi
	    runMETplus=no
	fi
    fi

elif [[ $OBSERVATION = "GFS" ]] ; then
    sourcedir=$COMINgfs/gfs.$VDATE/$cc/atmos
    if [[ $icao2023 = yes ]] ; then
	sourcefile=$sourcedir/gfs.t${cc}z.wafs.0p25.anl
    else
	sourcefile=$sourcedir/gfs.t${cc}z.pgrb2.0p25.anl
    fi

    targetfile=$GRID_STAT_INPUT_BASE/gfs.t${cc}z.wafs.0p25.anl

    if [[ ! -f $targetfile ]] ; then
	if [[ -f $sourcefile ]] ; then
	    if [[ $icao2023 = yes ]] ; then
		# For WAFS after implementation 2023-2024
		$WGRIB2 $sourcefile -match ":(843.1|696.8|595.2|506|392.7|300.9|250|196.8|147.5|100.4) mb" \
		    -match ":(UGRD|VGRD|TMP):"\
		    -if ":843.1 mb" -set_lev "850 mb" -$end_wgrib2 \
		    -if ":696.8 mb" -set_lev "700 mb" -$end_wgrib2 \
		    -if ":595.2 mb" -set_lev "600 mb" -$end_wgrib2 \
		    -if ":506 mb" -set_lev "500 mb" -$end_wgrib2 \
		    -if ":392.7 mb" -set_lev "400 mb" -$end_wgrib2 \
		    -if ":300.9 mb" -set_lev "300 mb" -$end_wgrib2 \
		    -if ":196.8 mb" -set_lev "200 mb" -$end_wgrib2 \
		    -if ":147.5 mb" -set_lev "150 mb" -$end_wgrib2 \
		    -if ":100.4 mb" -set_lev "100 mb" -$end_wgrib2 \
		    -grib $targetfile
	    else
		# For WAFS before implementation 2023-2024
		$WGRIB2 $sourcefile -match ":(850|700|600|500|400|300|250|200|150|100) mb" \
			-match ":(UGRD|VGRD|TMP):"\
			-grib $targetfile
	    fi
	else
	    if [ $SENDMAIL = YES ] ; then
		export subject="$OBSERVATION Analysis Data Missing for EVS ${COMPONENT}"
		echo "Warning: $OBSERVATION analysis is missing for valid date ${VDATE}${cc}" > mailmsg.$OBSERVATION.$CENTER.$RESOLUTION
		echo "Missing file is $sourcefile" >> mailmsg.$OBSERVATION.$CENTER.$RESOLUTION
		echo "Job ID: $jobid" >> mailmsg.$OBSERVATION.$CENTER.$RESOLUTION
		cat mailmsg.$OBSERVATION.$CENTER.$RESOLUTION | mail -s "$subject" $MAILTO
	    fi
	    runMETplus=no
	fi
    fi
fi

export valid_beg=$cc
export valid_end=$cc
if [ $runMETplus = yes ] ; then
    ${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $DATAmpmd/GridStat_fcstWAFS_obs${OBSERVATION}_${RESOLUTION}.conf
    ${METPLUS_PATH}/ush/run_metplus.py -c $MACHINE_CONF -c $PARMevs/StatAnalysis_fcstWAFS_obs${OBSERVATION}_GatherbyDay.conf
fi
