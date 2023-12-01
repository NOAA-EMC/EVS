#! /bin/bash
########################################################################################
# Name of Script: exevs_wafs_atmos_stats.sh
# Purpose of Script: To generate the verification products for WAFS verification
# Arguments: exevs_wafs_atmos_stats.sh
#   
########################################################################################
set -x

cd $DATA
if [ -s wafs_stat.cmdfile ];then
	rm wafs_stat.cmdfile
else
	echo "WARNING: wafs_stat.cmdfile DOES NOT EXIST"
fi

export DATAsemifinal=$DATA/semifinal
mkdir -p $DATAsemifinal

export MPIRUN=${MPIRUN:-"mpiexec"}
ic=0
observations="GCIP GFS"
for observation in $observations ; do
    if [ $observation = "GCIP" ] ; then
	# For ICING, there are 2 different resolutions (before Nov 2023) and 3 centers
	resolutions="0P25"
	centers="blend uk us"
    elif [ $observation = "GFS" ] ; then
	# For wind/temperature, only 1 resolution so far
	resolutions="1P25"
	centers="gfs"
    fi

    for resolution in $resolutions ; do
	for center in $centers; do
	    if [ `echo $MPIRUN | cut -d " " -f1` = 'srun' ] ; then
		echo $ic $USHevs/evs_wafs_atmos_stats.sh $observation $resolution $center  >> wafs_stat.cmdfile
	    else
		echo $USHevs/evs_wafs_atmos_stats.sh $observation $resolution $center  >> wafs_stat.cmdfile
		export MP_PGMMODEL=mpmd
	    fi
	    ic=`expr $ic + 1`
	done
    done
done

export STATSDIR=$DATA/stats
export STATSOUTsmall=$STATSDIR/$RUN.$VDATE
export STATSOUTfinal=$STATSDIR/$MODELNAME.$VDATE
mkdir -p $STATSOUTsmall $STATSOUTfinal


export MPIRUN="$MPIRUN -np $ic -cpu-bind verbose,core cfp"
$MPIRUN wafs_stat.cmdfile

export err=$?; err_chk

# Combine icing files from different centers ( blend, uk, us) to $COMOUTfinal
#===============================
resolutions="0P25"
centers="blend uk us"
cd $DATAsemifinal
for resolution in $resolutions ; do
    for center in $centers ; do
      if [ ! -z  `ls ${center}_$resolution.*` ] ; then
	file=`ls ${center}_$resolution.*`
	finalfile=${file#*\.}
	cat $file >> $finalfile
      fi
    done
    if [[ -s $finalfile ]] ; then
	awk '!seen[$0]++' $finalfile > $STATSOUTfinal/$finalfile
    fi
done

if [ $SENDCOM = YES ] ; then
    [ -z `ls -A $STATSOUTfinal` ] || cpreq $STATSOUTfinal/* $COMOUTfinal/.  
    [ -z `ls -A $STATSOUTsmall` ] || cpreq $STATSOUTsmall/* $COMOUTsmall/.
fi

#########################################
#Cat'ing errfiles to stdout
#########################################

log_dir=$DATA/METplus_output/logs
log_file_count=$(find $log_dir -type f |wc -l)
if [[ $log_file_count -ne 0 ]]; then
	for log_file in $log_dir/*; do
		echo "Start: $log_file"
		cat $log_file
		echo "End: $log_file"
	done
fi

#########################################
