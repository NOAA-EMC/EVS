#!/bin/ksh
#**************************************************************************
# Purpose: set up environment, paths, and run the global_ens precip
#          plotting python scripts
#
# Updated: 07/23/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#          03/14/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#          11/17/2023 by Binbin Zhou, Lynker@EMC/NCEP
#**************************************************************************
set -x 

cd $DATA

export output_base_dir=$DATA/stat_archive
export plots_all_dir=$DATA/plots_all
mkdir -p $output_base_dir
mkdir -p $plots_all_dir

verif_case=$VERIF_CASE
verif_type=ccpa
model_list='ECME CMCE GEFS'
models='ECME, CMCE, GEFS'
VX_MASK_LIST="CONUS, CONUS_East, CONUS_South, CONUS_Central, CONUS_West"
valid_time='valid_12z'
init_time='init00z_12z'

n=0
while [ $n -le $past_days ] ; do
  hrs=$((n*24))
  first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  n=$((n+1))
done

export valid_beg=$first_day
export valid_end=$VDATE
export init_beg=$first_day
export init_end=$VDATE
export fcst_init_hour="0,12"
export fcst_valid_hour="12"

#*************************************************
# Create links of stat files from past 31/90 days
#*************************************************
n=0
while [ $n -le $past_days ] ; do
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/global_ens/evs_get_gens_atmos_stat_file_link_plots.sh $day "$model_list"
  export err=$?; err_chk
  n=$((n+1))
done 

#*****************************************
# Build a POE script to collect sub-tasks
#*****************************************
> run_all_poe.sh

