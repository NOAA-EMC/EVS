
#!/bin/bash
#########################################################################################################################
# Name of Script: global_ens_wave_plots_copy_plots.sh
# Developed for EVS-global_ens: Samira Ardani (samira.ardani@noaa.gov)                   
# Cited to: Mallory Row's work for global_det component.     
# Purpose of Script: Copy individual plot from tmp directory in $DATA to job working directory to address mpmd (05/2025)   

#######################################
# Copy the plots to a common directory
#######################################


# set up plot variables
set -x

small_periods='last31days last90days'

inithours='00 12'
wave_vars='WIND HTSGW PERPW'
fhrs='000 024 048 072 096 120 144 168 192 216 240 264 288 312 336 360 384'
stats_list='stats1 stats2 stats3 stats4 stats5'
region='glb'
export region=${region}
export obtype="sfcshp"
export obtype2="wave"
ptype='timeseries lead_average'

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
				imagename=evs.${COMPONENT}.${image_stat}.${w_var}_${image_level}_${obtype}.${small_period}.fhrmean_valid${vhr}z_f384.latlon_0p25_${region}.png
            			tmp_image=$DATA/$obtype/$imagename
				job_work_dir=${DATA}/job_work_dir/plot_${wvar}_${vhr}_${stats}_lead_average_$(echo ${small_period} | tr '[a-z]' '[A-Z]')
				job_image=$job_work_dir/$obtype2/$imagename
				if [[ ! -s $tmp_image ]]; then
					if [[ -s $job_image ]]; then
						cp -v $job_image $tmp_image
					else
						echo "NOTE: $job_image does not exist"
					fi
				fi
				# Time series plots
				for fhr in ${fhrs} ; do
					imagename=evs.${COMPONENT}.${image_stat}.${w_var}_${image_level}_${obtype}.${small_period}.timeseries_valid${vhr}z_f${fhr}.latlon_0p25_${region}.png
            				tmp_image=$DATA/$obtype/$imagename
					job_work_dir=${DATA}/job_work_dir/plot_${wvar}_${vhr}_${fhr}_${stats}_time_series_$(echo ${small_period} | tr '[a-z]' '[A-Z]')
					job_image=$job_work_dir/$obtype/$imagename
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

