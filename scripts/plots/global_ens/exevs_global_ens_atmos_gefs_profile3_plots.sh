#!/bin/ksh
#*******************************************************************************
# Purpose: set up environment, paths, and run the global_ens profile3
#          plotting python scripts
# Note:    The profile plots are split to 4 smaller scripts: profile1,2,3,4.
#          profile3 is for vertical profiles of ECNT scores 
#
# Updated: 07/28/2025 by L. Gwen Chen (lichuan.chen@noaa.gov)
#          11/17/2023 by Binbin Zhou, Lynker@EMC/NCEP
#*******************************************************************************
set -x

cd $DATA

export output_base_dir=$DATA/stat_archive
export plots_all_dir=$DATA/plots_all
mkdir -p $output_base_dir
mkdir -p $plots_all_dir

verif_case=grid2obs
verif_type=upper_air
model_list='ECME CMCE GEFS'
VX_MASK_LIST="G003, NHEM, SHEM, TROPICS, CONUS"
valid_time='valid12z'
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

for stats in rmse_spread me ; do 
  if [ $stats = me ] ; then
    stat_list='me'
    line_tp='ecnt'
  elif [ $stats = mae ] ; then
    stat_list='mae'
    line_tp='ecnt'
  elif [ $stats = rmse_spread ] ; then
    stat_list='rmse, spread'
    line_tp='ecnt'
  else
    err_exit "$stats is not a valid metric"
  fi   

  for score_type in stat_by_level ; do
    export fcst_leads="0 12 24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"
 
    for lead in $fcst_leads ; do 
      export fcst_lead=$lead

      if [ $fcst_lead = 372 ] || [ $fcst_lead = 384 ]; then
	models='CMCE, GEFS'
      else
	models='ECME, CMCE, GEFS'
      fi

      for VAR in HGT TMP UGRD VGRD RH ; do 
        var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
        if [ $VAR = HGT ] || [ $VAR = UGRD ] || [ $VAR = VGRD ]; then
          FCST_LEVEL_value="P1000,P925,P850,P700,P500,P300,P250,P200,P100,P50,P10"
        elif [ $VAR = TMP ] || [ $VAR = RH ] ; then
          FCST_LEVEL_value="P1000,P925,P850,P700,P500,P250,P200,P100,P50,P10"
        fi

	OBS_LEVEL_value=$FCST_LEVEL_value
        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

        for line_type in $line_tp ; do
	  export WORKtask=$DATA/run_${stats}.${score_type}.${lead}.${VAR}.${line_type}
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
          > run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh  

          echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
	  echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
          echo "export ush_dir=$ush_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
	  echo "export prune_dir=$prune_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
	  echo "export save_dir=$save_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
	  echo "export plot_dir=$plot_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export output_base_dir=$output_base_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
          echo "export log_metplus=$log_metplus" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export valid_beg=$valid_beg" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export valid_end=$valid_end" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export init_beg=$init_beg" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export init_end=$init_end" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
          echo "export fcst_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export confidence_intervals=False" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

	  thresh=''

          sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g" -e "s!thresh_fcst!$thresh!g" -e "s!thresh_obs!$thresh!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g" $USHevs/global_ens/evs_gens_atmos_plots_config.sh > $WORKtask/run_py.${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

          chmod +x $WORKtask/run_py.${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh
          echo "$WORKtask/run_py.${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

          # Copy png files to plots_all_dir            
	  echo "cp $plot_dir/*.png $plots_all_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

	  # Cat the plotting log file            
	  echo "if [ -s $log_metplus ]; then" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "  cat $log_metplus" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh            
	  echo "fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh

          chmod +x run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh 
          echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${line_type}.sh" >> run_all_poe.sh

        done # end of line_type
      done # end of VAR
    done # end of lead
  done # end of score_type
done # end of stats 

chmod +x run_all_poe.sh

#*********************************************************************
# Run the POE script in parallel or in sequence to generate png files
#*********************************************************************
if [ $run_mpi = yes ] ; then
  mpiexec -np 330 -ppn 55 --cpu-bind verbose,depth --depth 2 cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
  export err=$?; err_chk
fi

#*************************************************
# Change plot file names to meet the EVS standard
#*************************************************
cd $plots_all_dir

for stats in rmse_spread me ; do
    if [ $stats = rmse_spread ]; then
        evs_graphic_stats="rmse_sprd"
    else
        evs_graphic_stats=$stats
    fi

    for domain in g003 nhem shem tropics conus ; do
        if [ $domain = g003 ] ; then
            domain_new=glb
        elif [ $domain = conus ]; then
            domain_new="buk_conus"
        else
            domain_new=$domain
        fi

	for var in hgt tmp ugrd vgrd rh ; do
            leads="0 12 24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384"

	    for lead in $leads ; do
                lead_new=$(printf "%03d" "${lead}")
                if [ -f "stat_by_level_regional_${domain}_valid_12z_${var}_${stats}_f${lead}.png" ]; then
                    mv stat_by_level_regional_${domain}_valid_12z_${var}_${stats}_f${lead}.png evs.global_ens.${evs_graphic_stats}.${var}_all.last${past_days}days.vertprof_valid12z_f${lead_new}.g003_${domain_new}.png
                fi
            done # lead
        done # var
    done # domain
done # stats

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar $COMOUT/.
    fi
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar
fi

