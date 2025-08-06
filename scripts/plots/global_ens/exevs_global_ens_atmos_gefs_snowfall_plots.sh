#!/bin/ksh
#**************************************************************************
# Purpose: set up environment, paths, and run the global_ens snowfall 
#          plotting python scripts
#
# Updated: 07/30/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#          11/17/2023 by Binbin Zhou, Lynker@EMC/NCEP 
#**************************************************************************
set -x

cd $DATA

export output_base_dir=$DATA/stat_archive
export plots_all_dir=$DATA/plots_all
mkdir -p $output_base_dir
mkdir -p $plots_all_dir

verif_case=precip
verif_type=ccpa
model_list='ECME CMCE GEFS'
VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
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

for stats in ets fbias crps fss ; do 
  if [ $stats = ets ] ; then
    stat_list='ets'
    line_tp='ctc'
    VARs='WEASD_24_gt0p0254 SNOD_24_gt0p0254 WEASD_24_gt0p1016 SNOD_24_gt0p1016 WEASD_24_gt0p2032 SNOD_24_gt0p2032 WEASD_24_gt0p3048 SNOD_24_gt0p3048' 
    threshes=''
  elif [ $stats = fbias ] ; then
    stat_list='fbias'
    line_tp='ctc'
    VARs='WEASD_24_gt0p0254 SNOD_24_gt0p0254 WEASD_24_gt0p1016 SNOD_24_gt0p1016 WEASD_24_gt0p2032 SNOD_24_gt0p2032 WEASD_24_gt0p3048 SNOD_24_gt0p3048'
    threshes=''
  elif [ $stats = crps ] ; then
    stat_list='crps'
    line_tp='ecnt'
    VARs='WEASD_24 SNOD_24'
    threshes=''
  elif [ $stats = fss ] ; then
    stat_list='fss'
    line_tp='nbrcnt'
    VARs='WEASD_24_gt0p0254 SNOD_24_gt0p0254 WEASD_24_gt0p1016 SNOD_24_gt0p1016 WEASD_24_gt0p2032 SNOD_24_gt0p2032 WEASD_24_gt0p3048 SNOD_24_gt0p3048'
    threshes=''
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
        FCST_LEVEL_values="L0"

        if [ $VAR = WEASD_24_gt0p0254 ] || [ $VAR = SNOD_24_gt0p0254 ]; then
          threshes='>0.0254'
        elif [ $VAR = WEASD_24_gt0p1016 ] || [ $VAR = SNOD_24_gt0p1016 ]; then
          threshes='>0.1016'
        elif [ $VAR = WEASD_24_gt0p2032 ] || [ $VAR = SNOD_24_gt0p2032 ]; then
          threshes='>0.2032'
        elif [ $VAR = WEASD_24_gt0p3048 ] || [ $VAR = SNOD_24_gt0p3048 ]; then
          threshes='>0.3048'
        fi

        if [ $VAR = SNOD_24_gt0p0254 ] || [ $VAR = SNOD_24_gt0p1016 ] || [ $VAR = SNOD_24_gt0p2032 ] || [ $VAR = SNOD_24_gt0p3048 ] || [ $VAR = SNOD_24 ] ; then
	  models='CMCE, GEFS'
        else
	  models='ECME, CMCE, GEFS'
        fi

        for FCST_LEVEL_value in $FCST_LEVEL_values ; do 
	  OBS_LEVEL_value=A24
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
     
            thresh_fcst=$threshes
            thresh_obs=$threshes

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

for var in weasd snod ; do
    for domain in conus conus_east conus_west conus_south conus_central ; do
        if [ $domain = conus_east ]; then
            evs_graphic_domain="buk_conus_e"
        elif [ $domain = conus_west ]; then
            evs_graphic_domain="buk_conus_w"
        elif [ $domain = conus_south ]; then
            evs_graphic_domain="buk_conus_s"
        elif [ $domain = conus_central ]; then
            evs_graphic_domain="buk_conus_c"
        elif [ $domain = conus ]; then
            evs_graphic_domain="buk_conus"
        fi

	for stats in crps ets fbias fss ; do
            if [ $stats = crps ]; then
                threshs="NA"
            else
                threshs="gt0.0254 gt0.1016 gt0.2032 gt0.3048"
            fi

            if [ $stats = fss ]; then
                nbrhds="1 3 5 7 9 11"
            else
                nbrhds="NA"
            fi

            for thresh in $threshs; do
                if [ $thresh = NA ]; then
                    thresh_graphic=""
                    evs_thresh_graphic=""
                else
                    thresh_graphic=$(echo "_${thresh}")
                    evs_thresh_graphic=$(echo $thresh_graphic | sed -e "s/0\./0p/g")
                fi

                for nbrhd in $nbrhds; do
                    if [ $nbrhd = NA ]; then
                        nbhrd_graphic=""
                    else
                        nbhrd_graphic=$(echo "_width${nbrhd}")
                    fi

                    if [ -f "lead_average_regional_${domain}_valid_12z_${var}_l0_${stats}${nbhrd_graphic}${thresh_graphic}.png" ]; then
                        mv lead_average_regional_${domain}_valid_12z_${var}_l0_${stats}${nbhrd_graphic}${thresh_graphic}.png evs.global_ens.${stats}${nbhrd_graphic}${evs_thresh_graphic}.${var}_a24.last${past_days}days.fhrmean_valid12z_f384.g212_${evs_graphic_domain}.png
                    fi

                    for lead in 120 240 360; do
                        lead_graphic=$(echo "_f${lead}")
                        if [ -f "time_series_regional_${domain}_valid_12z_${var}_l0_${stats}${nbhrd_graphic}${lead_graphic}${thresh_graphic}.png" ]; then
                            mv time_series_regional_${domain}_valid_12z_${var}_l0_${stats}${nbhrd_graphic}${lead_graphic}${thresh_graphic}.png evs.global_ens.${stats}${nbhrd_graphic}${evs_thresh_graphic}.${var}_a24.last${past_days}days.timeseries_valid12z${lead_graphic}.g212_${evs_graphic_domain}.png
                        fi
                    done # lead 
                done # nbrhd
            done # thresh
        done # stats
    done # domain
done # var

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar $COMOUT/.
    fi
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar
fi

