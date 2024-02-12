#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the global_ens profile2 
#          plotting python script
#  Note: The profile plots are split to 4 smaller scripts: profile1,2,3,4.
#        The profile2 is for MAE for different levels
#
# Last updated: 11/17/2023, Binbin Zhou Lynker@EMC/NCEP
#******************************************************************************
set -x 

cd $DATA

export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/GENS_verif_plotting_job.out
mkdir -p $prune_dir
mkdir -p $save_dir
mkdir -p $output_base_dir
mkdir -p $DATA/logs

export eval_period='TEST'

export interp_pnts='' 

export init_end=$VDATE
export valid_end=$VDATE

model_list='ECME CMCE GEFS'

n=0
while [ $n -le $past_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

#*************************************************************
# Virtual link required stat data files of past 31/90 days
#*************************************************************
n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/global_ens/evs_get_gens_atmos_stat_file_link_plots.sh $day "$model_list"
  export err=$?; err_chk
  n=$((n+1))
done 


VX_MASK_LIST="G003, NHEM, SHEM, TROPICS, CONUS"

export fcst_init_hour="0,12"
export fcst_valid_hour="0,12"
valid_time='valid00z_12z'
init_time='init00z_12z'


export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
mkdir -p $plot_dir

verif_case=grid2obs
verif_type=upper_air

#*****************************************
# Build a POE script to collect sub-tasks
# ****************************************
> run_all_poe.sh

for stats in  mae ; do 

if [ $stats = me ] ; then
  stat_list='me'
  line_tp='ecnt'
elif [ $stats = mae ] ; then
  stat_list='mae'
  line_tp='ecnt'
elif [ $stats = rmse_spread  ] ; then
  stat_list='rmse, spread'
  line_tp='ecnt'
else
  err_exit "$stats is not a valid metric"
fi   

 for score_type in time_series lead_average ; do

  if [ $score_type = time_series ] ; then
    export fcst_leads="120 240 360"
  else
    export fcst_leads="vs_lead" 
  fi
 
  for lead in $fcst_leads ; do 

   if [ $lead = vs_lead ] ; then
	export fcst_lead="0, 12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384"
   else
        export fcst_lead=$lead
   fi

    for VAR in HGT TMP UGRD VGRD RH ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = HGT ] || [ $VAR = UGRD ] || [ $VAR = VGRD ] ; then
          FCST_LEVEL_values="P1000 P925 P850 P700 P500 P300 P250 P200 P100 P50 P10"
       elif [ $VAR = TMP ] || [ $VAR = RH ] ; then
          FCST_LEVEL_values="P1000 P925 P850 P700 P500 P250 P200 P100 P50 P10"
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         #***************************
         # Build sub-task scripts
         #***************************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

	 if [ $FCST_LEVEL_value = P10 ] || [ $FCST_LEVEL_value = P250 ]; then
	    models='CMCE, GEFS'
	 else
	    models='ECME, CMCE, GEFS'
         fi

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

	 thresh=' '
         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh!g" -e "s!thresh_obs!$thresh!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g"  $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo " ${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh


#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 212 -ppn 53 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
  export err=$?; err_chk
fi

# Cat the plotting log file
log_file=$DATA/logs/GENS_verif_plotting_job.out
if [ -s $log_file ]; then
    echo "Start: $log_file"
    cat $log_file
    echo "End: $log_file"
fi

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for stats in mae ; do
    for domain in g003 nhem shem tropics conus ; do
        if [ $domain = g003 ] ; then
            domain_new=glb
        elif [ $domain = conus ]; then
            domain_new="buk_conus"
        else
            domain_new=$domain
        fi
        for var in hgt tmp ugrd vgrd rh ; do
            if [ $var = hgt ] || [ $var = ugrd ] || [ $var = vgrd ] ; then
                levels='1000 925 850 700 500 300 250 200 100 50 10'
            elif [ $var = tmp ] || [ $var = rh ] ; then
                levels='1000 925 850 700 500 250 200 100 50 10'
            fi
            for level in $levels ; do
                plevel=p${level}
                if [ -f "lead_average_regional_${domain}_valid_00z_12z_${level}mb_${var}_${stats}.png" ]; then
                    mv lead_average_regional_${domain}_valid_00z_12z_${level}mb_${var}_${stats}.png  evs.global_ens.${stats}.${var}_${plevel}.last${past_days}days.fhrmean_valid00z_12z_f384.g003_${domain_new}.png
                fi
                for lead in 120 240 360; do
                    if [ -f "time_series_regional_${domain}_valid_00z_12z_${level}mb_${var}_${stats}_f${lead}.png" ]; then
                        mv time_series_regional_${domain}_valid_00z_12z_${level}mb_${var}_${stats}_f${lead}.png  evs.global_ens.${stats}.${var}_${plevel}.last${past_days}days.timeseries_valid00z_12z_f${lead}.g003_${domain_new}.png
                    fi
                done #lead
            done #level
        done #var
    done  #domain
done     #stats

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar  $COMOUT/.
    fi
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar
fi

