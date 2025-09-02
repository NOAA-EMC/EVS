#!/bin/ksh
#*******************************************************************************
# Purpose: set up environment, paths, and run the global_ens grid2grid 
#          plotting python scripts
#
# Updated: 08/14/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#          07/22/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#          11/17/2023 by Binbin Zhou, Lynker@EMC/NCEP
#*******************************************************************************
set -x

cd $DATA

export output_base_dir=$DATA/stat_archive
export plots_all_dir=$DATA/plots_all
mkdir -p $output_base_dir
mkdir -p $plots_all_dir

verif_case=$VERIF_CASE 
model_list='ECME CMCE GEFS'
VX_MASK_LIST="G003, NHEM, SHEM, TROPICS, CONUS"

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
  for stats in acc me_mae crpss rmse_spread ; do 
    if [ $stats = acc ] ; then
      stat_list='acc'
      line_tp='sal1l2'
    elif [ $stats = bias ] ; then
      stat_list='bias'
      line_tp='sl1l2'
    elif [ $stats = mae ] ; then
      stat_list='mae'
      line_tp='sl1l2'
    elif [ $stats = me_mae ] ; then
      stat_list='me, mae'
      line_tp='ecnt'
    elif [ $stats = crpss ] ; then
      stat_list='crpss'
      line_tp='ecnt'
    elif [ $stats = rmse_spread ] ; then
      stat_list='rmse, spread'
      line_tp='ecnt'
    else
      err_exit "$stats is not a valid metric"
    fi   

    for score_type in time_series lead_average ; do
      if [ $score_type = time_series ] ; then
        export fcst_leads="24 120 240 360"
      else
        export fcst_leads="vs_lead" 
      fi
 
      for lead in $fcst_leads ; do 
        if [ $lead = vs_lead ] ; then
	  export fcst_lead="0, 24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336, 360, 384"
        else
          export fcst_lead=$lead
        fi

        for VAR in HGT TMP UGRD VGRD PRMSL ; do 
          var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
          if [ $VAR = HGT ] ; then
            FCST_LEVEL_values="P500 P1000"
          elif [ $VAR = TMP ] ; then
            FCST_LEVEL_values="P500 P850"
          elif [ $VAR = UGRD ] || [ $VAR = VGRD ] ; then
            FCST_LEVEL_values="P250 P850"
          elif [ $VAR = PRMSL ] ; then
            FCST_LEVEL_values="L0"
          fi

          for FCST_LEVEL_value in $FCST_LEVEL_values ; do 
	    OBS_LEVEL_value=$FCST_LEVEL_value
            level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

            for line_type in $line_tp ; do
	      export WORKtask=$DATA/run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}
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
              > run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

              if [ $stats = acc ] ; then
                verif_type=anom
              else
                if [ $FCST_LEVEL_value = L0 ] || [ $FCST_LEVEL_value = Z10 ] ; then
                  verif_type=sfc
                else
    		  verif_type=pres
	        fi
	      fi

	      if [ $FCST_LEVEL_value = P250 ]; then
	        models='CMCE, GEFS'
              else
	        models='ECME, CMCE, GEFS'
	      fi

              echo "export verif_case=$verif_case" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
	      echo "export verif_type=$verif_type" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
              echo "export ush_dir=$ush_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
	      echo "export prune_dir=$prune_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
	      echo "export save_dir=$save_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
	      echo "export plot_dir=$plot_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
              echo "export output_base_dir=$output_base_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
	      echo "export log_metplus=$log_metplus" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
              echo "export log_level=DEBUG" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
              echo "export date_type=VALID" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh	    
	      echo "export eval_period=TEST" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "export valid_beg=$valid_beg" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "export valid_end=$valid_end" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "export init_beg=$init_beg" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "export init_end=$init_end" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "export fcst_level=$FCST_LEVEL_value" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "export obs_level=$OBS_LEVEL_value" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
	      echo "export var_name=$VAR" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh           
	      echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "export line_type=$line_type" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "export interp=NEAREST" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
              echo "export confidence_intervals=False" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
	      echo "export PLOT_TYPE=$score_type" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

	      thresh=''

              sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g" -e "s!thresh_fcst!$thresh!g" -e "s!thresh_obs!$thresh!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g" $USHevs/global_ens/evs_gens_atmos_plots_config.sh > $WORKtask/run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

              chmod +x $WORKtask/run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
              echo "$WORKtask/run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

              # Copy png files to plots_all_dir            
	      echo "cp $plot_dir/*.png $plots_all_dir" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

              # Cat the plotting log file            
	      echo "if [ -s $log_metplus ]; then" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "  cat $log_metplus" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh            
	      echo "fi" >> run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

              chmod +x run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
              echo "${DATA}/run_${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

            done # end of line_type
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
  mpiexec -np 360 -ppn 120 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
  export err=$?; err_chk
