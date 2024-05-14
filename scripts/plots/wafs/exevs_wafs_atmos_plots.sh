#!/bin/bash

set -x

export DATAplot=$DATA/plot
mkdir -p $DATAplot

export MPIRUN=${MPIRUN:-"mpiexec"}

OBSERVATIONS=${OBSERVATIONS:-"GCIP GFS"}

rm -f wafs_plots.cmdfile

ic=0
export VX_MASK_ALL="GLB ASIA AUNZ EAST NAMER NATL_AR2 NHEM NPO SHEM TROPICS"
for observation in $OBSERVATIONS ; do
    if [ $observation = "GCIP" ] ; then
	loopFHOURS="06 09 12 15 18 21 24 27 30 33 36"
	plot_types="roc_curve fbias"
    elif [ $observation = "GFS" ] ; then
	# Need to use more CPUs to break down plotting of each forecast hour
	# It takes too long for each plotting over years (10 minutes/6 years)
	loopFHOURS="06 12 18 24 30 36"
	plot_types="time_series"
    fi
    for ndays in $DAYS_LIST ; do
	if [ $ndays -le 90 ] ; then
	    loopFHOURS="all"
	fi
	for subregion in $VX_MASK_ALL ; do
	    for hh in $loopFHOURS ; do
		for plot_type in $plot_types ; do
		    if [ `echo $MPIRUN | cut -d " " -f1` = 'srun' ] ; then
			echo $ic $USHevs/evs_wafs_atmos_plots.sh $observation $ndays $subregion $hh $plot_type >> wafs_plots.cmdfile
		    else
			echo $USHevs/evs_wafs_atmos_plots.sh $observation $ndays $subregion $hh $plot_type >> wafs_plots.cmdfile
			export MP_PGMMODEL=mpmd
		    fi
		    ic=$(( ic + 1 ))
		done
	    done
	done
    done
done
export MPIRUN="$MPIRUN -np $ic -cpu-bind verbose,core cfp"
$MPIRUN wafs_plots.cmdfile

export err=$?; err_chk

cd $DATAplot
for ndays in $DAYS_LIST ; do
    eval_period="last${ndays}days"
    tarball=$NET.$STEP.${COMPONENT}.${RUN}.${VERIF_CASE}.$eval_period.v${VDATE}.tar
    tar -cvf $tarball *${eval_period}*png

    if [ -s $tarball ]; then
	if [ $SENDCOM = "YES" ]; then
	    cp -v $tarball $COMOUT/.
	fi
	if [ $SENDDBN = YES ] ; then     
	    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/$tarball
	fi
    fi
done


#########################################
#Cat'ing errfiles to stdout
#########################################

log_dir=$DATA/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
	for log_file in $log_dir/*; do                                  
		echo "Start: $log_file"
		cat $log_file                                                                   
		echo "End: $log_file"
	done
fi

echo "********SCRIPT exevs_wafs_atmos_plots.sh COMPLETED NORMALLY on `$NDATE`"
