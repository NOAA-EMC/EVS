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

export init_end=$VDATE
export valid_end=$VDATE

model_list='ECME CMCE GEFS'
models='ECME, CMCE, GEFS'

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
  sh $USHevs/global_ens/evs_get_gens_atmos_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


VX_MASK_LIST="G003, NHEM, SHEM, TROPICS, CONUS"
																  
export fcst_init_hour="0,12"
export fcst_valid_hour="0,12"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}


verif_case=$VERIF_CASE

> run_all_poe.sh

for stats in acc bias_mae crpss rmse_spread ; do 
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
elif [ $stats = bias_mae  ] ; then
  stat_list='bias, mae'
  line_tp='sl1l2'
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
  echo $stats is wrong stat
  exit
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
	export fcst_lead="12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384"
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

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=10.0" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

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
         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_list!$thresh!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "sh ${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


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
   mpiexec -np 192 -ppn 192 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
 sh ${DATA}/run_all_poe.sh
fi


cd $plot_dir
for stats in acc bias_mae crpss rmse_spread ; do
 for score_type in time_series lead_average ; do

  if [ $score_type = time_series ] ; then
    leads='_f120.png _f240.png _f360.png'
    scoretype='timeseries' 

  elif [ $score_type = lead_average ] ; then
    leads='.png'
    scoretype='fhrmean'
  fi


  for lead in $leads ; do
    
    if [ $score_type = time_series ] ; then
	lead_time=_${lead:1:4}
    else
        lead_time=''
    fi

   for domain in g003 nhem shem tropics conus ; do

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
           plevel=${level}m
         else
           plevel=$level
         fi

         if [ $var = prmsl ] ; then

             if [ $stats = acc ] ; then 
                  mv ${score_type}_regional_${domain}_valid_00z_12z_l0_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}.${plevel}.last${past_days}days.${scoretype}_${valid_time}.${init_time}${lead_time}.${domain}_glb.png
             else  
		  mv ${score_type}_regional_${domain}_valid_00z_12z_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}.${plevel}.last${past_days}days.${scoretype}_${valid_time}.${init_time}${lead_time}.${domain}_glb.png
             fi

         else

             if [ $var = ugrd ] || [ $var = vgrd ] ; then

	       if [ $level = 10 ] && [ $stats = acc ] ; then
	           mv ${score_type}_regional_${domain}_valid_00z_12z_z10_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}.${plevel}.last${past_days}days.${scoretype}_${valid_time}.${init_time}${lead_time}.${domain}_glb.png
               else
	           mv ${score_type}_regional_${domain}_valid_00z_12z_${level}${unit}_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}.${plevel}.last${past_days}days.${scoretype}_${valid_time}.${init_time}${lead_time}.${domain}_glb.png	     
               fi

            else

               mv ${score_type}_regional_${domain}_valid_00z_12z_${level}${unit}_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}.${plevel}.last${past_days}days.${scoretype}_${valid_time}.${init_time}${lead_time}.${domain}_glb.png

            fi
        fi
               
      done #level

    done #var
   done  #domain
  done   #lead
 done    #score_type
done     #stats

scp *.png wd20bz@emcrzdm:/home/people/emc/www/htdocs/bzhou/evs_plots/gens/grid2grid

tar -cvf plots_gefs_grid2grid_v${VDATE}_$past_days.tar *.png

cp plots_gefs_grid2grid_v${VDATE}_$past_days.tar  $COMOUT/.  





