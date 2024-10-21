#!/bin/bash
##################################################################################
# Name of Script: exevs_glwu_wave_grid2obs_plots.sh                           
# Samira Ardani / samira.ardani@noaa.gov                                    
# Purpose of Script: Run the grid2obs plots for GLWU wave model           
#                      
#                                                                               
# Usage:                                                                        
#  Parameters: None                                                             
#  Input files:                                                                 
#     evs.stats.glwu.wave.grid2obs.vYYYYMMDD.stat                             
#  Output files:                                                                
#     evs.plots.glwu.wave.grid2obs.last31days.vYYYYMMDD.tar                   
#     evs.plots.glwu.wave.grid2obs.last90days.vYYYYMMDD.tar                   
#                                                
#################################################################################

set -x

# set major & minor MET version
export MET_VERSION_major_minor=`echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g"`

# Use LOUD variable to turn on/off trace.  Defaults to YES (on).
export LOUD=${LOUD:-YES}; [[ $LOUD = yes ]] && export LOUD=YES
[[ "$LOUD" != YES ]] && set -x

#############################
# grid2obs wave model plots 
#############################

cd $DATA
echo "Starting grid2obs_plots for ${MODELNAME}_${RUN}"

set -x
echo ' '
echo ' ******************************************'
echo " *** ${MODELNAME}-${RUN} grid2obs plots ***"
echo ' ******************************************'
echo ' '
echo "Starting at : `date`"
echo '-------------'
echo ' '
[[ "$LOUD" = YES ]] && set -x

#############################
# get the model .stat files 
#############################
set -x
echo ' '
echo 'Copying *.stat files :'
echo '-----------------------------'
[[ "$LOUD" = YES ]] && set -x

mkdir -p ${DATA}/stats
mkdir -p ${DATA}/wave

plot_start_date=${PDYm90}
plot_end_date=${VDATE}

theDate=${plot_start_date}
while (( ${theDate} <= ${plot_end_date} )); do
  EVSINglwu=${COMIN}/stats/${COMPONENT}/${MODELNAME}.${theDate}
    if [ -s ${EVSINglwu}/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${theDate}.stat ]; then
	    cp ${EVSINglwu}/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${theDate}.stat ${DATA}/stats/.
    else
	    echo "WARNING: ${EVSINglwu}/evs.stats.${MODELNAME}.${RUN}.${VERIF_CASE}.v${theDate}.stat DOES NOT EXIST"
    fi
    theDate=$(date --date="${theDate} + 1 day" '+%Y%m%d')
done

####################
# quick error check 
####################

nc=`ls ${DATA}/stats/evs*stat | wc -l | awk '{print $1}'`
echo " Found ${nc} ${DATA}/stats/evs*stat file for ${VDATE} "
if [ "${nc}" != '0' ]
then
	set -x
	echo "Successfully copied the GLWU *.stat file for ${VDATE}"
	[[ "$LOUD" = YES ]] && set -x
else
	set -x
	echo ' '
	echo '**************************************** '
	echo '*** FATAL ERROR: NO GLWU *.stat FILES *** '
	echo "             for ${VDATE} "
	echo '**************************************** '
	echo ' '
	echo "${MODELNAME}_${RUN} $VDATE $vhour : GLWU *.stat files missing."
	[[ "$LOUD" = YES ]] && set -x
	"FATAL ERROR: NO GLWU *.stat files for ${VDATE}"
	err_exit "FATAL ERROR: Did not copy the GLWU *.stat files for ${VDATE}"
	exit
fi

#################################
## Make the command files for cfp 
#################################
# time_series
${USHevs}/${COMPONENT}/evs_wave_timeseries.sh
export err=$?; err_chk

# lead_averages
${USHevs}/${COMPONENT}/evs_wave_leadaverages.sh
export err=$?; err_chk

chmod 775 plot_all_${MODELNAME}_${RUN}_g2o_plots.sh

###########################################
# Run the command files for the LAST31DAYS 
###########################################

