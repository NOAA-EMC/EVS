#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the NAEFS grid2obs verification 
#          score plotting python script
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

met_v=`echo $MET_VERSION | sed "s/\([^.]*\.[^.]*\)\..*/\1/g"`
export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='NAEFS CMCE GEFS'
models='NAEFS, CMCE, GEFS'

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


export fcst_init_hour="0,12"
export fcst_valid_hour="0,12"
valid_time='valid00z_12z'
init_time='init00z_12z'

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
mkdir -p $plot_dir

verif_case=$VERIF_CASE


#*****************************************
# Build a POE script to collect sub-tasks
# ****************************************
> run_all_poe.sh

for stats in acc crps rmse_spread me_mae ; do 
 if [ $stats = acc ] ; then
  stat_list='acc'
  line_tp='sal1l2'
  VARs='TMP2m UGRD10m VGRD10m UGRD VGRD TMP'
 elif [ $stats = crps ] ; then
  stat_list='crps'
  line_tp='ecnt'
  VARs='TMP2m  UGRD10m VGRD10m UGRD VGRD TMP'
 elif [ $stats = rmse_spread  ] ; then
  stat_list='rmse, spread'
  line_tp='ecnt'
  VARs='TMP2m UGRD10m VGRD10m UGRD VGRD TMP'
 elif [ $stats = me_mae ] ; then
  stat_list='me, mae'
  line_tp='ecnt'
  VARs='TMP2m UGRD10m VGRD10m UGRD VGRD TMP'
 else
  err_exit "$stats is not a valid metric"
 fi   

 for score_type in lead_average ; do

  export fcst_leads="vs_lead" 
 
  for lead in $fcst_leads ; do 

    export fcst_lead="0, 12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384"

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = TMP2m ] || [ $VAR = DPT2m ] || [ $VAR = RH2m ] ; then 
          FCST_LEVEL_values="Z2"
	  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
       elif [ $VAR = UGRD10m ] || [ $VAR = VGRD10m ] ; then
          FCST_LEVEL_values="Z10"
	  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
       elif [ $VAR = UGRD ] || [ $VAR = VGRD ] ; then
          FCST_LEVEL_values="P850 P250"
	  VX_MASK_LIST="NHEM, SHEM, TROPICS"
       elif [ $VAR = TMP ]  ; then
	  FCST_LEVEL_values="P850"
          VX_MASK_LIST="NHEM, SHEM, TROPICS"
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         #***************************
         # Build sub-task scripts
         #***************************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

	if [ $VAR = UGRD ] || [ $VAR = VGRD ] || [ $VAR = TMP ] ; then
              if [ $line_type = sal1l2 ] ; then
	         verif_case=grid2grid
	         verif_type=anom
	      else
	         verif_case=$VERIF_CASE
	         verif_type=upper_air
	      fi
         else
             verif_case=$VERIF_CASE
             verif_type=conus_sfc
	 fi	

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=$met_v" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

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

         thresh_fcst=' '
	 thresh_obs=' '

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

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
   mpiexec -np 32 -ppn 32 --cpu-bind verbose,core cfp ${DATA}/run_all_poe.sh
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

cd $plot_dir

for stats in  acc crps rmse_spread me_mae ; do
    if [ $stats = rmse_spread ]; then
        evs_graphic_stats="rmse_sprd"
    else
        evs_graphic_stats=$stats
    fi
    for var in tmp ugrd vgrd ; do
        if [ $var = tmp ] || [ $var = dpt ] ; then
	    levels='2m 850mb'
        elif [ $var = ugrd ] || [ $var = vgrd ] ; then
	    levels='10m 850mb 250mb'
        fi
        for level in $levels ; do     
            if [ $level = 850mb ] || [ $level = 250mb ] ; then
                domains='nhem shem tropics'
            else
	        domains='conus conus_east conus_west conus_south conus_central alaska'
            fi
            if [ $level = 850mb ] ; then
                level_new=p850
            elif [ $level = 250mb ] ; then
                level_new=p250
            elif [ $level = 2m ] ; then
                level_new=z2
            elif [ $level = 10m ] ; then
                level_new=z10
            else
	        level_new=$level
            fi
            for domain in $domains ; do	
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
                else
                    evs_graphic_domain=$domain
                fi
                if [ $domain = nhem ] || [ $domain = shem ] || [ $domain = tropics ] || [ $domain = alaska ]; then
                    if [ -f "lead_average_regional_${domain}_valid_00z_12z_${level}_${var}_${stats}.png" ]; then
                        mv lead_average_regional_${domain}_valid_00z_12z_${level}_${var}_${stats}.png  evs.naefs.${evs_graphic_stats}.${var}_${level_new}.last${past_days}days.fhrmean_valid00z_12z_f384.g003_${evs_graphic_domain}.png
                    fi
                else
                    if [ -f "lead_average_regional_${domain}_valid_00z_12z_${level}_${var}_${stats}.png" ]; then
                        mv lead_average_regional_${domain}_valid_00z_12z_${level}_${var}_${stats}.png  evs.naefs.${evs_graphic_stats}.${var}_${level_new}.last${past_days}days.fhrmean_valid00z_12z_f384.g212_${evs_graphic_domain}.png
                    fi
                fi
            done #domain
        done #level
    done   #var
done     #stats

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    cpreq evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar  $COMOUT/.
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar
fi