fi

#*************************************************
# Change plot file names to meet the EVS standard
#*************************************************
cd $plots_all_dir

for ihr in 00z 12z ; do
  for stats in acc me_mae crpss rmse_spread ; do
    if [ $stats = rmse_spread ]; then
        evs_graphic_stats="rmse_sprd"
    else
        evs_graphic_stats=$stats
    fi

    for domain in g003 nhem shem tropics conus ; do
        if [ $domain = g003 ] ; then
            domain_new="glb"
        elif [ $domain = conus ]; then
            domain_new="buk_conus"
        else
	    domain_new=$domain
        fi

        for var in hgt tmp ugrd vgrd prmsl ; do
            if [ $var = hgt ] ; then
                levels='500 1000'
                unit='mb'
            elif [ $var = tmp ] ; then
                levels='500 850'
                unit='mb'
            elif [ $var = ugrd ] || [ $var = vgrd ] ; then
                levels='250 850'
                unit='mb'
            elif [ $var = prmsl ] ; then
                levels='l0'
                unit=''
            fi

            for level in $levels ; do
                if [ $level = 10 ] ; then
                    unit='m'
	        fi

                if [ $level = 1000 ] || [ $level = 850 ] || [ $level = 500 ] || [ $level = 250 ] ; then
                    plevel=p${level}
                elif [ $level = 10 ] ; then
                    plevel=z${level}
                else
                    if [ $var = prmsl ] ; then
                        plevel=z0
                    else
                        plevel=$level
	            fi
                fi

                if [ $var = prmsl ] ; then
                    if [ -f "lead_average_regional_${domain}_valid_${ihr}_${var}_${stats}.png" ]; then
                        mv lead_average_regional_${domain}_valid_${ihr}_${var}_${stats}.png evs.global_ens.${evs_graphic_stats}.${var}_${plevel}.last${past_days}days.fhrmean_valid${ihr}_f384.g003_${domain_new}.png
                    fi
                else
                    if [ -f "lead_average_regional_${domain}_valid_${ihr}_${level}${unit}_${var}_${stats}.png" ]; then
                        mv lead_average_regional_${domain}_valid_${ihr}_${level}${unit}_${var}_${stats}.png evs.global_ens.${evs_graphic_stats}.${var}_${plevel}.last${past_days}days.fhrmean_valid${ihr}_f384.g003_${domain_new}.png
                    fi
                fi

                for lead in 24 120 240 360; do
                    if [ $var = prmsl ] ; then
                        if [ -f "time_series_regional_${domain}_valid_${ihr}_${var}_${stats}_f${lead}.png" ]; then
                            mv time_series_regional_${domain}_valid_${ihr}_${var}_${stats}_f${lead}.png evs.global_ens.${evs_graphic_stats}.${var}_${plevel}.last${past_days}days.timeseries_valid${ihr}_f${lead}.g003_${domain_new}.png
                        fi
                    else
                        if [ -f "time_series_regional_${domain}_valid_${ihr}_${level}${unit}_${var}_${stats}_f${lead}.png" ]; then
                            mv time_series_regional_${domain}_valid_${ihr}_${level}${unit}_${var}_${stats}_f${lead}.png evs.global_ens.${evs_graphic_stats}.${var}_${plevel}.last${past_days}days.timeseries_valid${ihr}_f${lead}.g003_${domain_new}.png
                        fi
                    fi
                done # lead
            done # level
        done # var
    done # domain
  done # stats
done # ihr

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.last${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.last${past_days}days.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.last${past_days}days.v${VDATE}.tar $COMOUT/.
    fi
fi

if [ $SENDDBN = YES ]; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.last${past_days}days.v${VDATE}.tar
fi