for stats in ets fbias crps me rmse bs bss fss ; do 
  if [ $stats = ets ] ; then
    stat_list='ets'
    line_tp='ctc'
    VARs='APCP24_gt1 APCP24_gt5 APCP24_gt10 APCP24_gt25 APCP24_gt50' 
    threshes=''
  elif [ $stats = fbias ] ; then
    stat_list='fbias'
    line_tp='ctc'
    VARs='APCP24_gt1 APCP24_gt5 APCP24_gt10 APCP24_gt25 APCP24_gt50'
    threshes=''
  elif [ $stats = crps ] ; then
    stat_list='crps'
    line_tp='ecnt'
    VARs='APCP_24'
    threshes=''
  elif [ $stats = me ] ; then
    stat_list='me'
    line_tp='ecnt'
    VARs='APCP_24'
    threshes=''
  elif [ $stats = rmse ] ; then
    stat_list='rmse'
    line_tp='ecnt'
    VARs='APCP_24'
    threshes=''
  elif [ $stats = bs ] ; then
    stat_list='bs'
    line_tp='pstd'
    VARs='APCP24_gt1 APCP24_gt5 APCP24_gt10 APCP24_gt25 APCP24_gt50'
    threshes=''
  elif [ $stats = bss ] ; then
    stat_list='bss'
    line_tp='pstd'
    VARs='APCP24_gt1 APCP24_gt5 APCP24_gt10 APCP24_gt25 APCP24_gt50'
    threshes=''
  elif [ $stats = fss ] ; then
    stat_list='fss'
    line_tp='nbrcnt'
    VARs='APCP24_gt1 APCP24_gt5 APCP24_gt10 APCP24_gt25 APCP24_gt50'
    threshes=''  #should set to threshes='>=1,>=5,>=10,>=25,>=50'? if not, then all thresholds will be used! 
  else
    err_exit "$stats is not a valid metric"
  fi   

  if [ $stats = fss ] ; then
    interp_pnts='1 9 25 49 81 121'
  else
    interp_pnts='1'
  fi 

  for score_type in time_series lead_average ; do
    if [ $score_type = time_series ] ; then
      export fcst_leads="120 240 360"
    else
      export fcst_leads="vs_lead" 
    fi
 
    for lead in $fcst_leads ; do 
      if [ $lead = vs_lead ] ; then
	export fcst_lead="24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336, 360, 384"
      else
        export fcst_lead=$lead
      fi

      for VAR in $VARs ; do 
        var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
        FCST_LEVEL_values="A24"

        if [ $VAR = APCP24_gt1 ] ; then
	  threshes='>1'
        elif [ $VAR = APCP24_gt5 ] ; then
          threshes='>5'	       
        elif [ $VAR = APCP24_gt10 ] ; then
          threshes='>10'
        elif [ $VAR = APCP24_gt25 ] ; then
          threshes='>25'
        elif [ $VAR = APCP24_gt50 ] ; then
          threshes='>50'
        fi

        for FCST_LEVEL_value in $FCST_LEVEL_values ; do 
	  OBS_LEVEL_value=$FCST_LEVEL_value
          level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

          for interp_pnt in $interp_pnts ; do 
            export WORKtask=$DATA/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}
	    export prune_dir=$WORKtask/data
	    export save_dir=$WORKtask/out
	    export log_metplus=$WORKtask/logs/GENS_verif_plotting_job.log
	    export plot_dir=$WORKtask/out/precip/${valid_beg}-${valid_end}
	    mkdir -p $WORKtask
	    mkdir -p $prune_dir
	    mkdir -p $save_dir
	    mkdir -p $WORKtask/logs
	    mkdir -p $plot_dir

            #************************
            # Build sub-task scripts
            #************************
            > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh  

            echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
            echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export ush_dir=$ush_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export prune_dir=$prune_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export save_dir=$save_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export plot_dir=$plot_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export output_base_dir=$output_base_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export log_metplus=$log_metplus" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export valid_beg=$valid_beg" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export valid_end=$valid_end" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export init_beg=$init_beg" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export init_end=$init_end" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export fcst_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export line_type=$line_tp" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
            echo "export confidence_intervals=False" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh

	    if [ $stats = fss ] ; then
              echo "export interp=NBRHD_SQUARE" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
              interp_pnt_config=$interp_pnt
            else	   
	      echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
              interp_pnt_config=''
	    fi

	    if [ $line_tp = pstd ] ; then
	      thresh_fcst='==0.10000'
	      thresh_obs=$threshes
            else
	      thresh_fcst=$threshes
              thresh_obs=$threshes
	    fi

            sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g" -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnt_config!g" $USHevs/global_ens/evs_gens_atmos_plots_config.sh > $WORKtask/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh

            chmod +x $WORKtask/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
            echo "$WORKtask/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh

	    # Copy png files to plots_all_dir            
	    echo "cp $plot_dir/*.png $plots_all_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh

	    # Cat the plotting log file            
	    echo "if [ -s $log_metplus ]; then" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
            echo "  cat $log_metplus" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh
	    echo "fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh

            chmod +x run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh 
            echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_tp}_${interp_pnt}.sh" >> run_all_poe.sh

          done # end of interp_pnt
        done # end of FCST_LEVEL_value
      done # end of VAR
    done # end of lead
  done # end of score_type
done # end of stats 

chmod +x run_all_poe.sh

#*********************************************************************
# Run the POE script in parallel or in sequence to generate png files
#*********************************************************************
if [ $run_mpi = yes ] ; then
  mpiexec -np 32 -ppn 32 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
  export err=$?; err_chk
fi

#*************************************************
# Change plot file names to meet the EVS standard
#*************************************************
cd $plots_all_dir

