#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the href spcoutlook plotting python 
#          script
# Last updated: 
#               01/10/2025, add MPMD, by Binbin Zhou Lynker@EMC/NCEP
#               07/09/2024, add restart, by Binbin Zhou Lynker@EMC/NCEP
#               05/30/2025, Binbin Zhou Lynker@EMC/NCEP
#******************************************************************************
set -x 

mkdir -p $DATA/scripts
cd $DATA/scripts

export machine=${machine:-"WCOSS2"}
export output_base_dir=$DATA/stat_archive
mkdir -p $output_base_dir

all_plots=$DATA/plots/all_plots
mkdir -p $all_plots
if [ $SENDCOM = YES ] ; then
 restart=$COMOUT/restart/$last_days/href_spcoutlook_plots
 if [ ! -d  $restart ] ; then
  mkdir -p $restart
 fi
fi

export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='HREF_MEAN'
models='HREF_MEAN'

n=0
while [ $n -le $last_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

#*************************************************************
# Virtual link the href's stat data files of last 31/90 days
#*************************************************************
n=0
while [ $n -le $last_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/cam/evs_get_href_stat_file_link_plots.sh $day HREF_MEAN
  n=$((n+1))
done 
																  
export fcst_init_hour="0,6,12,18"
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
	  var_rst=cape
       elif [ $VAR = MLCAPE ] ; then
	  FCST_LEVEL_values="ML"
	  var_rst=mlcape
       fi 	  

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

        OBS_LEVEL_value=$FCST_LEVEL_value

      for line_type in $line_tp ; do 

       for valid_time in 00 12 ; do

	 #****************************
	 #  Build sub-jobs
	 #****************************
         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh  
       #***********************************************************************************************************************************
       #  Check if this sub-job has been completed in the previous run for restart
       if [ ! -e $restart/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.completed ] ; then
       #***********************************************************************************************************************************

        verif_type=conus_sfc

	echo "#!/bin/ksh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	echo "set -x" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
        save_dir=$DATA/plots/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}
	plot_dir=$save_dir/sfc_upper/${valid_beg}-${valid_end}
	mkdir -p $plot_dir
	mkdir -p $save_dir/data

        echo "export save_dir=$save_dir" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	echo "export log_metplus=$save_dir/log_verif_plotting_job.out" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	echo "export prune_dir=$save_dir/data" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

	if [ $score_type = lead_average ] ; then
	  echo "export PLOT_TYPE=lead_average_valid " >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	else
	  echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
        fi

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
         echo "export interp=BILIN" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

         thresh_fcst='>=250, >=500, >=1000, >=2000'
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$valid_time!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

	 echo "${DATA}/scripts/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

         echo "if [ -s ${plot_dir}/${score_type}_regional_*_valid_${valid_time}z_${var_rst}*.png ] ; then" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	 echo "  cp -v ${plot_dir}/${score_type}_regional_*_valid_${valid_time}z_${var_rst}*.png $all_plots" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	 echo "  echo completed >${plot_dir}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.completed" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
        
	 #Copy files to restart directory
	 echo "  if [ $SENDCOM = YES ] ; then" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	 echo "    cp -v $all_plots/${score_type}_regional_*_valid_${valid_time}z_${var_rst}*.png $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh       
	 echo "    cp -v ${plot_dir}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.completed $restart" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	 echo "  fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh
	 echo "fi" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh 
         echo "${DATA}/scripts/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${valid_time}.sh" >> run_all_poe.sh

        else 
          cp -v ${restart}/${score_type}_regional_*_valid_${valid_time}z_${var_rst}*.png $all_plots

       fi

       done #end of valid time

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
mpiexec -np 6 -ppn 6 --cpu-bind verbose,depth cfp ${DATA}/scripts/run_all_poe.sh
export err=$?; err_chk


#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $all_plots

for domain in day1_mrgl day1_slgt day1_tstm day1_enh day1_mdt day1_high day2_mrgl day2_slgt day2_tstm day2_enh day2_mdt day2_high day3_mrgl day3_slgt day3_tstm day3_enh day3_mdt day3_high ; do
 for var in cape mlcape ; do
  if [ $var = cape ] ; then
    var_new=cape
    level=l0
  elif [ $var = mlcape ] ; then
    var_new=mlcape
    level=ml
  fi

  for valid in 00z 12z ; do 
  if ls lead_average_regional_${domain}_valid_${valid}_${var}*.png 1> /dev/null 2>&1; then
     mv lead_average_regional_${domain}_valid_${valid}_${var}*.png  evs.href.csi_fbias.${var_new}_${level}.last${last_days}days.fhrmean_valid${valid}.${domain}.png
  fi
  if ls threshold_average_regional_${domain}_valid_${valid}_${var}_csi*.png 1> /dev/null 2>&1; then
     mv threshold_average_regional_${domain}_valid_${valid}_${var}_csi*.png  evs.href.csi.${var_new}_${level}.last${last_days}days.threshmean_valid${valid}.${domain}.png
  fi
  if ls threshold_average_regional_${domain}_valid_${valid}_${var}_fbias*.png 1> /dev/null 2>&1; then
     mv threshold_average_regional_${domain}_valid_${valid}_${var}_fbias*.png  evs.href.fbias.${var_new}_${level}.last${last_days}days.threshmean_valid${valid}.${domain}.png
  fi
  if ls performance_diagram_regional_${domain}_valid_${valid}_${var}*.png 1> /dev/null 2>&1; then
     mv performance_diagram_regional_${domain}_valid_${valid}_${var}*.png evs.href.ctc.${var_new}_${level}.last${last_days}days.perfdiag_valid${valid}.${domain}.png
  fi

  done
 done
done
 	
if [ -s evs*.png ] ; then
  tar -cvf evs.plots.href.spcoutlook.last${last_days}days.v${VDATE}.tar evs*.png
fi

# Cat the plotting log files
log_dir="$DATA/plots"
if [ -s $log_dir/*/log*.out ]; then
  log_files=`ls $log_dir/*/log*.out`
  for log_file in $log_files ; do
     echo "Start: $log_file"
     cat  "$log_file"
     echo "End: $log_file"
  done  
fi


if [ $SENDCOM = YES ] && [ -s evs.plots.href.spcoutlook.last${last_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.href.spcoutlook.last${last_days}days.v${VDATE}.tar  $COMOUT/.  
fi

if [ $SENDDBN = YES ] ; then
   $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.href.spcoutlook.last${last_days}days.v${VDATE}.tar
fi















