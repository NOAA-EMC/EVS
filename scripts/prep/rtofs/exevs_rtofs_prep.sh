#!/bin/bash
#############################################################################################
# Name of Script: exevs_rtofs_prep.sh
# Purpose of Script: To copy RTOFS production data, convert RTOFS forecasts grids,
#                    process obs, create masking files
# Authors: Mallory Row (mallory.row@noaa.gov)
#		
# Modified for EVSv2:
# By: Samira Ardani (samira.ardani@noaa.gov)
# 05/2024: Modified the code so that the RTOFS prep job writes to one rtofs.YYYMMDD directory.
# 08/2024: Added restart capability and the remaining fixes and additions for EVS v2.0.
#############################################################################################

set -x

##########################
# get latest RTOFS data
##########################
if [ ! -d $COMOUTprep/rtofs.$INITDATE ]; then
    mkdir -p $COMOUTprep/rtofs.$INITDATE
fi
# n024 is nowcast = f000 forecast
leads='n024 f024 f048 f072 f096 f120 f144 f168 f192'
filetypes_2ds='diag ice prog'
filestypes_3dz_daily='3zsio 3ztio 3zuio 3zvio'
for lead in ${leads}; do
    # glo_2ds files
    for filetype in ${filetypes_2ds}; do
        input_rtofs_file=$COMINrtofs/rtofs.$INITDATE/rtofs_glo_2ds_${lead}_${filetype}.nc
        tmp_rtofs_file=${DATA}/rtofs_glo_2ds_${lead}_${filetype}.nc
        output_rtofs_file=$COMOUTprep/rtofs.$INITDATE/rtofs_glo_2ds_${lead}_${filetype}.nc
        if [ ! -s $output_rtofs_file ]; then
            if [ -s $input_rtofs_file ]; then
                cp -v $input_rtofs_file $tmp_rtofs_file
                if [ $SENDCOM = YES ]; then
			if [ -s $tmp_rtofs_file ]; then
                    		cp -v $tmp_rtofs_file $output_rtofs_file
			fi
                fi
            else
                echo "WARNING: ${input_rtofs_file} does not exist"
                if [ $SENDMAIL = YES ] ; then
                    export subject="${lead} RTOFS Forecast Data Missing for EVS ${COMPONENT}"
                    echo "Warning: No RTOFS forecast was available for ${INITDATE}${lead}" > mailmsg
                    echo "Missing file is ${input_rtofs_file}" >> mailmsg
                    echo "Job ID: $jobid" >> mailmsg
                    cat mailmsg | mail -s "$subject" $MAILTO
                fi
            fi
   	else
	    echo "RESTART: $output_rtofs_file exists; Copying to $tmp_rtofs_file"
	    cp -v $output_rtofs_file $tmp_rtofs_file

        fi
    done
    # glo_3dz daily files
    for filetype in ${filestypes_3dz_daily}; do
        input_rtofs_file=$COMINrtofs/rtofs.$INITDATE/rtofs_glo_3dz_${lead}_daily_${filetype}.nc
        tmp_rtofs_file=${DATA}/rtofs_glo_3dz_${lead}_daily_${filetype}.nc
        output_rtofs_file=$COMOUTprep/rtofs.$INITDATE/rtofs_glo_3dz_${lead}_daily_${filetype}.nc
        if [ ! -s $output_rtofs_file ]; then
            if [ -s $input_rtofs_file ]; then
                cp -v $input_rtofs_file $tmp_rtofs_file
                if [ $SENDCOM = YES ]; then
			if [ -s $tmp_rtofs_file ]; then
                    		cp -v $tmp_rtofs_file $output_rtofs_file
			fi
                fi
            else
                echo "WARNING: ${input_rtofs_file} does not exist"
                if [ $SENDMAIL = YES ] ; then
                    export subject="${lead} RTOFS Forecast Data Missing for EVS ${COMPONENT}"
                    echo "Warning: No RTOFS forecast was available for ${INITDATE}${lead}" > mailmsg
                    echo "Missing file is ${input_rtofs_file}" >> mailmsg
                    echo "Job ID: $jobid" >> mailmsg
                    cat mailmsg | mail -s "$subject" $MAILTO
                fi
            fi
        else
	   echo "RESTART: $output_rtofs_file exists; Copying to $tmp_rtofs_file"
           cp -v $output_rtofs_file $tmp_rtofs_file
        fi
    done
done

