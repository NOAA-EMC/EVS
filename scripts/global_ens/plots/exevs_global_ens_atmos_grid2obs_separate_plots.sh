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


VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
																  
export fcst_init_hour="0,12"
export fcst_valid_hours="0 12"

#  valid_time='valid00z_12z'
init_time='init00z_12z'


export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}


verif_case=$VERIF_CASE

> run_all_poe.sh

export fcst_valid_hour 

for fcst_valid_hour in $fcst_valid_hours ; do

  valid_time=valid${fcst_valid_hour}z

for stats in acc bias_mae crpss rmse_spread ; do 
 if [ $stats = acc ] ; then
  stat_list='acc'
  line_tp='sal1l2'
  VARs='TMP2m DPT2m UGRD10m VGRD10m'
  score_types='time_series lead_average'
 elif [ $stats = bias_mae  ] ; then
  stat_list='bias, mae'
  line_tp='sl1l2'
  VARs='TMP2m DPT2m UGRD10m VGRD10m RH2m'
  score_types='time_series lead_average'
 elif [ $stats = crpss ] ; then
  stat_list='crpss'
  line_tp='ecnt'
  score_types='time_series lead_average'
  VARs='TMP2m DPT2m UGRD10m VGRD10m'
 elif [ $stats = rmse_spread  ] ; then
  stat_list='rmse, spread'
  line_tp='ecnt'
  VARs='TMP2m DPT2m UGRD10m VGRD10m RH2m'
  score_types='time_series lead_average'
 else
  echo $stats is wrong stat
  exit
 fi   

 for score_type in $score_types ; do

  if [ $score_type = time_series ] ; then
    export fcst_leads="120 240 360"
  else 
    export fcst_leads="vs_lead" 
  fi
 
  for lead in $fcst_leads ; do 

   if [ $lead = vs_lead ] ; then
	export fcst_lead="12, 24, 36, 48, 60, 72, 84, 96,108, 120, 132, 144, 156, 168, 180, 192,204, 216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 360, 372, 384"
   else
        export fcst_lead=$lead
   fi

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = TMP2m ] || [ $VAR = DPT2m ] || [ $VAR = RH2m ] ; then 
          FCST_LEVEL_values="Z2"
       elif [ $VAR = UGRD10m ] || [ $VAR = VGRD10m ] ; then
          FCST_LEVEL_values="Z10"
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

        verif_type=conus_sfc

        echo "export PLOT_TYPE=$score_type" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=10.0" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        else
          echo "export date_type=VALID" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        fi


         echo "export var_name=$VAR" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export interp=NEAREST" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

	 if [ $VAR = CAPEsfc ] && [ $line_type = ctc ] ; then
	   thresh=$thresh_cape
	 else
	   thresh=' '
	 fi 

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_list!$thresh!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "sh ${DATA}/run_py.${fcst_valid_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


         chmod +x  run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo " ${DATA}/run_${fcst_valid_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done #fcst_valid_hour 

chmod +x run_all_poe.sh

if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 144 -ppn 144 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
 sh ${DATA}/run_all_poe.sh
fi



cd $plot_dir

for vhr in 00z 12z ; do
 for stats in  acc bias_mae crpss rmse_spread ; do
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

    for domain in conus conus_east conus_west conus_south conus_central alaska ; do

     for var in tmp dpt ugrd vgrd rh ; do
      if [ $var = tmp ] || [ $var = dpt ] || [ $var = rh ]; then
	 levels='2m'
      elif [ $var = ugrd ] || [ $var = vgrd ] ; then
	 levels='10m'
      fi

       for level in $levels ; do

        mv ${score_type}_regional_${domain}_valid_${vhr}_${level}_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}.${level}.last${past_days}days.${scoretype}_valid${vhr}.${init_time}${lead_time}.buk_${domain}.png

               
      done #level

    done #var
   done  #domain
  done   #lead
 done    #score_type
done     #stats
done     #vhr









