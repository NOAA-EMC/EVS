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

model_list='HREF'
models='HREF'

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
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


VX_MASK_LIST="CONUS, Alaska, Hawaii, PRico"
#VX_MASK_LIST="PRico"

export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,12"
valid_time='valid00_12z'
init_time='init00z_06z_12z_18Z'


export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}

verif_case=grid2obs
verif_type=upper_air

> run_all_poe.sh

for stats in rmse_spread bss ; do 

if [ $stats = rmse_spread  ] ; then
  stat_list='rmse, spread'
  line_tp='ecnt'
  score_types='stat_by_level'
  VARS='HGT TMP UGRD VGRD RH'
elif [ $stats = bss ] ; then
  stat_list='bss_smpl'
  line_tp='pstd'  
  score_types='lead_average'
  VARS='TMP_lt0C'
  #VARS='TMP_lt0C WIND_ge30kt WIND_ge40kt'
else
  echo $stats is wrong stat
  exit
fi   

 for score_type in $score_types ; do

  export fcst_leads="6,12,18,24,30,36,42,48"
 
  for lead in $fcst_leads ; do 

    export fcst_lead=$lead

    for VAR in $VARS ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $score_type = stat_by_level ] ; then
         FCST_LEVEL_values="P1000,P975,P950,P925,P900,P875,P850,P825,P800,P750,P700,P650,P600,P550,P500,P400,P300,P200"
       elif [ $score_type = lead_average ] ; then 
	  if [ $VAR = TMP_lt0C ] ; then
	     FCST_LEVEL_values="P850"
	  else
             FCST_LEVEL_values="P850 P700"
	  fi
       fi	  
     
     for FCST_LEVEL_value in $FCST_LEVEL_values ; do  

       OBS_LEVEL_value=$FCST_LEVEL_value

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
         echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         if [ $line_tp = ecnt ] ; then
	   thresh_fcst=' '
	   thresh_obs=' '
	 elif [ $line_tp = pstd ] ; then
	    if [ $VAR = TMP_lt0C ] ; then
	       thresh_fcst='==0.10000'
	       thresh_obs='<273.15'
             elif [ $VAR =  WIND_ge30kt ] ; then
	       thresh_fcst='==0.10000'
	       thresh_obs='>=15.4'
	     elif [ $VAR =  WIND_ge40kt ] ; then
	       thresh_fcst='==0.10000'
               thresh_obs='>=20.58'
             fi	       
	 fi

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g"  $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done # end of level

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh

if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 10 -ppn 10 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi

cd $plot_dir

for stats in rmse_spread bss_smpl ; do
 if [ $stats = rmse_spread ] ; then
  score_types='stat_by_level'
  leads='_f6-12-18-24-30-36-42-48.png'
  vars='hgt rh tmp ugrd vgrd'
 else
  score_types='lead_average'
  leads='.png'
  vars='700mb_wind_ens_freq_ge15.4 700mb_wind_ens_freq_ge20.58 850mb_tmp_ens_freq_lt273.15 850mb_wind_ens_freq_ge15.4 850mb_wind_ens_freq_ge20.58'
 fi

 for score_type in $score_types  ; do
  
  if [ $score_type = stat_by_level ] ; then
     scoretype='profile'
  elif [ $score_type = lead_average ] ; then
     scoretype='fhrmean'
  fi


  for lead in $leads ; do
    
   for domain in conus alaska hawaii prico; do

    for var in $vars ; do

      if [ $score_type = lead_average  ] ; then
	level=p${var:0:3}
	if [ $var = 700mb_wind_ens_freq_ge15.4 ] ; then
	  var_new='windspeed.ge.30kt.p700'
	elif [ $var = 700mb_wind_ens_freq_ge20.58 ] ; then
	  var_new='windspeed.ge.40KT.P700'
	elif [ $var = 850mb_wind_ens_freq_ge15.4 ] ; then
	  var_new='windspeed.ge.30kt.p850'
        elif [ $var = 850mb_wind_ens_freq_ge20.58 ] ; then
          var_new='windspeed.ge.40kt.p850'	
        elif [ $var = 850mb_tmp_ens_freq_lt273.15 ] ; then
	  lead=_eq0.10000.png	
	  var_new='tmp.lt.0C.p850'
	fi
	valid="valid_available_times"
      else
        level=''
	var_new=$var
	valid="valid_00z_12z"
      fi	

      
       mv ${score_type}_regional_${domain}_${valid}_${var}_${stats}${lead}  evs.href.${stats}.${var_new}.last${past_days}days.${scoretype}.${valid_time}.${init_time}.buk_${domain}.png

    done #var
   done  #domain
  done   #lead
 done    #score_type
done     #stats


tar -cvf evs.plots.href.profile.past${past_days}days.v${VDATE}.tar *.png

cp evs.plots.href.profile.past${past_days}days.v${VDATE}.tar  $COMOUT/.  