##########################
#  convert RTOFS forecast data into lat-lon grids for each OBTYPE;
#  OBTYPE is the validation source: ghrsst, smos, smap etc.
##########################
for rcase in ghrsst smos smap aviso osisaf ndbc argo; do
	export OBTYPE=$rcase
	for lead in ${leads}; do
		if [ $lead = n024 ]; then
			fhr=000
		else
			fhr=$(echo $lead | cut -c 2-4)
		fi
		if [ ! -d $COMOUTprep/rtofs.$INITDATE/$OBTYPE ]; then
			mkdir -p $COMOUTprep/rtofs.$INITDATE/$OBTYPE
        	fi
        	mkdir -p $DATA/rtofs.$INITDATE/$OBTYPE
        	for ftype in prog diag ice; do
			rtofs_grid_file=$FIXevs/cdo_grids/rtofs_$OBTYPE.grid
			rtofs_native_filename=$EVSINprep/rtofs.$INITDATE/rtofs_glo_2ds_${lead}_${ftype}.nc
			tmp_rtofs_latlon_filename=$DATA/rtofs.$INITDATE/$OBTYPE/rtofs_glo_2ds_f${fhr}_${ftype}.$OBTYPE.nc
			output_rtofs_latlon_filename=$COMOUTprep/rtofs.$INITDATE/$OBTYPE/rtofs_glo_2ds_f${fhr}_${ftype}.$OBTYPE.nc
			if [ ! -s $output_rtofs_latlon_filename ]; then
                		if [ -s $rtofs_native_filename ]; then
                    			cdo remapbil,$rtofs_grid_file $rtofs_native_filename $tmp_rtofs_latlon_filename
                    			export err=$?; err_chk
                    			if [ $SENDCOM = "YES" ]; then
                        			if [ -s $tmp_rtofs_latlon_filename ]; then
			    				cp -v $tmp_rtofs_latlon_filename $output_rtofs_latlon_filename
						fi
                    			fi
                		else
                    			echo "WARNING: ${rtofs_native_filename} does not exist; cannot create ${tmp_rtofs_latlon_filename}"
                		fi
			else
				echo "RESTART: $output_rtofs_latlon_filename exists; Copying to $tmp_rtofs_latlon_filename"
				cp -v $output_rtofs_latlon_filename $tmp_rtofs_latlon_filename

            		fi
        	done
        	if [ $OBTYPE = 'argo' ] ; then
			for ftype in t s; do
                		rtofs_grid_file=$FIXevs/cdo_grids/rtofs_$OBTYPE.grid
                		rtofs_native_filename=$EVSINprep/rtofs.$INITDATE/rtofs_glo_3dz_${lead}_daily_3z${ftype}io.nc
                		tmp_rtofs_latlon_filename=$DATA/rtofs.$INITDATE/$OBTYPE/rtofs_glo_3dz_f${fhr}_daily_3z${ftype}io.$OBTYPE.nc
                		output_rtofs_latlon_filename=$COMOUTprep/rtofs.$INITDATE/$OBTYPE/rtofs_glo_3dz_f${fhr}_daily_3z${ftype}io.$OBTYPE.nc
                		if [ ! -s $output_rtofs_latlon_filename ]; then
                    			if [ -s $rtofs_native_filename ]; then
                        			cdo remapbil,$rtofs_grid_file $rtofs_native_filename $tmp_rtofs_latlon_filename
                        			export err=$?; err_chk
                        			if [ $SENDCOM = "YES" ]; then
                            				if [ -s $tmp_rtofs_latlon_filename ]; then
								cp -v $tmp_rtofs_latlon_filename $output_rtofs_latlon_filename
			    				fi
                        			fi
                    			else
                        			echo "WARNING: ${rtofs_native_filename} does not exist; cannot create ${tmp_rtofs_latlon_filename}"
                    			fi
				else
					echo "RESTART: $output_rtofs_latlon_filename exists; Copying to $tmp_rtofs_latlon_filename"
					cp -v $output_rtofs_latlon_filename $tmp_rtofs_latlon_filename

                		fi
            		done
        	fi
	done
done

##########################
#  process obs data
##########################
min_size=2404
# convert OSI-SAF data into lat-lon grid
export OBTYPE=osisaf
if [ ! -d $COMOUTprep/rtofs.$INITDATE/$OBTYPE ]; then
	mkdir -p $COMOUTprep/rtofs.$INITDATE/$OBTYPE
