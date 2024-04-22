#!/bin/ksh
#################################################################################
# Purpose: setup environment, paths, and run the narre ploting python script
# Last updated: 04/01/2024, Add restart capability, Binbin Zhou Lynker@EMC/NCEP
#               After a sub-task file is create, first check if it has been done
#               in the previous (see its .completed file exists or not)
#               If it has been done before, then skip further building this 
#               sub-task, so that this sub-task file name is 0 size in the
#               working directory
#
#               10/27/2023, Binbin Zhou Lynker@EMC/NCEP
##################################################################################
set -x 

cd $DATA

export prune_dir=$DATA/data
export save_dir=$DATA/out
export output_base_dir=$DATA/stat_archive
export log_metplus=$DATA/logs/NARRE_verif_plotting_job.out
mkdir -p $prune_dir
mkdir -p $save_dir
mkdir -p $output_base_dir
mkdir -p $DATA/logs

if [ ! -d  $COMOUT/restart/$past_days ] ; then
  mkdir -p $COMOUT/restart/$past_days
fi

export eval_period='TEST'
#export past_days=0

export init_end=$VDATE
export valid_end=$VDATE

n=0
while [ $n -le $past_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

#*************************************************************************
# Virtual link the  narre's stat data files of past days (31 or 90 days)
#**************************************************************************
n=0
while [ $n -le $past_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/narre/evs_get_narre_stat_file_link.sh $day
  n=$((n+1))
done 

VX_MASK_LIST="G130 G242"

export fcst_valid_hour="0,3,6,9,12,15,18,21"
export fcst_lead="1,2,3,4,5,6,7,8,9,10,11,12"

export plot_dir=$DATA/out/sfc_upper/${valid_beg}-${valid_end}
mkdir -p ${plot_dir}

#*****************************************
# Build a POE file to collect sub-jobs
# **************************************** 
> run_all_poe.sh 
for grid in $VX_MASK_LIST ; do

 #for score_type in performance_diagram  threshold_average time_series valid_hour_average lead_average ; do
 for score_type in performance_diagram ; do

  for var in VISsfc HGTcldceil ; do 

   #for line_type in ctc sl1l2 ; do 
   for line_type in ctc ; do 

    #*****************************************************************************
    # Build sub-jobs and setup environment for running the python plotting scripts
    # ****************************************************************************
    > run_narre_${grid}.${score_type}.${var}.${line_type}.sh 

  if [ $grid = G130 ] ; then
    export grd=g130
  elif [ $grid = G242 ] ; then
    export grd=g242
  fi

  #**********************************************************************************************
  # Check if this sub-job has been completed in the previous run for restart
   if [ ! -e $COMOUT/restart/$past_days/run_narre_${grid}.${score_type}.${var}.${line_type}.completed ] ; then
  #************************************************************************************************

    if [ $grid = G130 ] ; then
      echo "export mask=buk_conus" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      #echo "export grd=g130"  >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      #grd=g130
    elif [ $grid = G242 ] ; then
      echo "export mask=alaska" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      #echo "export grd=g242"  >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      #grd=g242
    fi

      echo "export PLOT_TYPE=$score_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

    if [ $var = VISsfc ] ; then
      echo "export field=vis_l0" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      echo "export vname=vis" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
    elif [ $var = HGTcldceil ] ; then
      echo "export field=ceiling_l0" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
      echo "export vname=hgt" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
    fi


     if [ $var = VISsfc  ] || [ $var = HGTcldceil ] || [ $var = TCDC ] ; then
      FCST_LEVEL_value="L0"
      OBS_LEVEL_value="L0"
     elif [ $var = TMP2m ] || [ $var = RH2m ] || [ $var = DPT2m ] ; then
      FCST_LEVEL_value="Z2"
      OBS_LEVEL_value="Z2"
     elif [ $var = UGRD10m ] || [ $var = VGRD10m ] ; then
      FCST_LEVEL_value="Z10"
      OBS_LEVEL_value="Z10"
     elif [ $var = CAPEsfc ] ; then
      FCST_LEVEL_value="L0"
      OBS_LEVEL_value="L100000-0"
     elif [ $var = PRMSL ] ; then
      FCST_LEVEL_value="Z0"
      OBS_LEVEL_value="Z0"
     fi

     if [ $line_type = ctc ] ; then
       if [ $score_type = performance_diagram ] ; then
         stat_list="sratio, pod, csi"
       else
         stat_list="csi"
       fi
     elif [ $line_type = sl1l2 ] ; then
       stat_list="rmse, bias"
     fi

     if [ $var = VISsfc  ] ; then
      thresh="<805,<1609,<4828,<8045,<16090"
     elif [ $var = HGTcldceil ] ; then
      thresh="<152,<305,<914,<1524,<3048"
     fi

     echo "export vx_mask_list=$grid" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export verif_case=grid2obs" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export verif_type=conus_sfc" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

     echo "export log_level=INFO" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export model=NARRE_MEAN" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

     echo "export eval_period=TEST" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

     if [ $score_type = valid_hour_average ] ; then
       echo "export date_type=INIT" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     else
       echo "export date_type=VALID" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     fi

     echo "export var_name=$var" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export fcts_level=$FCST_LEVEL_value" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export obs_level=$OBS_LEVEL_value" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh


     echo "export line_type=$line_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export interp=NEAREST" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "export score_py=$score_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh

     sed -e "s!stat_list!$stat_list!g"  -e "s!thresh_list!$thresh!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$fcst_valid_hour!g" -e "s!fcst_lead!$fcst_lead!g"  $USHevs/narre/evs_narre_plots.sh > run_py.${var}_${line_type}.${score_type}.${grid}.sh

     chmod +x run_py.${var}_${line_type}.${score_type}.${grid}.sh

     echo "${DATA}/run_py.${var}_${line_type}.${score_type}.${grid}.sh" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
 
     #For restart
     echo "cp ${plot_dir}/${score_type}_regional_${grd}_valid_*${vname}_*.png  $COMOUT/restart/$past_days/." >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo ">$COMOUT/restart/$past_days/run_narre_${grid}.${score_type}.${var}.${line_type}.completed" >> run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     
     chmod +x run_narre_${grid}.${score_type}.${var}.${line_type}.sh
     echo "${DATA}/run_narre_${grid}.${score_type}.${var}.${line_type}.sh" >> run_all_poe.sh

    else

      #For restart
      cp $COMOUT/restart/$past_days/${score_type}_regional_${grd}_*${vname}_*.png ${plot_dir}/.

    fi      

    done #end of line_type

  done #end of var

 done #end of score_type

done #end of grid 

chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
# **************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 8 -ppn 8 --cpu-bind verbose,core cfp ${DATA}/run_all_poe.sh
   export err=$?; err_chk
else
  ${DATA}/run_all_poe.sh
  export err=$?; err_chk
fi


#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $plot_dir

for grid in g130 g242 ; do 
  if [ $grid = g130 ] ; then
   domain=buk_conus
  elif [ $grid = g242 ] ; then
   domain=alaska  
  fi

  for var in vis hgt ; do
    if [ $var = vis ] ; then
	  field=vis_l0
	  thrsh=_lt805lt1609lt4828lt8045lt16090
    elif [ $var = hgt ] ; then
          field=ceiling_l0
	  thrsh=_lt152lt305lt914lt1524lt3048
    fi	  
    if [ -s performance_diagram_regional_${grid}_valid_00z_03z_06z_09z_12z_15z_18z_21z_${var}_f1_to_f12_${thrsh}.png ] ; then
      cp  performance_diagram_regional_${grid}_valid_00z_03z_06z_09z_12z_15z_18z_21z_${var}_f1_to_f12_${thrsh}.png evs.narre.ctc.${field}.last${past_days}days.perfdiag_valid_all_times.${domain}.png
    fi 
  done
done

tar -cvf evs.plots.narre.grid2obs.last${past_days}days.v${VDATE}.tar *.png

if [ $SENDCOM = YES ] && [ -s evs.plots.narre.grid2obs.last${past_days}days.v${VDATE}.tar ] ; then
   cp -v evs.plots.narre.grid2obs.last${past_days}days.v${VDATE}.tar  $COMOUT/.
fi

if [ $SENDDBN = YES ] ; then    
   $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.narre.grid2obs.last${past_days}days.v${VDATE}.tar
fi 