for domain in conus conus_east conus_west conus_south conus_central ; do
    if [ $domain = conus ]; then
        evs_graphic_domain="buk_conus"
    elif [ $domain = conus_east ]; then
        evs_graphic_domain="buk_conus_e"
    elif [ $domain = conus_west ]; then
        evs_graphic_domain="buk_conus_w"
    elif [ $domain = conus_south ]; then
        evs_graphic_domain="buk_conus_s"
    elif [ $domain = conus_central ]; then
        evs_graphic_domain="buk_conus_c"
    fi

    for stat in ets fbias crps me rmse bs bss fss ; do
        if [ $stat = crps ]; then
            threshs="NA"
	elif [ $stat = me ]; then
	    threshs="NA"
	elif [ $stat = rmse ]; then
	    threshs="NA"
        else
            threshs="gt1 gt5 gt10 gt25 gt50"
        fi

	if [ $stat = fss ]; then
            nbrhds="1 3 5 7 9 11"
        else
            nbrhds="NA"
        fi

	for thresh in $threshs; do
            if [ $thresh = NA ]; then
                thresh_graphic=""
            else
                thresh_graphic=$(echo "_${thresh}")
            fi

	    for nbrhd in $nbrhds; do
                if [ $nbrhd = NA ]; then
                    nbhrd_graphic=""
                else
                    nbhrd_graphic=$(echo "_width${nbrhd}")
                fi

		if [ $stat = bs ]; then
                    if [ -f "lead_average_regional_${domain}_valid_12z_24h_apcp_24_ens_freq${thresh_graphic}_bs.png" ]; then
                        mv lead_average_regional_${domain}_valid_12z_24h_apcp_24_ens_freq${thresh_graphic}_bs.png evs.global_ens.${stat}${nbhrd_graphic}${thresh_graphic}.apcp_a24.last${past_days}days.fhrmean_valid12z_f384.g212_${evs_graphic_domain}.png
                    fi
                elif [ $stat = bss ]; then
		    if [ -f "lead_average_regional_${domain}_valid_12z_24h_apcp_24_ens_freq${thresh_graphic}_bss.png" ]; then
		        mv lead_average_regional_${domain}_valid_12z_24h_apcp_24_ens_freq${thresh_graphic}_bss.png evs.global_ens.${stat}${nbhrd_graphic}${thresh_graphic}.apcp_a24.last${past_days}days.fhrmean_valid12z_f384.g212_${evs_graphic_domain}.png
		    fi
   	        else
                    if [ -f "lead_average_regional_${domain}_valid_12z_24h_apcp_24_${stat}${nbhrd_graphic}${thresh_graphic}.png" ]; then
                        mv lead_average_regional_${domain}_valid_12z_24h_apcp_24_${stat}${nbhrd_graphic}${thresh_graphic}.png evs.global_ens.${stat}${nbhrd_graphic}${thresh_graphic}.apcp_a24.last${past_days}days.fhrmean_valid12z_f384.g212_${evs_graphic_domain}.png
                    fi
                fi

		for lead in 120 240 360; do
                    lead_graphic=$(echo "_f${lead}")
                    if [ $stat = bs ]; then
                        if [ -f "time_series_regional_${domain}_valid_12z_24h_apcp_24_ens_freq${thresh_graphic}_bs${lead_graphic}.png" ]; then
                            mv time_series_regional_${domain}_valid_12z_24h_apcp_24_ens_freq${thresh_graphic}_bs${lead_graphic}.png evs.global_ens.${stat}${nbhrd_graphic}${thresh_graphic}.apcp_a24.last${past_days}days.timeseries_valid12z${lead_graphic}.g212_${evs_graphic_domain}.png
                        fi
		    elif [ $stat = bss ]; then
			if [ -f "time_series_regional_${domain}_valid_12z_24h_apcp_24_ens_freq${thresh_graphic}_bss${lead_graphic}.png" ]; then
			    mv time_series_regional_${domain}_valid_12z_24h_apcp_24_ens_freq${thresh_graphic}_bss${lead_graphic}.png evs.global_ens.${stat}${nbhrd_graphic}${thresh_graphic}.apcp_a24.last${past_days}days.timeseries_valid12z${lead_graphic}.g212_${evs_graphic_domain}.png
			fi
                    else
                        if [ -f "time_series_regional_${domain}_valid_12z_24h_apcp_24_${stat}${nbhrd_graphic}${lead_graphic}${thresh_graphic}.png" ]; then
                            mv time_series_regional_${domain}_valid_12z_24h_apcp_24_${stat}${nbhrd_graphic}${lead_graphic}${thresh_graphic}.png evs.global_ens.${stat}${nbhrd_graphic}${thresh_graphic}.apcp_a24.last${past_days}days.timeseries_valid12z${lead_graphic}.g212_${evs_graphic_domain}.png
                        fi
                    fi
                done # lead
            done # nbrhd
        done # thresh
    done # stat
done # domain

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar $COMOUT/.
    fi
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar
fi

