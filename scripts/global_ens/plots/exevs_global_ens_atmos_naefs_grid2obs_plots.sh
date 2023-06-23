#!/bin/ksh

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

n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/global_ens/evs_get_gens_atmos_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


export fcst_init_hour="0,12"
export fcst_valid_hour="0,12"
valid_time='valid00z_12z'
init_time='init00z_12z'

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}


verif_case=$VERIF_CASE


> run_all_poe.sh

for stats in acc bias_mae crps rmse_spread me_mae ; do 
 if [ $stats = acc ] ; then
  stat_list='acc'
  line_tp='sal1l2'
  VARs='TMP2m UGRD10m VGRD10m UGRD VGRD TMP'
 elif [ $stats = bias_mae  ] ; then
  stat_list='bias, mae'
  line_tp='sl1l2'
  VARs='TMP2m  UGRD10m VGRD10m '
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
  VARs='UGRD VGRD TMP'
 else
  echo $stats is wrong stat
  exit
 fi   

 for score_type in lead_average ; do

  export fcst_leads="vs_lead" 
 
  for lead in $fcst_leads ; do 

    export fcst_lead="12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384"

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


if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 37 -ppn 37 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi

cd $plot_dir

for stats in  acc bias_mae crps rmse_spread me_mae ; do
 for score_type in lead_average ; do

    leads='.png'
    scoretype='fhrmean'
    vars='tmp ugrd vgrd'

  for lead in $leads ; do
    
    lead_time=''

    for var in $vars ; do
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
      elif [ $level = 850mb ] ; then
	 level_new=p250
      else
	 level_new=$level
      fi

      for domain in $domains ; do

        if [ $domain = nhem ] || [ $domain = shem ] || [ $domain = tropics ] ; then
           mv ${score_type}_regional_${domain}_valid_00z_12z_${level}_${var}_${stats}${lead}  evs.naefs.${stats}.${var}_${level_new}.last${past_days}days.${scoretype}.${valid_time}${lead_time}.g003_${domain}.png
	else
           mv ${score_type}_regional_${domain}_valid_00z_12z_${level}_${var}_${stats}${lead}  evs.naefs.${stats}.${var}_${level_new}.last${past_days}days.${scoretype}.${valid_time}${lead_time}.buk_${domain}.png
        fi
               
      done #domain

    done #level
   done  #domain
  done   #var
 done    #score_type
done     #stats

#scp *.png wd20bz@emcrzdm:/home/people/emc/www/htdocs/bzhou/evs_plots/naefs/grid2obs

tar -cvf evs.plots.naefs.grid2obs.v${VDATE}.past${past_days}days.tar *.png

cp evs.plots.naefs.grid2obs.v${VDATE}.past${past_days}days.tar  $COMOUT/.  








