
#!/bin/bash
#########################################################################################################################
# Name of Script: evs_wave_timeseries.sh
# Developed for EVS-GLWU: Samira Ardani (samira.ardani@noaa.gov)                   
# Cited to: Mallory Rows's work for global_det component.     
# Purpose of Script: Copy individual plot from tmp directory in $DATA to job working directory to address mpmd (03/2025)   

#######################################
# Copy the plots to a common directory
#######################################


# set up plot variables
set -x

small_periods='last31days last90days'

inithours='01 07 13 19'
wave_vars='HTSGW WIND'
fhrs='000 024 048 072 096 120 144'
stats_list='stats1 stats2 stats3 stats4 stats5'
region='greatlakes'
export region=${region}
export obstype="ndbc_standard"
ptype='timeseries fhrmean'

for small_period in ${small_periods} ; do
	for vhr in ${inithours} ; do
		for wvar in ${wave_vars} ; do
			w_var=$(echo ${wvar} | tr '[A-Z]' '[a-z]')
			for stats in ${stats_list}; do
				case ${stats} in
					'stats1')
					image_stat="me_rmse"
					;;
					'stats2')
					image_stat="corr"
			       		;;
					'stats3')
					image_stat="fbar_obar"
					;;
					'stats4')
					image_stat="esd"
		                	;;
					'stats5')
					image_stat="si"
		                	;;
		                	'stats6')
					image_stat="p95"
					;;
				esac
				case ${wvar} in
					'WIND')
					image_level="z10"
					;;
					*)
					image_level="l0"
					;;
				esac

				# Lead average plots
				imagename=evs.${COMPONENT}.${image_stat}.${w_var}_${image_level}_${obstype}.${small_period}.fhrmean_valid${vhr}z_f144.${region}.png
            			tmp_image=$DATA/images/$imagename
				job_work_dir=${DATA}/job_work_dir/plot_${wvar}_${vhr}_${stats}_lead_average_$(echo ${small_period} | tr '[a-z]' '[A-Z]')
				job_image=$job_work_dir/images/$imagename
				if [[ ! -s $tmp_image ]]; then
					if [[ -s $job_image ]]; then
						cp -v $job_image $tmp_image
					else
						echo "NOTE: $job_image does not exist"
					fi
				fi
				# Time series plots
				for fhr in ${fhrs} ; do
					imagename=evs.${COMPONENT}.${image_stat}.${w_var}_${image_level}_${obstype}.${small_period}.timeseries_valid${vhr}z_f${fhr}.${region}.png
            				tmp_image=$DATA/images/$imagename
					job_work_dir=${DATA}/job_work_dir/plot_${wvar}_${vhr}_${fhr}_${stats}_time_series_$(echo ${small_period} | tr '[a-z]' '[A-Z]')
					job_image=$job_work_dir/images/$imagename
					if [[ ! -s $tmp_image ]]; then
						if [[ -s $job_image ]]; then
							cp -v $job_image $tmp_image
						else
							echo "NOTE: $job_image does not exist"
						fi
					fi
				done
			done
		done
	done
done

