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

model_list='HREF_MEAN HREF_AVRG HREF_LPMM HREF_PMMN'
models='HREF_MEAN,  HREF_AVRG, HREF_LPMM, HREF_PMMN'

VX_MASK_LISTs='CONUS CONUS_East CONUS_West CONUS_South CONUS_Central Alaska'

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


export plot_dir=$DATA/out/precip/${valid_beg}-${valid_end}

verif_case=precip
verif_type=ccpa

> run_all_poe.sh

for VX_MASK_LIST in $VX_MASK_LISTs ; do
 	
for stats in ets_fbias ratio_pod_csi fss ; do 
 if [ $stats = ets_fbias ] ; then
    stat_list='ets, fbias'
    line_tp='ctc'
    VARs='APCP_01 APCP_03 APCP_24'
    interp_pnts=''
    score_types='threshold_average '
 elif [ $stats = ratio_pod_csi ] ; then
    stat_list='sratio, pod, csi'
    line_tp='ctc'
    VARs='APCP_01 APCP_03 APCP_24'
    interp_pnts=''
    score_types='performance_diagram'
 elif [ $stats = fss ] ; then
    stat_list='fss'
    line_tp='nbrcnt'
    VARs='APCP_01 APCP_03 APCP_24'    
    interp_pnts='1,9,25,49,91,121'
    score_types='threshold_average' 
 else
  echo $stats is wrong stat
  exit
 fi   

 for score_type in $score_types ; do

  for VAR in $VARs ; do
 
   if [ $VAR = APCP_01 ] ; then
	#export fcst_leads='3,6,9,12,15,18,21,24'
	export fcst_leads='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24'
	export fcst_valid_hour='0,3,6,9,12,15,18,21'
	#export fcst_valid_hour='0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23'
	FCST_LEVEL_values=A01
   elif [ $VAR = APCP_03 ] ; then
         export fcst_leads='3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48'
	 export fcst_valid_hour='0,3,6,9,12,15,18,21'
	 FCST_LEVEL_values=A03
   elif [ $VAR = APCP_24 ] ; then
         export fcst_leads='24,30,36,42,48'
	 export fcst_valid_hour='12'
	 FCST_LEVEL_values=A24
   fi

  for lead in $fcst_leads ; do 

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

	if [ $VX_MASK_LIST = Alaska ] ; then
          OBS_LEVEL_value=L0
	else
          OBS_LEVEL_value=$FCST_LEVEL_value
        fi

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh  

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        echo "export met_ver=$met_v" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

	 if [ $stats = fss ] ; then
	   
	   echo "export interp=NBRHD_SQUARE" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
         else	   
           echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
	 fi

         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh
 
	 if [ $VAR = APCP_01 ] ; then
           thresh_fcst='>=0.254, >=2.54, >=6.35, >=12.7, >=25.4'
         elif [ $VAR = APCP_03 ] ; then
           thresh_fcst='>=2.54, >=6.35, >=12.7, >=25.4, >=50.8'
         elif [ $VAR = APCP_24 ] ; then
           thresh_fcst='>=12.7, >=25.4, >=50.8, >=76.2'
	 fi
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${FCST_LEVEL_value}.${line_type}.${VX_MASK_LIST}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of score_type

done #end of stats 

done #end of vx_mask_list
chmod +x run_all_poe.sh


if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 54 -ppn 54 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi


cd $plot_dir

for stats in ets fbias fss ; do
  score_type='threshold_average' 
  scoretype='thresholdmean'

  for var in apcp_01 apcp_03 apcp_24 ; do
    level=${var:5:2}h
    if [ $stats = fss ] ; then 
       if [ $var = apcp_01 ] ; then
        valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
        lead=width1-3-5-7-9-11_f1_to_f24
       elif [ $var = apcp_03 ] ; then
        valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
        lead=width1-3-5-7-9-11_f3_to_f48
       elif [ $var = apcp_24 ] ; then
               valid=valid_12z
        lead=width1-3-5-7-9-11_f24-30-36-42-48
       fi	
    else	    
      if [ $var = apcp_01 ] ; then
	valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
        lead=f1_to_f24
      elif [ $var = apcp_03 ] ; then
        valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
        lead=f3_to_f48
      elif [ $var = apcp_24 ] ; then
        valid=valid_12z
        lead=f24-30-36-42-48
      fi
    fi

   for domain in conus conus_east conus_west conus_south conus_central alaska  ; do
      mv ${score_type}_regional_${domain}_${valid}_${level}_${var}_${stats}_${lead}.png  evs.href.${stats}.${var}h.last${past_days}days.${scoretype}.buk_${domain}.png
   done

 done
done


score_type='performance_diagram'  
scoretype='perfdiag'

for var in apcp_01 apcp_03 apcp_24 ; do
    level=${var:5:2}h
    if [ $var = apcp_01 ] ; then
	valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
        lead=f1_to_f24__ge0.254ge2.54ge6.35ge12.7ge25.4
    elif [ $var = apcp_03 ] ; then
        valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
        lead=f3_to_f48__ge2.54ge6.35ge12.7ge25.4ge50.8
    elif [ $var = apcp_24 ] ; then
        valid=valid_12z
        lead=f24-30-36-42-48__ge12.7ge25.4ge50.8ge76.2
    fi

   for domain in conus conus_east conus_west conus_south conus_central alaska  ; do
      mv ${score_type}_regional_${domain}_${valid}_${level}_${var}_${lead}.png  evs.href.ctc.${var}h.last${past_days}days.${scoretype}.buk_${domain}.png
   done

done


tar -cvf evs.plots.href.precip.past${past_days}days.v${VDATE}.tar *.png

cp evs.plots.href.precip.past${past_days}days.v${VDATE}.tar  $COMOUT/.  

















