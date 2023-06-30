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
export fcst_valid_hour="0,3,6,9,12,15,18,21,24"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}

export fcst_init_hour="0,6,12,18"
export fcst_valid_hour="0,3,6,9,12,15,18,21"
valid_time='valid00z_03z_06z_09z_12z_15z_18z_21z'
init_time='init00z_06z_12z_18z'

verif_case=grid2obs

> run_all_poe.sh

for stats in csi_fbias ets_fbias ratio_pod_csi ; do 
 if [ $stats = csi_fbias ] ; then
    stat_list='csi, fbias'
    line_tp='ctc'
    VARs='VISsfc HGTcldceil CAPEsfc MLCAPE'
    score_types='lead_average threshold_average'
 elif [ $stats = ets_fbias ] ; then
    stat_list='ets, fbias'
    line_tp='ctc'
    VARs='TCDC'
    score_types='lead_average threshold_average'
 elif [ $stats = ratio_pod_csi ] ; then
    stat_list='sratio, pod, csi'
    line_tp='ctc'
    VARs='VISsfc HGTcldceil CAPEsfc TCDC MLCAPE'
    score_types='performance_diagram'   
 else
  echo $stats is wrong stat
  exit
 fi   

 for score_type in $score_types ; do

  export fcst_leads="6,9,12,15,18,21,24,27,30,33,36,39,42,45,48"

  for lead in $fcst_leads ; do 

    for VAR in $VARs ; do 

       var=`echo $VAR | tr '[A-Z]' '[a-z]'` 
	    
       if [ $VAR = CAPEsfc ] || [ $VAR = VISsfc ] || [ $VAR = HGTcldceil ] || [ $VAR = TCDC ] ; then
          FCST_LEVEL_values="L0"
       elif [ $VAR = MLCAPE ] ; then
	  FCST_LEVEL_values="ML"
       fi 	  

       if [ $VAR = CAPEsfc ] || [ $VAR = MLCAPE ] ; then 
	   doms="dom1 dom2 dom3 dom4 dom5"
       else
	   doms="dom1 dom2 dom3 dom4 dome5 dom6 dom7 dom8"
       fi 

       for dom in $doms ; do 

       if [ $VAR = CAPEsfc ] || [ $VAR = MLCAPE ] ; then

	 if [ $dom = dom1 ] ; then      
             VX_MASK_LIST="CONUS, CONUS_East, CONUS_West"
	 elif [ $dom = dom2 ] ; then
	      VX_MASK_LIST="CONUS_South, CONUS_Central,  Appalachia"
	 elif [ $dom = dom3 ] ; then
	      VX_MASK_LIST="DeepSouth, GreatBasin, Mezquital"
	 elif [ $dom = dom4 ] ; then
	      VX_MASK_LIST="MidAtlantic,  PacificNW"
	 elif [ $dom = dom4 ] ; then
              VX_MASK_LIST="Southeast, SPlains"
	 fi
       else
	 if [ $dom = dom1 ] ; then
            VX_MASK_LIST="CONUS, CONUS_East, CONUS_West"
         elif [ $dom = dom2 ] ; then
	    VX_MASK_LIST="CONUS_South, CONUS_Central, Alaska"
         elif [ $dom = dom3 ] ; then
	    VX_MASK_LIST="Appalachia, CPlains, DeepSouth"
         elif [ $dom = dom4 ] ; then
	    VX_MASK_LIST="GreatBasin, GreatLakes, Mezquital"
	 elif [ $dom = dom5 ] ; then
	    VX_MASK_LIST="MidAtlantic, NorthAtlantic, NPlains"
	 elif [ $dom = dom6 ] ; then
            VX_MASK_LIST="NRockies, PacificNW, PacificSW" 
	 elif [ $dom = dom7 ] ; then
            VX_MASK_LIST="SRockies, Prairie, Southeast"
	 elif [ $dom = dom8 ] ; then
            VX_MASK_LIST="Southwest, SPlains"
	 fi
       fi

     for FCST_LEVEL_value in $FCST_LEVEL_values ; do 

        OBS_LEVEL_value=$FCST_LEVEL_value

        level=`echo $FCST_LEVEL_value | tr '[A-Z]' '[a-z]'`      

      for line_type in $line_tp ; do 

         > run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh  

        verif_type=conus_sfc

        echo "export PLOT_TYPE=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export field=${var}_${level}" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export vx_mask_list='$VX_MASK_LIST'" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_case=$verif_case" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export verif_type=$verif_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export log_level=DEBUG" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        echo "export met_ver=$met_v" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

        echo "export eval_period=TEST" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh


        if [ $score_type = valid_hour_average ] ; then
          echo "export date_type=INIT" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        else
          echo "export date_type=VALID" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
        fi


         echo "export var_name=$VAR" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export fcts_level=$FCST_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export obs_level=$OBS_LEVEL_value" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         echo "export line_type=$line_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export interp=NEAREST" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh
         echo "export score_py=$score_type" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

	 if [ $VAR = CAPEsfc ] || [ $VAR = MLCAPE ] ; then
           thresh_fcst='>=250, >=500, >=1000, >=2000'
	 elif [ $VAR = VISsfc  ] ; then
           thresh_fcst='<805, <1609, <4828, <8045, <16090'
         elif [ $VAR = HGTcldceil  ] ; then
            thresh_fcst='<152, <305, <914, <1524, <3048'
	 elif [ $VAR = TCDC ] ; then
	    #Binbin Note: can not set threshold operands '<' and '>=' together in the threshold list
            #thresh_fcst='<10, >=10, >=50, >=90'		 
            thresh_fcst='>=10, >=50, >=90'		 
         fi	    
	 thresh_obs=$thresh_fcst

         sed -e "s!model_list!$models!g" -e "s!stat_list!$stat_list!g"  -e "s!thresh_fcst!$thresh_fcst!g"  -e "s!thresh_obs!$thresh_obs!g"   -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$lead!g"  -e "s!interp_pnts!$interp_pnts!g" $USHevs/cam/evs_href_plots_config.sh > run_py.${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_py.${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         echo "${DATA}/run_py.${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh" >> run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh

         chmod +x  run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh 
         echo "${DATA}/run_${stats}.${score_type}.${lead}.${VAR}.${dom}.${FCST_LEVEL_value}.${line_type}.sh" >> run_all_poe.sh

      done #end of line_type

     done #end of FCST_LEVEL_value

    done #end of VAR

  done #end of fcst_lead

 done #end of dom 

 done #end of score_type

done #end of stats 

chmod +x run_all_poe.sh


if [ $run_mpi = yes ] ; then
  export LD_LIBRARY_PATH=/apps/dev/pmi-fix:$LD_LIBRARY_PATH
   mpiexec -np 102 -ppn 102 --cpu-bind verbose,depth cfp ${DATA}/run_all_poe.sh
else
  ${DATA}/run_all_poe.sh
fi

cd $plot_dir

for domain in conus conus_east conus_west conus_south conus_central alaska  appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nolains nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

 for var in vis hgt cape mlcape tcdc ; do
  if [ $var = vis ] ; then
    var_new=$var
    level=l0
    valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
  elif [ $var = hgt ] ; then
    var_new=ceiling
    level=l0
    valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
  elif [ $var = cape ] ; then
    var_new=cape
    level=l0
    valid=valid_00z_12z
  elif [ $var = mlcape ] ; then
    var_new=mlcape 
    level=ml
    valid=valid_00z_12z     
  elif [ $var = tcdc ] ; then
    var_new_tatal_cloud
    level=l0
    valid=valid_00z_03z_06z_09z_12z_15z_18z_21z
  fi

  mv performance_diagram_regional_${domain}_valid*_${var}_*.png evs.href.ctc.${var_new}_${level}.last${past_days}days.perfdiag.${valid}.buk_${domain}.png

 done
done

 	
for score_type in lead_average threshold_average; do

  for var in vis hgt cape tcdc mlcape ; do
   if [ $var = vis ] ; then
       var_new=$var
       level=l0
       stats="csi_fbias csi fbias"
   elif [ $var = hgt ] ; then
       var_new=ceiling
       level=l0
       stats="csi_fbias csi fbias"
   elif [ $var = cape ] ; then
       var_new=cape
       level=l0
       stats="csi_fbias  csi fbias"
   elif [ $var = mlcape ] ; then
       var_new=mlcape
       level=ml
       stats="csi_fbias csi fbias"
   elif [ $var = tcdc ] ; then
       var_new=tatal_cloud
       level=l0
       stats="ets_fbias ets fbias" 
   fi
   
   valid="valid_available_times"

  if [ $score_type = lead_average ] ; then
     scoretype=fhrmean
  elif [ $score_type = threshold_average ] ; then
     scoretype=thresholdmean
  fi 

  for stat in $stats ; do

    for domain in conus conus_east conus_west conus_south conus_central alaska appalachia cplains deepsouth greatbasin greatlakes mezquital midatlantic northatlantic nolains nrockies pacificnw pacificsw prairie southeast southwest splains nplains srockies ; do

     mv ${score_type}_regional_${domain}_valid*_${var}_${stat}*.png evs.href.${stat}.${var_new}_${level}.last${past_days}days.${scoretype}.${valid}.buk_${domain}.png

       done #domain
    done #stat
  done  #var
done    #score_type

tar -cvf evs.plots.href.grid2obs.ctc.past${past_days}days.v${VDATE}.tar *.png

cp  evs.plots.href.grid2obs.ctc.past${past_days}days.v${VDATE}.tar  $COMOUT/.  

















