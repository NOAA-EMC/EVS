#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the global_ens grid2grid  
#          plotting python script separated by different  validation times
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

export interp_pnts=' '

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


#VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
																  
export fcst_init_hours="0 12"
export fcst_valid_hour="0, 12"

valid_time='valid00z_12z'


export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
mkdir -p $plot_dir


verif_case=$VERIF_CASE


#*****************************************
# Build a POE script to collect sub-tasks
# ****************************************
> run_all_poe.sh

export fcst_valid_hour 

for fcst_init_hour in $fcst_init_hours ; do

  init_time=init${fcst_valid_hour}z

for stats in acc me_mae crpss rmse_spread ets fbias sratio_pod_csi ; do 
 if [ $stats = acc ] ; then
  stat_list='acc'
  line_tp='sal1l2'
  VARs='TMP2m DPT2m UGRD10m VGRD10m'
  score_types='time_series lead_average'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central, Alaska"
 elif [ $stats = me_mae  ] ; then
  stat_list='me, mae'
  line_tp='ecnt'
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
 elif [ $stats = ets ] ; then
  stat_list='ets'
  line_tp='ctc'
  VARs='CAPEsfc'
  score_types='time_series lead_average'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
 elif [ $stats = fbias ] ; then
  stat_list='fbias'
  line_tp='ctc'
  VARs='CAPEsfc'
  score_types='time_series lead_average'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