fi
mkdir -p $DATA/rtofs.$INITDATE/$OBTYPE
for ftype in nh sh; do
	osi_saf_grid_file=$FIXevs/cdo_grids/rtofs_$OBTYPE.grid
	input_osisaf_file=$DCOMROOT/$INITDATE/seaice/osisaf/ice_conc_${ftype}_polstere-100_multi_${INITDATE}1200.nc
	tmp_osisaf_file=$DATA/rtofs.$INITDATE/$OBTYPE/ice_conc_${ftype}_polstere-100_multi_${INITDATE}1200.nc
	output_osisaf_file=$COMOUTprep/rtofs.$INITDATE/$OBTYPE/ice_conc_${ftype}_polstere-100_multi_${INITDATE}1200.nc
	if [ -s $input_osisaf_file ]; then
    		actual_size_osisaf=$(wc -c <"$DCOMROOT/$INITDATE/seaice/osisaf/ice_conc_${ftype}_polstere-100_multi_${INITDATE}1200.nc")
    	fi
    	if [[ ! -s $input_osisaf_file || $actual_size_osisaf -lt $min_size ]]; then
	    	echo "WARNING: No OSI-SAF ${ftype} data was available for valid date $INITDATE."
	    	if [ $SENDMAIL = YES ] ; then
			export subject="OSI-SAF Data Missing for EVS RTOFS"
		    	echo "Warning: No OSI-SAF ${ftype} data was available for valid date $INITDATE." > mailmsg
		    	echo "Missing file is $input_osisaf_file" >> mailmsg
		    	cat mailmsg | mail -s "$subject" $MAILTO
	    	fi
    	fi
    	if [ ! -s $output_osisaf_file ]; then
        	if [ -s $input_osisaf_file ]; then
            		cdo remapbil,$osi_saf_grid_file $input_osisaf_file $tmp_osisaf_file
            		export err=$?; err_chk
            		if [ $SENDCOM = "YES" ]; then
                		if [ -s $tmp_osisaf_file ]; then
		    			cp -v $tmp_osisaf_file $output_osisaf_file
				fi
            		fi
        	else
			echo "WARNING: No OSI-SAF ${ftype} data was available for valid date $INITDATE."
            		if [ $SENDMAIL = YES ] ; then
                		export subject="OSI-SAF Data Missing for EVS RTOFS"
                		echo "Warning: No OSI-SAF ${ftype} data was available for valid date $INITDATE." > mailmsg
                		echo "Missing file is $input_osisaf_file" >> mailmsg
                		cat mailmsg | mail -s "$subject" $MAILTO
            		fi
        	fi
	else
		echo "RESTART: $output_osisaf_file exists; Copying to $tmp_osisaf_file"
		cp -v $output_osisaf_file $tmp_osisaf_file

    	fi
done
# convert NDBC *.txt files into a netcdf file using ASCII2NC
export OBTYPE=ndbc
if [ ! -d $COMOUTprep/rtofs.$INITDATE/$OBTYPE ]; then
	mkdir -p $COMOUTprep/rtofs.$INITDATE/$OBTYPE
fi
if [ ! -d $COMOUTprep/rtofs.$INITDATE/$OBTYPE/buoy ]; then
    	mkdir -p $COMOUTprep/rtofs.$INITDATE/$OBTYPE/buoy
fi
mkdir -p $DATA/rtofs.$INITDATE/$OBTYPE
mkdir -p $DATA/rtofs.$INITDATE/$OBTYPE/buoy
export MET_NDBC_STATIONS=${FIXevs}/ndbc_stations/ndbc_stations.xml
ndbc_txt_ncount=$(find $DCOMROOT/$INITDATE/validation_data/marine/buoy -type f -name "*.txt" |wc -l)
if [ $ndbc_txt_ncount -gt 0 ]; then
	python $USHevs/${COMPONENT}/${COMPONENT}_${STEP}_trim_ndbc_files.py
    	export err=$?; err_chk
    	tmp_ndbc_file=$DATA/rtofs.$INITDATE/$OBTYPE/ndbc.${INITDATE}.nc
    	output_ndbc_file=$COMOUTprep/rtofs.$INITDATE/$OBTYPE/ndbc.${INITDATE}.nc
    	if [ ! -s $output_ndbc_file ]; then
        	run_metplus.py -c $PARMevs/metplus_config/machine.conf \
        	-c $CONFIGevs/$STEP/$COMPONENT/grid2obs/ASCII2NC_obsNDBC.conf
        	export err=$?; err_chk
         	if [ $SENDCOM = YES ]; then
             		if [ -s $tmp_ndbc_file ] ; then
				cp -v $tmp_ndbc_file $output_ndbc_file
			fi
         	fi
	else
		echo "RESTART: $output_ndbc_file exists; Copying to $tmp_ndbc_file"
		cp -v $output_ndbc_file $tmp_ndbc_file

   	 fi
