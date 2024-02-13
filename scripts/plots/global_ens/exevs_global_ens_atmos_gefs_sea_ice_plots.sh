#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the global_ens sea ice score
#          plotting python script. Only GEFS scores are  in the plots
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

model_list='GEFS'
models='GEFS'

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


VX_MASK_LIST="ARCTIC, ANTARCTIC"
																  
export fcst_init_hour="0"
export fcst_valid_hour="0"
valid_time='valid00z'
init_time='init00z'

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
mkdir -p $plot_dir


verif_case=satellite
verif_type=ghrsst_ncei_avhrr_anl

#*****************************************
# Build a POE script to collect sub-tasks
# ****************************************
> run_all_poe.sh

for stats in rmse me csi sratio_pod_csi ; do 
 if [ $stats = rmse  ] ; then
   stat_list='rmse'
   line_tp='ecnt'
   VARs='ICEC'
   threshes=''
   score_types='time_series lead_average'
 elif [ $stats = me  ] ; then
   stat_list='me'
   line_tp='ecnt'
   VARs='ICEC'
   threshes=''
   score_types='time_series lead_average'
 elif [ $stats = csi  ] ; then
    stat_list='csi'
    line_tp='ctc'	  
    VARs='ICEC_gt10 ICEC_gt40 ICEC_gt80'
    threshes=''
    score_types='time_series lead_average'
 elif [ $stats = sratio_pod_csi ] ; then
    stat_list='sratio, pod, csi'
    line_tp='ctc'
    VARs='ICEC'
    threshes='>10, >40, >80'
    score_types='performance_diagram'
 else
   err_exit "$stats is not a valid metric"
 fi   

 for score_type in $score_types ; do

  if [ $score_type = time_series ] || [ $score_type = performance_diagram ] ; then
    export fcst_leads="24 48 72 96 120 144 168 192 216 240 264 288 312 336 360 384"
  else
    export fcst_leads="vs_lead" 
  fi
 
  for lead in $fcst_leads ; do 

   if [ $lead = vs_lead ] ; then
	export fcst_lead="24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336, 360, 384"
   else
        export fcst_lead=$lead
   fi

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       FCST_LEVEL_values="Z0"

       if [ $VAR = ICEC_gt10 ] ; then
	   threshes='>10'
       elif [ $VAR = ICEC_gt40 ] ; then
           threshes='>40'	       
       elif [ $VAR = ICEC_gt80 ] ; then
           threshes='>80'
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	OBS_LEVEL_value="*,*"

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         #***************************
         # Build sub-task scripts
         #***************************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

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
     
	 thresh_fcst=$threshes
	 thresh_obs=$threshes

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g" -e "s!thresh_obs!$thresh_obs!g"  -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/global_ens/evs_gens_atmos_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

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
   mpiexec -np 32 -ppn 32 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
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

for domain in arctic antarctic ; do
    for lead in 24 48 72 96 120 144 168 192 216 240 264 288 312 336 360 384; do
        lead_new=$(printf "%03d" "${lead}")
        if [ -f "performance_diagram_regional_${domain}_valid_00z_z0_icec_z0_mean_f${lead}__gt10gt40gt80.png" ]; then
            mv performance_diagram_regional_${domain}_valid_00z_z0_icec_z0_mean_f${lead}__gt10gt40gt80.png  evs.global_ens.ctc.icec_z0.last${past_days}days.perfdiag_${valid_time}_f${lead_new}.g003_${domain}.png
        fi
    done #lead
done #domain

for stats in  rmse me csi ; do
    if [ $stats = csi ]; then
        threshs="gt10 gt40 gt80"
    else
        threshs="NA"
    fi
    for thresh in $threshs; do
        if [ $thresh = NA ]; then
            thresh_graphic=""
        else
            thresh_graphic=$(echo "_${thresh}")
        fi
        for domain in arctic antarctic ; do
            if [ -f "lead_average_regional_${domain}_valid_00z_z0_icec_z0_mean_${stats}${thresh_graphic}.png" ]; then
                mv lead_average_regional_${domain}_valid_00z_z0_icec_z0_mean_${stats}${thresh_graphic}.png  evs.global_ens.${stats}${thresh_graphic}.icec_z0.last${past_days}days.fhrmean_valid00z_f384.g003_${domain}.png
            fi
            for lead in 24 48 72 96 120 144 168 192 216 240 264 288 312 336 360 384; do
                lead_new=$(printf "%03d" "${lead}")
                if [ -f "time_series_regional_${domain}_valid_00z_z0_icec_z0_mean_${stats}_f${lead}${thresh_graphic}.png" ]; then
                    mv time_series_regional_${domain}_valid_00z_z0_icec_z0_mean_${stats}_f${lead}${thresh_graphic}.png  evs.global_ens.${stats}${thresh_graphic}.icec_z0.last${past_days}days.timeseries_valid00z_f${lead_new}.g003_${domain}.png
                fi
            done #lead
        done #domain
    done  #thresh
done     #stats

tar -cvf evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ]; then
    if [ -s evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar ]; then
        cp -v evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar  $COMOUT/.
    fi
fi

if [ $SENDDBN = YES ]; then 
    $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.${COMPONENT}.${RUN}.${MODELNAME}.${VERIF_CASE}.past${past_days}days.v${VDATE}.tar
fi

