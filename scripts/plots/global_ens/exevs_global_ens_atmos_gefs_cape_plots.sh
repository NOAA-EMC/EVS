#!/bin/ksh
#*******************************************************************************
# Purpose: set up environment, paths, and run the global_ens cape plotting  
#          python scripts
#
# Updated: 09/05/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#*******************************************************************************
set -x

cd $DATA

export output_base_dir=$DATA/stat_archive
export plots_all_dir=$DATA/plots_all
mkdir -p $output_base_dir
mkdir -p $plots_all_dir

verif_case=grid2obs
model_list='CMCE GEFS'

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
export fcst_valid_hours="0 12"
export interp_pnts=''

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

for fcst_valid_hour in $fcst_valid_hours ; do

  for stats in ets fbias sratio_pod_csi ; do 
    if [ $stats = ets ] ; then
      stat_list='ets'
      line_tp='ctc'
      VARs='CAPEsfc'
      score_types='time_series lead_average'
      VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
    elif [ $stats = fbias ] ; then
      stat_list='fbias'
      line_tp='ctc'
      VARs='CAPEsfc'
      score_types='time_series lead_average'
      VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
    elif [ $stats = sratio_pod_csi ] ; then
      stat_list='sratio, pod, csi'
      line_tp='ctc'
      VARs='CAPEsfc'
      score_types='performance_diagram'
      VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
    else
      err_exit "$stats is not a valid metric"
    fi   

    for score_type in $score_types ; do
      if [ $score_type = time_series ] || [ $score_type = performance_diagram ] ; then
        export fcst_leads="24 120 240 360"
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
	    
          if [ $VAR = CAPEsfc ] ; then
            models='CMCE, GEFS'
	    FCST_LEVEL_values="L0"
          fi
       
          if [ $score_type = performance_diagram ]; then
            thresh_list='all'
          else
            thresh_list='ge250 ge500 ge1000 ge2000'
          fi

          for FCST_LEVEL_value in $FCST_LEVEL_values ; do 
	    OBS_LEVEL_value=$FCST_LEVEL_value
            level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

            for thresh in $thresh_list ; do 
              export WORKtask=$DATA/run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}
	      export prune_dir=$WORKtask/data
	      export save_dir=$WORKtask/out
	      export log_metplus=$WORKtask/logs/GENS_verif_plotting_job.log
	      export plot_dir=$WORKtask/out/sfc_upper/${valid_beg}-${valid_end}
	      mkdir -p $WORKtask
	      mkdir -p $prune_dir
	      mkdir -p $save_dir
	      mkdir -p $WORKtask/logs
	      mkdir -p $plot_dir

              #************************
              # Build sub-task scripts
              #************************
              > run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh

	      echo "export verif_case=$verif_case" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export verif_type=conus_sfc" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export ush_dir=$ush_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export prune_dir=$prune_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export save_dir=$save_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export plot_dir=$plot_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export output_base_dir=$output_base_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export log_metplus=$log_metplus" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export log_level=DEBUG" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
              echo "export date_type=VALID" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export eval_period=TEST" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export valid_beg=$valid_beg" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export valid_end=$valid_end" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export init_beg=$init_beg" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export init_end=$init_end" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export fcst_level=$FCST_LEVEL_value" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export obs_level=$OBS_LEVEL_value" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export var_name=$VAR" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export line_type=$line_tp" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
              echo "export interp=NEAREST" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
              echo "export confidence_intervals=False" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "export PLOT_TYPE=$score_type" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh

              if [ $VAR = CAPEsfc ] && [ $line_tp = ctc ] ; then
                if [ $score_type = performance_diagram ]; then
                  thresh_fcst='>=250, >=500, >=1000, >=2000'
                  thresh_obs='>=250, >=500, >=1000, >=2000'
                else
	          thresh_fcst=$(echo ${thresh/ge/>=})
	          thresh_obs=$(echo ${thresh/ge/>=})
                fi
	      fi

              sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g" -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g" $USHevs/global_ens/evs_gens_atmos_plots_config.sh > $WORKtask/run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh

              chmod +x $WORKtask/run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
              echo "$WORKtask/run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh

	      # Copy png files to plots_all_dir
	      echo "cp $plot_dir/*.png $plots_all_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh

              # Cat the plotting log file
	      echo "if [ -s $log_metplus ]; then" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
              echo "  cat $log_metplus" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh
	      echo "fi" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh

              chmod +x run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh 
              echo "${DATA}/run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.sh" >> run_all_poe.sh

            done # end of thresh
          done # end of FCST_LEVEL_value
        done # end of VAR
      done # end of lead
    done # end of score_type
  done # end of stats 
