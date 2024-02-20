#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href profile plotting python script
# Last updated: 10/30/2023, Binbin Zhou Lynker@EMC/NCEP
#******************************************************************************
set -x 

cd $DATA

export machine=${machine:-"WCOSS2"}
export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/GENS_verif_plotting_job
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

#*************************************************************
# Virtual link the href's stat data files of past 31/90 days
#*************************************************************
n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day "$model_list"
  export err=$?; err_chk
  n=$((n+1))
done 



export fcst_init_hour="0,6,12,18"
valid_time='valid00_12z'
init_time='init00z_06z_12z_18Z'


export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}

verif_case=grid2obs
verif_type=upper_air

#*****************************************
# Build a POE file to collect sub-jobs
#****************************************
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
  VARS='TMP_lt0C WIND_ge30kt WIND_ge40kt'
else
  err_exit "$stats is not a valid stat"
fi   

 for fcst_valid_hour in 00 12 ; do

  for score_type in $score_types ; do

   if [ $score_type = lead_average ] ; then
     export fcst_leads="6,12,18,24,30,36,42,48"
   else 
     export fcst_leads="06 12 18 24 30 36 42 48"
   fi

   for lead in $fcst_leads ; do 

    export fcst_lead=$lead

    if [[ "$fcst_lead" == "06" ]] || [[ "$fcst_lead" == "18" ]] || [[ "$fcst_lead" == "30" ]] || [[ "$fcst_lead" == "42" ]] ; then
       VX_MASK_LIST="CONUS, Alaska, PRico"
    elif [[ "$fcst_lead" == "12" ]] || [[ "$fcst_lead" == "24" ]] || [[ "$fcst_lead" == "36" ]] || [[ "$fcst_lead" == "48" ]] ; then
       VX_MASK_LIST="CONUS, Hawaii"
    else
       VX_MASK_LIST="CONUS, Alaska"
    fi

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

	 #*********************
	 # Build sub-jobs
	 # ********************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh  

	if [ $score_type = lead_average ] ; then
	    echo "export PLOT_TYPE=lead_average_valid" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        else	    
            echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        fi

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
        fi

         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
         echo "export interp=BILIN" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

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

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g"  $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh


         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${fcst_valid_hour}.sh" >> run_all_poe.sh

      done #end of line_type

     done # end of level

    done #end of VAR

   done #end of fcst_lead

  done # end of fcst_valid_hour 

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 60 -depth 1 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for valid in 00z 12z ; do

 for stats in rmse_spread bss_smpl ; do
  if [ $stats = rmse_spread ] ; then
   score_types='stat_by_level'
   vars='hgt rh tmp ugrd vgrd'
   leads='f6 f12 f18 f24 f30 f36 f42 f48'
  else
   score_types='lead_average'
   vars='700mb_wind_ens_freq_ge15.4 700mb_wind_ens_freq_ge20.58 850mb_tmp_ens_freq_lt273.15 850mb_wind_ens_freq_ge15.4 850mb_wind_ens_freq_ge20.58'
   leads="all"
  fi


 for score_type in $score_types  ; do
  
  if [ $score_type = stat_by_level ] ; then
     scoretype='profile'
  elif [ $score_type = lead_average ] ; then
     scoretype='fhrmean'
  fi
    
   for domain in conus alaska hawaii prico; do

       if [ $domain = conus ] ; then
	    new_domain='buk_conus'
       else
            new_domain=$domain
       fi


    for var in $vars ; do

      if [ $score_type = lead_average  ] ; then
	level=p${var:0:3}
        end=eq0.10000.png

	if [ $var = 700mb_wind_ens_freq_ge15.4 ] ; then
	  var_new='windspeed.ge.30kt.p700'
	elif [ $var = 700mb_wind_ens_freq_ge20.58 ] ; then
	  var_new='windspeed.ge.40kt.p700'
	elif [ $var = 850mb_wind_ens_freq_ge15.4 ] ; then
	  var_new='windspeed.ge.30kt.p850'
        elif [ $var = 850mb_wind_ens_freq_ge20.58 ] ; then
          var_new='windspeed.ge.40kt.p850'	
        elif [ $var = 850mb_tmp_ens_freq_lt273.15 ] ; then
	  var_new='tmp.lt.0C.p850'
	fi
      else
        level=''
	var_new=$var
      fi	

      for lead in $leads ; do
        if [ $lead = f6 ] ; then
           new_lead=f06
        else
          new_lead=$lead
        fi

       if [ ${score_type} = lead_average ] ; then	
	  if [ -s ${score_type}_regional_${domain}_valid_${valid}_${var}_${stats}_${end} ] ; then
             mv ${score_type}_regional_${domain}_valid_${valid}_${var}_${stats}_${end}  evs.href.${stats}.${var_new}.last${past_days}days.${scoretype}_valid_${valid}.${new_domain}.png
          fi 
       else
	  if [ -s ${score_type}_regional_${domain}_valid_${valid}_${var}_${stats}_${lead}.png ] ; then
   	     mv ${score_type}_regional_${domain}_valid_${valid}_${var}_${stats}_${lead}.png  evs.href.${stats}.${var_new}.last${past_days}days.${scoretype}_valid_${valid}_${new_lead}.${new_domain}.png
          fi 
       fi
      done #lead

    done #var
   done  #domain
 done    #score_type
done     #stats
done     #vlaid


tar -cvf evs.plots.href.profile.past${past_days}days.v${VDATE}.tar *.png

# Cat the plotting log files
log_dir="$DATA/logs"
if [ -d $log_dir ]; then
    log_file_count=$(find $log_dir -type f | wc -l)
    if [[ $log_file_count -ne 0 ]]; then
        log_files=("$log_dir"/*)
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                echo "Start: $log_file"
                cat "$log_file"
                echo "End: $log_file"
            fi
        done
    fi
fi


if [ $SENDCOM = YES ] && [ -s evs.plots.href.profile.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.profile.past${past_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.profile.past${past_days}days.v${VDATE}.tar
fi