elif [ $stats = sratio_pod_csi ] ; then
  stat_list='sratio, pod, csi'
  line_tp='ctc'
  VARs='CAPEsfc'
  score_types='performance_diagram'
  VX_MASK_LIST="CONUS, CONUS_East, CONUS_West, CONUS_South, CONUS_Central"
 else
  err_exit "$stats is not a valid metric"
 fi   

 for score_type in $score_types ; do

  if [ $score_type = time_series ] || [ $score_type = performance_diagram ] ; then
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

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = TMP2m ] || [ $VAR = DPT2m ] || [ $VAR = RH2m ] ; then 
          FCST_LEVEL_values="Z2"
       elif [ $VAR = UGRD10m ] || [ $VAR = VGRD10m ] ; then
          FCST_LEVEL_values="Z10"
       elif [ $VAR = CAPEsfc ] ; then
	  FCST_LEVEL_values="L0"
       fi
       
       if [ $VAR = CAPEsfc ] && [ $line_tp = ctc ] ; then
           if [ $score_type = performance_diagram ]; then
               thresh_list='all'
           else
               thresh_list='ge250 ge500 ge1000 ge2000'
           fi
       else
           thresh_list='NA'
       fi

       if [ $VAR = RH2m ] || [ $VAR = CAPEsfc ] ; then
          models='CMCE, GEFS'
       elif [ $VAR = DPT2m ] ; then
          models='ECME, GEFS'
       else
          models='ECME, CMCE, GEFS'
       fi
     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for thresh in $thresh_list ; do 


         #***************************
         # Build sub-task scripts
         #***************************
         > run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh  

        verif_type=conus_sfc

        echo "export PLOT_TYPE=$score_type" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh

        echo "export field=${var}_${level}" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh
        echo "export verif_case=$verif_case" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh
        echo "export verif_type=$verif_type" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh

        echo "export log_level=DEBUG" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh

        echo "export eval_period=TEST" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh


        #if [ $score_type = valid_hour_average ] ; then
        #  echo "export date_type=INIT" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh
        #else
        #  echo "export date_type=VALID" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh
        #fi

	export date_type=INIT

         echo "export var_name=$VAR" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh

         echo "export line_type=$line_tp" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh
         echo "export interp=NEAREST" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh
         echo "export score_py=$score_type" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh

         if [ $VAR = CAPEsfc ] && [ $line_tp = ctc ] ; then
              if [ $score_type = performance_diagram ]; then
                  thresh_fcst='>=250, >=500, >=1000, >=2000'
                  thresh_obs='>=250, >=500, >=1000, >=2000'
              else
	          thresh_fcst=$(echo ${thresh/ge/>=})
	          thresh_obs=$(echo ${thresh/ge/>=})
              fi
	 elif [ $thresh = NA ]; then 
	      thresh_fcst=' '
	      thresh_obs=' '
	 fi

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g" -e "s!interp_pnts!$interp_pnts!g"  $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${fcst_init_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh

         chmod +x  run_py.${fcst_init_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh

         echo "${DATA}/run_py.${fcst_init_hour}.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh" >> run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh


         chmod +x  run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh 
         echo " ${DATA}/run_${fcst_init_hour}_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${thresh}.${line_tp}.sh" >> run_all_poe.sh

      done #end of thresh_list

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done #fcst_init_hour 

chmod +x run_all_poe.sh



#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
#**************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 154 -ppn 77 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
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

for ihr in 00z 12z ; do
    for domain in conus conus_east conus_west conus_south conus_central ; do
        if [ $domain = conus_east ]; then
            evs_graphic_domain="conus_e"
        elif [ $domain = conus_west ]; then
            evs_graphic_domain="conus_w"
        elif [ $domain = conus_south ]; then
            evs_graphic_domain="conus_s"
        elif [ $domain = conus_central ]; then
            evs_graphic_domain="conus_c"
        else
            evs_graphic_domain=$domain
        fi
        for lead in 120 240 360; do
            if [ -f "performance_diagram_regional_${domain}_init_${ihr}_cape_f${lead}__ge250ge500ge1000ge2000.png" ]; then
                mv performance_diagram_regional_${domain}_init_${ihr}_cape_f${lead}__ge250ge500ge1000ge2000.png  evs.global_ens.ctc.cape_l0.last${past_days}days.perfdiag_init${ihr}_f${lead}.g212_buk_${evs_graphic_domain}.png
            fi
        done #lead
    done #domain
done #ihr

for stats in ets fbias ; do
    for ihr in 00z 12z ; do
        for thresh in ge250 ge500 ge1000 ge2000 ; do
            for domain in conus conus_east conus_west conus_south conus_central  ; do
                if [ $domain = conus_east ]; then
                    evs_graphic_domain="conus_e"
                elif [ $domain = conus_west ]; then
                    evs_graphic_domain="conus_w"
                elif [ $domain = conus_south ]; then
                    evs_graphic_domain="conus_s"
                elif [ $domain = conus_central ]; then
                    evs_graphic_domain="conus_c"
                else
                    evs_graphic_domain=$domain
                fi
                if [ -f "lead_average_regional_${domain}_init_${ihr}_cape_${stats}_${thresh}.png" ]; then
                    mv lead_average_regional_${domain}_init_${ihr}_cape_${stats}_${thresh}.png  evs.global_ens.${stats}_${thresh}.cape_l0.last${past_days}days.fhrmean_init${ihr}_f384.g212_buk_${evs_graphic_domain}.png
                fi
                for lead in 120 240 360 ; do
                    if [ -f "time_series_regional_${domain}_init_${ihr}_cape_${stats}_f${lead}_${thresh}.png" ]; then
                        mv time_series_regional_${domain}_init_${ihr}_cape_${stats}_f${lead}_${thresh}.png  evs.global_ens.${stats}_${thresh}.cape_l0.last${past_days}days.timeseries_init${ihr}_f${lead}.g212_buk_${evs_graphic_domain}.png
                    fi
                done #lead
            done #domain
        done #thresh
    done #ihr
done #stats

for ihr in 00z 12z ; do
    for var in tmp dpt ugrd vgrd rh ; do
        if [ $var = tmp ] || [ $var = dpt ] || [ $var = rh ]; then
            levels='2m'
        elif [ $var = ugrd ] || [ $var = vgrd ] ; then
            levels='10m'
        fi
        if [ $var = rh ]; then
            stats_list="me_mae rmse_spread"
        else
            stats_list="acc me_mae crpss rmse_spread"
        fi
        for domain in conus conus_east conus_west conus_south conus_central alaska ; do
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
            if [ $domain = alaska ]; then
                grid="g003"
            else
                grid="g212"
            fi
            for stats in $stats_list ; do
                if [ $stats = rmse_spread ]; then
                    evs_graphic_stats="rmse_sprd"
                else
                    evs_graphic_stats=$stats
                fi
                for level in $levels ; do
                    if [ $level = '2m' ]; then
                        evs_graphic_level='z2'
                    elif [ $level = '10m' ]; then
                        evs_graphic_level='z10'
                    fi
                    if [ -f "lead_average_regional_${domain}_init_${ihr}_${level}_${var}_${stats}.png" ]; then
                        mv lead_average_regional_${domain}_init_${ihr}_${level}_${var}_${stats}.png  evs.global_ens.${evs_graphic_stats}.${var}_${evs_graphic_level}.last${past_days}days.fhrmean_init${ihr}_f384.${grid}_${evs_graphic_domain}.png
                    fi
                    for lead in 120 240 360; do
                        if [ -f "time_series_regional_${domain}_init_${ihr}_${level}_${var}_${stats}_f${lead}.png" ]; then
                            mv time_series_regional_${domain}_init_${ihr}_${level}_${var}_${stats}_f${lead}.png  evs.global_ens.${evs_graphic_stats}.${var}_${evs_graphic_level}.last${past_days}days.timeseries_init${ihr}_f${lead}.${grid}_${evs_graphic_domain}.png
                        fi
                    done #lead
                done #level
            done #stats
        done  #domain
    done     #var
done     #ihr

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}_separate.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    cpreq  evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}_separate.past${past_days}days.v${VDATE}.tar $COMOUT/.
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}_separate.past${past_days}days.v${VDATE}.tar
fi

