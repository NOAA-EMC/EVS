#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the global_ens grid2grid 
#          plotting python script
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
# Virtual link reguired stat files of past 31/90 days
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

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
mkdir -p $plot_dir


verif_case=$VERIF_CASE
#*****************************************
# Build a POE script to collect sub-tasks
# ****************************************
> run_all_poe.sh

for stats in acc me_mae crpss rmse_spread ; do 
if [ $stats = acc ] ; then
  stat_list='acc'
  line_tp='sal1l2'
  #verif_type='anom'
elif [ $stats = bias ] ; then
  stat_list='bias'
  line_tp='sl1l2'
  #verif_type='pres'
elif [ $stats = mae ] ; then
  stat_list='mae'
  line_tp='sl1l2'
  #verif_type='pres'
elif [ $stats = me_mae  ] ; then
  stat_list='me, mae'
  line_tp='ecnt'
  #verif_type='pres'
elif [ $stats = crps  ] ; then
  stat_list='crps'
  line_tp='ecnt'
  #verif_type='pres'
elif [ $stats = crpss ] ; then
  stat_list='crpss'
  line_tp='ecnt'
  #verif_type='pres'
elif [ $stats = rmse_spread  ] ; then
  stat_list='rmse, spread'
  line_tp='ecnt'
  #verif_type='pres'
else
  err_exit "$stats is not a valid metric"
fi   

for score_type in time_series lead_average ; do

  if [ $score_type = time_series ] ; then
    export fcst_init_hour="0,12"
    export fcst_valid_hour="0,12"
    valid_time='valid00z_12z'
    init_time='init00z_12z'
    export fcst_leads="120 240 360"
  else
    export fcst_init_hour="0,12"
    export fcst_valid_hour="0,12"
    valid_time='valid00z_12z'
    init_time='init00z_12z'
    export fcst_leads="vs_lead" 
  fi
 
  for lead in $fcst_leads ; do 

   if [ $lead = vs_lead ] ; then
	export fcst_lead="0, 12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384"
   else
        export fcst_lead=$lead
   fi

    for VAR in HGT TMP UGRD VGRD PRMSL ; do 
       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = HGT ] ; then
          FCST_LEVEL_values="P500 P700 P1000"
       elif [ $VAR = TMP ] ; then
          FCST_LEVEL_values="P500 P850"
       elif [ $VAR = UGRD ] || [ $VAR = VGRD ] ; then
          FCST_LEVEL_values="P850 P250 Z10"
       elif [ $VAR = PRMSL ] ; then
          FCST_LEVEL_values="L0"
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

	 #***************************
	 # Build sub-task scripts
	 #***************************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

        if [ $stats = acc ] ; then
	   verif_type=anom
        else
           if [ $FCST_LEVEL_value = L0 ] || [ $FCST_LEVEL_value = Z10 ] ;  then
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
   mpiexec -np 192 -ppn 96 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
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
                levels='500 700 1000'
                unit='mb'
            elif [ $var = tmp ] ; then
                levels='500 850'
                unit='mb'
            elif [ $var = ugrd ] || [ $var = vgrd ] ; then
                levels='850 250 10'
                unit='mb'
            elif [ $var = prmsl ] ; then
                levels='l0'
                unit=''
            fi
            for level in $levels ; do
                if [ $level = 10 ] ; then
                    unit='m'
	        fi
                if [ $level = 1000 ] || [ $level = 850 ] ||  [ $level = 500  ] ||  [ $level = 250  ] ||  [ $level = 700 ] ; then
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
                    if [ -f "lead_average_regional_${domain}_valid_00z_12z_${var}_${stats}.png" ]; then
                        mv lead_average_regional_${domain}_valid_00z_12z_${var}_${stats}.png evs.global_ens.${evs_graphic_stats}.${var}_${plevel}.last${past_days}days.fhrmean_valid00z_12z_f384.g003_${domain_new}.png
                    fi
                else
                    if [ -f "lead_average_regional_${domain}_valid_00z_12z_${level}${unit}_${var}_${stats}.png" ]; then
                        mv lead_average_regional_${domain}_valid_00z_12z_${level}${unit}_${var}_${stats}.png evs.global_ens.${evs_graphic_stats}.${var}_${plevel}.last${past_days}days.fhrmean_valid00z_12z_f384.g003_${domain_new}.png
                    fi
                fi
                for lead in 120 240 360; do
                    if [ $var = prmsl ] ; then
                        if [ -f "time_series_regional_${domain}_valid_00z_12z_${var}_${stats}_f${lead}.png" ]; then
                            mv time_series_regional_${domain}_valid_00z_12z_${var}_${stats}_f${lead}.png evs.global_ens.${evs_graphic_stats}.${var}_${plevel}.last${past_days}days.timeseries_valid00z_12z_f${lead}.g003_${domain_new}.png
                        fi
                    else
                        if [ -f "time_series_regional_${domain}_valid_00z_12z_${level}${unit}_${var}_${stats}_f${lead}.png" ]; then
                            mv time_series_regional_${domain}_valid_00z_12z_${level}${unit}_${var}_${stats}_f${lead}.png evs.global_ens.${evs_graphic_stats}.${var}_${plevel}.last${past_days}days.timeseries_valid00z_12z_f${lead}.g003_${domain_new}.png
                        fi
                    fi
                done #lead
            done #level
        done #var
    done  #domain
done     #stats

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    cpreq evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar  $COMOUT/.
fi

if [ $SENDDBN = YES ]; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar
fi
