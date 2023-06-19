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
  $USHevs/global_ens/evs_get_gens_atmos_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


#VX_MASK_LIST="CONUS"
VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
																  
export fcst_init_hour="0,12"
export fcst_valid_hour="12"

export plot_dir=$DATA/out/precip/${valid_beg}-${valid_end}


verif_case=precip
verif_type=ccpa

> run_all_poe.sh

for stats in ets fbias crps fss ; do 
  if [ $stats = ets ] ; then
    stat_list='ets'
    line_tp='ctc'
    VARs='WEASD_24 SNOD_24' 
    threshes='>0.0254, >0.1016, >0.2032, >0.3048'
  elif [ $stats = fbias ] ; then
    stat_list='fbias'
    line_tp='ctc'
    VARs='WEASD_24 SNOD_24'
    threshes='>0.0254, >0.1016, >0.2032, >0.3048'
  elif [ $stats = crps  ] ; then
    stat_list='crps'
    line_tp='ecnt'
    VARs='WEASD_24 SNOD_24'
    threshes=''
  elif [ $stats = fss ] ; then
    stat_list='fss'
    line_tp='nbrcnt'
    VARs='WEASD_24 SNOD_24'
    threshes='>0.0254, >0.1016, >0.2032, >0.3048'
  else
    echo $stats is wrong stat
  exit
  fi   

  if [ $stats = fss ] ; then
   interp_pnts='1,9,25,49,91,121'
  else
   interp_pnts=''
  fi 

 for score_type in time_series lead_average ; do

  if [ $score_type = time_series ] ; then
    export fcst_init_hour="0,12"
    export fcst_valid_hour="12"
    valid_time='valid_12z'
    init_time='init00z_12z'
    export fcst_leads="120 240 360"
  else
    export fcst_init_hour="0,12"
    export fcst_valid_hour="12"
    valid_time='valid_12z'
    init_time='init00z_12z'
    export fcst_leads="vs_lead" 
  fi
 
  for lead in $fcst_leads ; do 

   if [ $lead = vs_lead ] ; then
	export fcst_lead="24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336, 360, 384"
   else
        export fcst_lead=$lead
   fi

    for VAR in  $VARs; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       FCST_LEVEL_values="L0"

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=A24

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

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
         if [ $stats = fss ] ; then
            echo "export interp=NBRHD_SQUARE" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         else	   
	    echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
	 fi
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
     
         thresh_fcst=$threshes
         thresh_obs=$threshes

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g"  $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

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
   mpiexec -np 32 -ppn 32 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi

cd $plot_dir

for stats in  crps ets fbias fss ; do
 vars='weasd_l0 snod_l0'
 for score_type in time_series lead_average ; do

   if [ $score_type = time_series ] ; then
     if [ $stats = fss ] || [ $stats = ets ] || [ $stats = fbias ] ; then	   
       leads='_f120_gt0.0254gt0.1016gt0.2032gt0.3048.png _f240_gt0.0254gt0.1016gt0.2032gt0.3048.png _f360_gt0.0254gt0.1016gt0.2032gt0.3048.png'
     else       
       leads='_f120.png _f240.png _f360.png'
     fi       
     scoretype='timeseries'
   elif [ $score_type = lead_average ] ; then
     if [  $stats = fss ] || [ $stats = ets ] || [ $stats = fbias ] ; then	   
       leads='_gt0.0254gt0.1016gt0.2032gt0.3048.png'
     else
       leads='.png'	     
     fi
     scoretype='fhrmean'

   fi

   for lead in $leads ; do
      if [ $score_type = time_series ] ; then
          lead_time=_${lead:1:4}
      else
          lead_time=_f384
     fi

     for domain in conus conus_east conus_west conus_south conus_central ; do

      for var in $vars ; do
    
	if [ $var = weasd_l0 ] ; then
	   var_new=weasd_a24
	elif [ $var = snod_l0 ] ; then
	   var_new=snod_a24
	fi 

        if [ $stats = fss ] ; then	     
          mv ${score_type}_regional_${domain}_valid_12z_${var}_${stats}_width1-3-5-7-9-11${lead} evs.global_ens.${stats}.${var_new}.last${past_days}days.${scoretype}.valid_12z${lead_time}.buk_${domain}.png  
       else
	  mv ${score_type}_regional_${domain}_valid_12z_${var}_${stats}${lead} evs.global_ens.${stats}.${var_new}.last${past_days}days.${scoretype}.valid_12z${lead_time}.buk_${domain}.png
        fi

      done #var	
     done  #domain
  done   #lead
 done    #score_type
done     #stats


#scp *.png wd20bz@emcrzdm:/home/people/emc/www/htdocs/bzhou/evs_plots/gens/snowfall

tar -cvf evs.plots.gefs.snowfall.v${VDATE}.past${past_days}days.tar *.png

cp evs.plots.gefs.snowfall.v${VDATE}.past${past_days}days.tar  $COMOUT/.  