if [ ${run_mpi} = 'yes' ] ; then
	mpiexec -np 36 --cpu-bind verbose,core --depth=3 cfp plot_all_${MODELNAME}_${RUN}_g2o_plots.sh
else
	echo "not running mpiexec"
	sh plot_all_${MODELNAME}_${RUN}_g2o_plots.sh
fi

#####################
# Gather all the files 
#######################

periods='LAST31DAYS LAST90DAYS'
if [ $gather = yes ] ; then
	echo "copying all images into one directory"
	cp ${DATA}/wave/*png ${DATA}/ndbc_standard/  ## lead_average plots 
	nc=$(ls ${DATA}/ndbc_standard/*.fhrmean_valid*.png | wc -l | awk '{print $1}')
	echo "copied $nc lead_average plots"
	for period in ${periods} ; do
		period_lower=$(echo ${period,,})
		if [ ${period} = 'LAST31DAYS' ] ; then
			period_out='last31days'
		elif [ ${period} = 'LAST90DAYS' ] ; then
			period_out='last90days'
		fi

		# check to see if the plots are there
    	    	nc=$(ls ${DATA}/ndbc_standard/*${period_lower}*.png | wc -l | awk '{print $1}')
		echo " Found ${nc} ${DATA}/plots/*${period_lower}*.png files for ${VDATE} "
		if [ "${nc}" != '0' ]
		then
			set -x
			echo "Found ${nc} ${period_lower} plots for ${VDATE}"
			[[ "$LOUD" = YES ]] && set -x
		else
			set -x
			echo ' '
			echo '**************************************** '
			echo "*** FATAL ERROR: NO ${period} PLOTS  *** "
			echo "    found for ${VDATE} "
			echo '**************************************** '
			echo ' '
			echo "${MODELNAME}_${RUN} ${VDATE} ${period}: PLOTS are missing."
			[[ "$LOUD" = YES ]] && set -x
		
			"FATAL ERROR : NO ${period} PLOTS FOR ${VDATE}"
			err_exit "FATAL ERROR: Did not find any ${period} plots for ${VDATE}"
		fi    	    	                                                                                                                                                                                                    		
		# tar and copy them to the final destination

		if [ "${nc}" > '0' ] ; then
			cd ${DATA}/ndbc_standard
			tar -cvf evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${period_out}.v${VDATE}.tar evs.*${period_lower}*.png
		fi

		if [ $SENDCOM = YES ]; then
			if [ -s evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${period_out}.v${VDATE}.tar ]; then
	   			cp -v evs.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${period_out}.v${VDATE}.tar ${COMOUTplots}
			fi
		fi
		if [ $SENDDBN = YES ]; then
			$DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job ${COMOUTplots}/${NET}.${STEP}.${COMPONENT}.${RUN}.${VERIF_CASE}.${period_out}.v${VDATE}.tar
		fi
	done

else  
	echo "not copying the plots"
fi

msg="JOB $job HAS COMPLETED NORMALLY."

#########################################
# copy log files into logs and cat them
#########################################

cd ${DATA}
mkdir -p ${DATA}/logs
log_dir=$DATA/logs

extns='out log'
for extn in ${extns} ; do
	count=$(find ${DATA} -type f -name "*.${extn}"|wc -l)
	if [ $count != 0 ] ; then
		cp ${DATA}/*.${extn} ${log_dir}
	fi
done

log_file_count=$(find ${DATA} -type f -name "*.out" -o -name ".log" |wc -l)
if [[ $log_file_count -ne 0 ]]; then
	for log_file in $log_dir/*; do
		echo "Start: $log_file"
		cat $log_file

		echo "End: $log_file"
	done
fi


# --------------------------------------------------------------------------- #
# Ending output 
#
set -x
echo ' '
echo "Ending at : `date`"
echo ' '
echo " *** End of ${MODELNAME}-${RUN} grid2obs stat *** "
echo ' '
[[ "$LOUD" = YES ]] && set -x


# End of GLWU grid2obs plots script ------------------------------------- #
