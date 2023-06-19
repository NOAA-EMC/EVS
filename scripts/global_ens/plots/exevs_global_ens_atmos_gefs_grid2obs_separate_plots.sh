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

export interp_pnts=' '

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


#VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
																  
export fcst_init_hours="0 12"
export fcst_valid_hour="0, 12"

valid_time='valid00z_12z'


export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}


verif_case=$VERIF_CASE

> run_all_poe.sh

export fcst_valid_hour 

for fcst_init_hour in $fcst_init_hours ; do

  init_time=init${fcst_valid_hour}z

for stats in acc bias_mae crpss rmse_spread ets_fbias sratio_pod_csi ; do 
 if [ $stats = acc ] ; then
  stat_list='acc'
  line_tp='sal1l2'
  VARs='TMP2m DPT2m UGRD10m VGRD10m'
  score_types='time_series lead_average'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
 elif [ $stats = bias_mae  ] ; then
  stat_list='bias, mae'
  line_tp='sl1l2'
  VARs='TMP2m DPT2m UGRD10m VGRD10m RH2m'
  score_types='time_series lead_average'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
 elif [ $stats = crpss ] ; then
  stat_list='crpss'
  line_tp='ecnt'
  score_types='time_series lead_average'
  VARs='TMP2m DPT2m UGRD10m VGRD10m'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
 elif [ $stats = rmse_spread  ] ; then
  stat_list='rmse, spread'
  line_tp='ecnt'
  VARs='TMP2m DPT2m UGRD10m VGRD10m RH2m'
  score_types='time_series lead_average'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
 elif [ $stats = ets_fbias ] ; then
  stat_list='ets, fbias'
  line_tp='ctc'
  VARs='CAPEsfc'
  thresh_cape='>=250, >=500, >=1000, >=2000'
  score_types='time_series lead_average'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
elif [ $stats = sratio_pod_csi ] ; then
  stat_list='sratio, pod, csi'
  line_tp='ctc'
  VARs='CAPEsfc'
  thresh_cape='>=250, >=500, >=1000, >=2000'
  score_types='performance_diagram'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
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
       elif [ $VAR = CAPEsfc ] ; then
	  FCST_LEVEL_values="L0"
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

        verif_type=conus_sfc

        echo "export PLOT_TYPE=$score_type" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=$met_v" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


        #if [ $score_type = valid_hour_average ] ; then
        #  echo "export date_type=INIT" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        #else
        #  echo "export date_type=VALID" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
        #fi

	export date_type=INIT

         echo "export var_name=$VAR" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export interp=NEAREST" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         if [ $VAR = CAPEsfc ] && [ $line_type = ctc ] ; then
	      thresh_fcst=$thresh_cape
	      thresh_obs=$thresh_cape
	else
	      thresh_fcst=' '
	      thresh_obs=' '
	fi

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g"  $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${fcst_init_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${fcst_init_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${fcst_init_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh


         chmod +x  run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo " ${DATA}/run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done #fcst_init_hour 

chmod +x run_all_poe.sh


if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 154 -ppn 154 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi


cd $plot_dir

valid_time=valid00_12z

for ihr in 00z 12z ; do
 for domain in conus conus_east conus_west conus_south conus_central ; do
   mv performance_diagram_regional_${domain}_init_${ihr}_cape_f12_to_f384__ge250ge500ge1000ge2000.png  evs.global_ens.ctc.cape.l0.last${past_days}days.perfdiag_${valid_time}_f12_to_f384.buk_${domain}.png
 done
done

for stats in ets_fbias ; do 
 for ihr in 00z 12z ; do
    for score_type in time_series lead_average ; do

      if [ $score_type = time_series ] ; then
        leads='_f120_ge250ge500ge1000ge2000.png  _f240_ge250ge500ge1000ge2000.png  _f360_ge250ge500ge1000ge2000.png'
        scoretype='timeseries'
      elif [ $score_type = lead_average ] ; then
        leads='_ge250ge500ge1000ge2000.png'
        scoretype='fhrmean'
      fi

      for lead in $leads ; do

         if [ $score_type = time_series ] ; then
             lead_time=_${lead:1:4}
         else
             lead_time=_f384
         fi

         for domain in conus conus_east conus_west conus_south conus_central  ; do
           mv ${score_type}_regional_${domain}_init_${ihr}_cape_${stats}${lead}  evs.global_ens.${stats}.cape_l0.last${past_days}days.${scoretype}.init${ihr}.${valid_time}${lead_time}.buk_${domain}.png
         done
       done
    done
  done
done

for ihr in 00z 12z ; do
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
        lead_time=_f384
    fi

    for domain in conus conus_east conus_west conus_south conus_central alaska ; do

     for var in tmp dpt ugrd vgrd rh ; do
      if [ $var = tmp ] || [ $var = dpt ] || [ $var = rh ]; then
	 levels='2m'
      elif [ $var = ugrd ] || [ $var = vgrd ] ; then
	 levels='10m'
      fi

       for level in $levels ; do

        mv ${score_type}_regional_${domain}_init_${ihr}_${level}_${var}_${stats}${lead}  evs.global_ens.${stats}.${var}_${level}.last${past_days}days.${scoretype}.init${ihr}.${valid_time}${lead_time}.buk_${domain}.png
               
      done #level

    done #var
   done  #domain
  done   #lead
 done    #score_type
done     #stats
done     #vhr

#scp *.png wd20bz@emcrzdm:/home/people/emc/www/htdocs/bzhou/evs_plots/gens/grid2obs_init_separate

tar -cvf evs.plots.gefs.grid2obs.v${VDATE}.past${past_days}days.separate.init.00.12.tar *.png

cp  evs.plots.gefs.grid2obs.v${VDATE}.past${past_days}days.separate.init.00.12.tar $COMOUT/.