else
	echo "WARNING: No NDBC data was available for valid date $INITDATE."	
  	if [ $SENDMAIL = YES ] ; then
    		export subject="NDBC Data Missing for EVS RTOFS"
    		echo "Warning: No NDBC data was available for valid date $INITDATE." > mailmsg
    		echo "Missing files are located at $DCOMROOT/$INITDATE/validation_data/marine/buoy" >> mailmsg
    		cat mailmsg | mail -s "$subject" $MAILTO
  	fi
fi
# convert Argo basin files into a netcdf file using python embedding
export OBTYPE=argo
if [ ! -d $COMOUTprep/rtofs.$INITDATE/$OBTYPE ]; then
	mkdir -p $COMOUTprep/rtofs.$INITDATE/$OBTYPE
fi
mkdir -p $DATA/rtofs.$INITDATE/$OBTYPE
if [ -s $DCOMROOT/$INITDATE/validation_data/marine/argo/atlantic_ocean/${INITDATE}_prof.nc ] && [ -s $DCOMROOT/$INITDATE/validation_data/marine/argo/indian_ocean/${INITDATE}_prof.nc ] && [ -s $DCOMROOT/$INITDATE/validation_data/marine/argo/pacific_ocean/${INITDATE}_prof.nc ]; then
	actual_size_argo_atlantic=$(wc -c <"$DCOMROOT/$INITDATE/validation_data/marine/argo/atlantic_ocean/${INITDATE}_prof.nc")
	actual_size_argo_indian=$(wc -c <"$DCOMROOT/$INITDATE/validation_data/marine/argo/indian_ocean/${INITDATE}_prof.nc")
	actual_size_argo_pacific=$(wc -c <"$DCOMROOT/$INITDATE/validation_data/marine/argo/pacific_ocean/${INITDATE}_prof.nc")
	if [ $actual_size_argo_atlantic -gt $min_size ] && [ $actual_size_argo_indian -gt $min_size ] && [ $actual_size_argo_pacific -gt $min_size ] ; then
		tmp_argo_file=$DATA/rtofs.$INITDATE/$OBTYPE/argo.${INITDATE}.nc
		output_argo_file=$COMOUTprep/rtofs.$INITDATE/$OBTYPE/argo.${INITDATE}.nc
		if [ ! -s $output_argo_file ]; then
			run_metplus.py -c $PARMevs/metplus_config/machine.conf \
			-c $CONFIGevs/$STEP/$COMPONENT/grid2obs/ASCII2NC_obsARGO.conf
			export err=$?; err_chk
			if [ $SENDCOM = YES ]; then
				if [ -s $tmp_argo_file ] ; then
					cp -v $tmp_argo_file $output_argo_file
				fi
			fi
		else
			echo "RESTART: $output_argo_file exists; Copying to $tmp_argo_file"
			cp -v $output_argo_file $tmp_argo_file
		fi
	else
		if [ $SENDMAIL = YES ] ; then
			export subject="Argo Data Missing for EVS RTOFS"
			echo "Warning: No Argo data was available for valid date $INITDATE." > mailmsg
			echo "Missing file is $DCOMROOT/$INITDATE/validation_data/marine/argo/atlantic_ocean/${INITDATE}_prof.nc, $DCOMROOT/$INITDATE/validation_data/marine/argo/indian_ocean/${INITDATE}_prof.nc, and/or $DCOMROOT/$INITDATE/validation_data/marine/argo/pacific_ocean/${INITDATE}_prof.nc" >> mailmsg
			cat mailmsg | mail -s "$subject" $MAILTO
		fi
	fi
else
	echo "WARNING: No Argo data was available for valid date $INITDATE."
	if [ $SENDMAIL = YES ] ; then
		export subject="Argo Data Missing for EVS RTOFS"
		echo "Warning: No Argo data was available for valid date $INITDATE." > mailmsg
		echo "Missing file is $DCOMROOT/$INITDATE/validation_data/marine/argo/atlantic_ocean/${INITDATE}_prof.nc, $DCOMROOT/$INITDATE/validation_data/marine/argo/indian_ocean/${INITDATE}_prof.nc, and/or $DCOMROOT/$INITDATE/validation_data/marine/argo/pacific_ocean/${INITDATE}_prof.nc" >> mailmsg
		cat mailmsg | mail -s "$subject" $MAILTO
	fi
fi


##########################
#  create the masks
#  NOTE: script below is calling MET's gen_vx_mask directly instead of using METplus
#        so keeping it in a ush script; future use should use METplus to do this
##########################
for rcase in ghrsst smos smap aviso osisaf ndbc argo; do
    export OBTYPE=$rcase
    $USHevs/${COMPONENT}/${COMPONENT}_${STEP}_regions.sh
done
################################ END OF SCRIPT ################################