done # end of fcst_valid_hour 

chmod +x run_all_poe.sh

#*********************************************************************
# Run the POE script in parallel or in sequence to generate png files
#*********************************************************************
if [ $run_mpi = yes ] ; then
  mpiexec -np 88 -ppn 22 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
  export err=$?; err_chk
fi

#*************************************************
# Change plot file names to meet the EVS standard
#*************************************************
cd $plots_all_dir

for ihr in 00z 12z ; do
    for domain in conus conus_east conus_west conus_south conus_central ; do
        if [ $domain = conus_east ]; then
            evs_graphic_domain="conus_e"
        elif [ $domain = conus_west ]; then
            evs_graphic_domain="conus_w"
        elif [ $domain = conus_south ]; then
            evs_graphic_domain="conus_s"
        elif [ $domain = conus_central ]; then
            evs_graphic_domain="conus_c"
        else
            evs_graphic_domain=$domain
        fi

        for lead in 24 120 240 360 ; do
            lead_new=$(printf "%03d" "${lead}")
            if [ -f "performance_diagram_regional_${domain}_valid_${ihr}_cape_f${lead}__ge250ge500ge1000ge2000.png" ]; then
                mv performance_diagram_regional_${domain}_valid_${ihr}_cape_f${lead}__ge250ge500ge1000ge2000.png evs.global_ens.ctc.cape_l0.last${past_days}days.perfdiag_valid${ihr}_f${lead_new}.g212_buk_${evs_graphic_domain}.png
            fi
        done # lead
    done # domain
done # ihr

for stats in ets fbias ; do
    for ihr in 00z 12z ; do
        for thresh in ge250 ge500 ge1000 ge2000 ; do
            for domain in conus conus_east conus_west conus_south conus_central ; do
                if [ $domain = conus_east ]; then
                    evs_graphic_domain="conus_e"
                elif [ $domain = conus_west ]; then
                    evs_graphic_domain="conus_w"
                elif [ $domain = conus_south ]; then
                    evs_graphic_domain="conus_s"
                elif [ $domain = conus_central ]; then
                    evs_graphic_domain="conus_c"
                else
                    evs_graphic_domain=$domain
                fi

                if [ -f "lead_average_regional_${domain}_valid_${ihr}_cape_${stats}_${thresh}.png" ]; then
                    mv lead_average_regional_${domain}_valid_${ihr}_cape_${stats}_${thresh}.png evs.global_ens.${stats}_${thresh}.cape_l0.last${past_days}days.fhrmean_valid${ihr}_f384.g212_buk_${evs_graphic_domain}.png
                fi

                for lead in 24 120 240 360 ; do
                    lead_new=$(printf "%03d" "${lead}")
                    if [ -f "time_series_regional_${domain}_valid_${ihr}_cape_${stats}_f${lead}_${thresh}.png" ]; then
                        mv time_series_regional_${domain}_valid_${ihr}_cape_${stats}_f${lead}_${thresh}.png evs.global_ens.${stats}_${thresh}.cape_l0.last${past_days}days.timeseries_valid${ihr}_f${lead_new}.g212_buk_${evs_graphic_domain}.png
                    fi
                done # lead
            done # domain
        done # thresh
    done # ihr
done # stats

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.cape.last${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.cape.last${past_days}days.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.cape.last${past_days}days.v${VDATE}.tar $COMOUT/.
    fi
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.cape.last${past_days}days.v${VDATE}.tar
fi

