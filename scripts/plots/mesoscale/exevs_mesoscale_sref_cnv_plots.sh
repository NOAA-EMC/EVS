#!/bin/ksh
#*******************************************************************************
# Purpose: setup environment, paths, and run the sref cnv (ceiling and visi) 
#           plotting python script
# Last updated: 
#               04/10/2024, Add restart capability, Binbin Zhou Lynker@EMC/NCEP
#               10/27/2023, Add comments,           Binbin Zhou Lynker@EMC/NCEP
#
# ******************************************************************************
set -x 

export PYTHONPATH=$HOMEevs/ush/$COMPONENT:$PYTHONPATH
cd $DATA

export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/GENS_verif_plotting_job.out
mkdir -p $prune_dir
mkdir -p $save_dir
mkdir -p $output_base_dir
mkdir -p $DATA/logs

restart=$COMOUTplots/restart/$past_days/sref_cnv_plots
if [ ! -d  $restart ] ; then
  mkdir -p $restart
fi


export eval_period='TEST'

export interp_pnts=''

export init_end=$VDATE
export valid_end=$VDATE

model_list='GEFS SREF'
          
models='GEFS, SREF'

n=0
while [ $n -le $past_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

#*************************************************************************
# Virtual link the  sref's stat data files of past 90 days
#**************************************************************************
n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/mesoscale/evs_get_sref_stat_file_link_plots.sh $day "$model_list"
  n=$((n+1))
done 


VX_MASK_LIST="CONUS"
																  
export fcst_init_hour="0,3,6,9,12,15,18,21"
export fcst_valid_hour="0,6,12,18"
init_time='init00_to_21z'

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
if [ ! -d $plot_dir ] ; then
 mkdir -p $plot_dir
fi

verif_case=grid2obs
line_type='ctc'
score_types='lead_average threshold_average'
VARS='VISsfc HGTcldceil'

#*****************************************
# Build a POE file to collect sub-jobs
# ****************************************
> run_all_poe.sh

for VAR in $VARS ; do

 if [ $VAR = VISsfc ] ; then
   var_short=vis
 elif [ $VAR = HGTcldceil ] ; then
   var_short=hgt
 fi 

 for stat in  ets fbias; do 
  stat_list=$stat

 for score_type in $score_types ; do

  if [ $score_type = lead_average ] ; then
    valid_times="00 06 12 18"
    if [ $VAR = VISsfc ] ; then
       thresholds="805 1609 4828 8045 16090"
    elif [ $VAR = HGTcldceil ] ; then
       thresholds="152 305 914 1524 3048"
    fi 
    export fcst_group=one_group
  elif [ $score_type = threshold_average ] ; then
    valid_times="00 06 12 18"
    if [ $VAR = VISsfc ] ; then
      thresholds="<805,<1609,<4828,<8045,<16090"
    elif [ $VAR = HGTcldceil ] ; then
      thresholds="<152,<305,<914,<1524,<3048" 
    fi	    
    export fcst_group="group1 group2 group3 group4 group5 group6" 
  fi
 
  for valid_time in $valid_times ; do
 
   for group in $fcst_group ; do	  

     if [ $group = one_group ] ; then	   
       fcst_lead=" 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 81, 84, 87"  
     elif [ $group = group1 ] ; then
       fcst_lead=" 6, 9, 12, 15, 18, 21, 24, 27"
     elif [ $group = group2 ] ; then
       fcst_lead="12, 15, 18, 21, 24, 27, 30, 33, 36, 39"
     elif [ $group = group3 ] ; then
       fcst_lead="24, 27, 30, 33, 36, 39, 42, 45, 48, 51"
     elif [ $group = group4 ] ; then
       fcst_lead="36, 39, 42, 45, 48, 51, 54, 57, 60, 63"
     elif [ $group = group5 ] ; then
       fcst_lead="48, 51, 54, 57, 60, 63, 66, 69, 72, 75"
     elif [ $group = group6 ] ; then
        fcst_lead="60, 63, 66, 69, 72, 75, 78, 81, 84, 87"
     fi

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       FCST_LEVEL_value="L0"

       OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      
 
	for threshold in $thresholds ; do
        
	  if [  $score_type = lead_average ] ; then
	     thresh=$threshold
	  elif [  $score_type = threshold_average ] ; then
	     thresh=all_thresholds
	  fi 

	 #*********************
	 # Build sub-jobs
	 #*********************
         > run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh  

        #*******************************************************************************************************************
        #  Check if this sub-job has been completed in the previous run for restart
	 if [ ! -e $restart/run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.completed ] ; then
        #*******************************************************************************************************************

        verif_type=conus_sfc

        echo "export PLOT_TYPE=$score_type" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

        echo "export field=${var}_${level}" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
        echo "export verif_case=$verif_case" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
        echo "export verif_type=$verif_type" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

        echo "export log_level=DEBUG" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

        echo "export eval_period=TEST" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
        else
          echo "export date_type=VALID" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
        fi


         echo "export var_name=$VAR" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

         echo "export line_type=$line_type" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "export interp=NEAREST" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "export score_py=$score_type" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

	 if [ $score_type = lead_average ] ; then
	  if [ $VAR = VISsfc ] ; then	 
            thresh_fcst="<${threshold}"
          elif [ $VAR = HGTcldceil ] ; then
            thresh_fcst="<${threshold}"
          fi
            thresh_obs=$thresh_fcst
	 elif [ $score_type = threshold_average ] ; then
	    thresh_fcst=${threshold}
	    thresh_obs=$thresh_fcst
	 else
          thresh_fcst=' '
	  thresh_obs=' '
         fi

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$valid_time!g" -e "s!fcst_lead!$fcst_lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/mesoscale/evs_sref_plots_config.sh > run_py.${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

         chmod +x  run_py.${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

         echo "${DATA}/run_py.${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         
         #Save for restart:
         echo "if [ ${score_type} = lead_average ] ; then " >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "  cp ${plot_dir}/${score_type}_regional_conus_valid_${valid_time}z_${var_short}_${stat}_*${thresh}.png $restart/." >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "else" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "  cp ${plot_dir}/${score_type}_regional_conus_valid_${valid_time}z_${var_short}_${stat}_*.png $restart/." >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "fi " >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh
         echo "[[ $? = 0 ]] && >$restart/run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.completed" >> run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh

         chmod +x  run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh 
         echo "${DATA}/run_${VAR}.${stat}.${score_type}.${valid_time}.${group}.${thresh}.sh" >> run_all_poe.sh

      else

         #For restart
	 if [ ${score_type} = lead_average ] ; then 
           cp $restart/${score_type}_regional_conus_valid_${valid_time}z_${var_short}_${stat}_*${thresh}.png ${plot_dir}/.
	 else
           cp $restart/${score_type}_regional_conus_valid_${valid_time}z_${var_short}_${stat}_*.png ${plot_dir}/.
	 fi

      fi

    done # enf of threshold

   done #end of fcst_group

  done #end of valid times 

 done #end of score_type

done #end of stats 

done #end of VAR

chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
# **************************************************************************
if [ $run_mpi = yes ] ; then
  mpiexec -np 176 -ppn 88 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
  export err=$?; err_chk
else
   ${DATA}/run_all_poe.sh
   export err=$?; err_chk
fi

echo "run_all_poe done!"

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for var in vis hgt ; do
   levels=L0
   stats='ets fbias'
   score_types='lead_average threshold_average'
   valid_times="00z 06z 12z 18z"
   unit=''
   if [ $var = vis ] ; then
     var_level=vis_l0
   elif [ $var = hgt ] ; then
     var_level=ceiling_l0
   fi

 for stat in $stats ; do
      	   
  for score_type in $score_types ; do

    for valid in $valid_times ; do

	if [ $score_type = lead_average ] ; then
	  if [ $var = vis ] ; then
             thresholds="lt805 lt1609 lt4828 lt8045 lt16090"
	  elif [ $var = hgt ] ; then
	     thresholds="lt152 lt305 lt914 lt1524 lt3048"    
	  fi 
	  leads="all"
	  scoretype=fhrmean
	else
	  thresholds="all"
          leads="f6-9-12-15-18-21-24-27 f12_to_f39 f24_to_f51 f36_to_f63 f48_to_f75 f60_to_f87"
	  scoretype=threshmean 
        fi

      for lead in $leads ; do 

	  if [ $lead = f6-9-12-15-18-21-24-27 ] ; then
	      new_lead=f06_to_f27
          else
              new_lead=$lead
          fi	      
       for threshold in $thresholds ; do

	   if [ $score_type = lead_average ] ; then
             if [ -s ${score_type}_regional_conus_valid_${valid}_${var}_${stat}_${threshold}.png ] ; then
               mv ${score_type}_regional_conus_valid_${valid}_${var}_${stat}_${threshold}.png  evs.sref.${stat}.${var_level}_${threshold}.last${past_days}days.${scoretype}.valid_${valid}.buk_conus.png
	     fi
           elif [ $score_type = threshold_average ] ; then
             if [ -s ${score_type}_regional_conus_valid_${valid}_${var}_${stat}_${lead}.png ] ; then
               mv ${score_type}_regional_conus_valid_${valid}_${var}_${stat}_${lead}.png  evs.sref.${stat}.${var_level}.last${past_days}days.${scoretype}.valid_${valid}.${new_lead}.buk_conus.png
	     fi
           fi

       done 
    done
   done 
  done  
 done    
done

tar -cvf evs.plots.sref.cnv.past${past_days}days.v${VDATE}.tar *.png


if [ $SENDCOM = YES ] && [ -s evs.plots.sref.cnv.past${past_days}days.v${VDATE}.tar ] ; then
 cp -v evs.plots.sref.cnv.past${past_days}days.v${VDATE}.tar  $COMOUTplots/.  
fi


if [ $SENDDBN = YES ] ; then
     $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUTplots/evs.plots.sref.cnv.past${past_days}days.v${VDATE}.tar
fi






