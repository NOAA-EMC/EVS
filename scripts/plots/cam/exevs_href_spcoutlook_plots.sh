#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href spcoutlook plotting python 
#          script
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

model_list='HREF_MEAN'
models='HREF_MEAN'

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
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day HREF_MEAN
  n=$((n+1))
done 
																  
export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,12"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}

export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,12"
valid_time='valid00z_12z'
init_time='init00z_06z_12z_18z'

verif_case=grid2obs

#********************************************
# Total SPC outlook area masks = 6 x 3 = 18
#********************************************
VX_MASK_LIST="DAY1_MRGL,  DAY2_MRGL, DAY3_MRGL, DAY1_TSTM,  DAY2_TSTM, DAY3_TSTM,  DAY1_SLGT,  DAY2_SLGT, DAY3_SLGT, DAY1_ENH,  DAY2_ENH, DAY3_ENH, DAY1_MDT,  DAY2_MDT, DAY3_MDT, DAY1_HIGH,  DAY2_HIGH, DAY3_HIGH"

#*********************************************
# Build a POE file to collect sub-jobs
# ********************************************
> run_all_poe.sh

for stats in csi_fbias ratio_pod_csi ; do 
 if [ $stats = csi_fbias ] ; then
    stat_list='csi, fbias'
    line_tp='ctc'
    VARs='CAPEsfc MLCAPE'
    score_types='lead_average threshold_average'
 elif [ $stats = ratio_pod_csi ] ; then
    stat_list='sratio, pod, csi'
    line_tp='ctc'
    VARs='CAPEsfc MLCAPE'
    score_types='performance_diagram'   
 else
  err_exit "$stats is not a valid stat"
 fi   

 for score_type in $score_types ; do

  #no space between fcst_lead hour, so take it as one string! 	 
  export fcst_leads="6,12,15,24,30,36,42,48"

  for lead in $fcst_leads ; do 

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = CAPEsfc ] ; then
          FCST_LEVEL_values="L0"
       elif [ $VAR = MLCAPE ] ; then
	  FCST_LEVEL_values="ML"
       fi 	  

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

        OBS_LEVEL_value=$FCST_LEVEL_value

      for line_type in $line_tp ; do 

	 #****************************
	 #  Build sub-jobs
	 #****************************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh  

        verif_type=conus_sfc

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
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
         echo "export interp=BILIN" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         thresh_fcst='>=250, >=500, >=1000, >=2000'
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

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
   mpiexec -np 6 -ppn 6 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi
export err=$?; err_chk

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************

cd $plot_dir

for domain in day1_mrgl day1_slgt day1_tstm day1_enh day1_mdt day1_high day2_mrgl day2_slgt day2_tstm day2_enh day2_mdt day2_high day3_mrgl day3_slgt day3_tstm day3_enh day3_mdt day3_high ; do
 for var in cape mlcape ; do
  if [ $var = cape ] ; then
    var_new=cape
    level=l0
    valid=valid_00z_12z
  elif [ $var = mlcape ] ; then
    var_new=mlcape
    level=ml
    valid=valid_00z_12z
  fi
  if ls lead_average_regional_${domain}_valid_all_times_${var}*.png 1> /dev/null 2>&1; then
     mv lead_average_regional_${domain}_valid_all_times_${var}*.png  evs.href.csi_fbias.${var_new}_${level}.last${past_days}days.fhrmean_${valid}.${domain}.png
  fi
  if ls threshold_average_regional_${domain}_${valid}_${var}_csi*.png 1> /dev/null 2>&1; then
     mv threshold_average_regional_${domain}_${valid}_${var}_csi*.png  evs.href.csi.${var_new}_${level}.last${past_days}days.threshmean_${valid}.${domain}.png
  fi
  if ls threshold_average_regional_${domain}_${valid}_${var}_fbias*.png 1> /dev/null 2>&1; then
     mv threshold_average_regional_${domain}_${valid}_${var}_fbias*.png  evs.href.fbias.${var_new}_${level}.last${past_days}days.threshmean_${valid}.${domain}.png
  fi
  if ls performance_diagram_regional_${domain}_${valid}_${var}*.png 1> /dev/null 2>&1; then
     mv performance_diagram_regional_${domain}_${valid}_${var}*.png evs.href.ctc.${var_new}_${level}.last${past_days}days.perfdiag_${valid}.${domain}.png
  fi

 done
done
 	

tar -cvf evs.plots.href.spcoutlook.past${past_days}days.v${VDATE}.tar *.png

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


if [ $SENDCOM = YES ] && [ -s evs.plots.href.spcoutlook.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.spcoutlook.past${past_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
   $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.spcoutlook.past${past_days}days.v${VDATE}.tar
fi















