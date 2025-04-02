#!/bin/ksh
#################################################################################
# Purpose: setup environment, paths, and run the narre ploting python script
# Last updated: 
#               02/05/2025, Add MPMD,  Binbin Zhou Lynker@EMC/NCEP
#               04/01/2024, Add restart capability, Binbin Zhou Lynker@EMC/NCEP
#               After a sub-task file is create, first check if it has been done
#               in the previous (see its .completed file exists or not)
#               If it has been done before, then skip further building this 
#               sub-task, so that this sub-task file name is 0 size in the
#               working directory
#
#               10/27/2023, Binbin Zhou Lynker@EMC/NCEP
##################################################################################
set -x 

mkdir -p $DATA/scripts
cd $DATA/scripts

export machine=${machine:-"WCOSS2"}
export output_base_dir=$DATA/stat_archive
mkdir -p $output_base_dir

all_plots=$DATA/plots/all_plots
mkdir -p $all_plots
if [ $SENDCOM = YES ] ; then
  restart=$COMOUT/restart/$last_days/narre_plots
  if [ ! -d  $restart ] ; then
    mkdir -p $restart 
  fi 
fi

export eval_period='TEST'

export init_end=$VDATE
export valid_end=$VDATE

n=0
while [ $n -le $last_days ] ; do
    hrs=$((n*24))
    first_day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
    n=$((n+1))
done

export init_beg=$first_day
export valid_beg=$first_day

#*************************************************************************
# Virtual link the  narre's stat data files of last days (31 or 90 days)
#**************************************************************************
n=0
while [ $n -le $last_days ] ; do
  #hrs=`expr $n \* 24`
  hrs=$((n*24))
  day=`$NDATE -$hrs ${VDATE}00|cut -c1-8`
  echo $day
  $USHevs/narre/evs_get_narre_stat_file_link.sh $day
  n=$((n+1))
done 

VX_MASK_LIST="G130 G242"

export fcst_valid_hour="0 3 6 9 12 15 18 21"
export fcst_lead="1,2,3,4,5,6,7,8,9,10,11,12"

#*****************************************
# Build a POE file to collect sub-jobs
# **************************************** 
> run_all_poe.sh 
for grid in $VX_MASK_LIST ; do

 for score_type in performance_diagram ; do

  for var in VISsfc HGTcldceil ; do 
 
    if [ $var = VISsfc ] ; then
      export vname=vis
    elif [ $var = HGTcldceil ] ; then
      export vname=hgt
    fi

   for line_type in ctc ; do 

    #*****************************************************************************
    # Build sub-jobs and setup environment for running the python plotting scripts
    # ****************************************************************************
    > run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh 

  if [ $grid = G130 ] ; then
    export grd=g130
  elif [ $grid = G242 ] ; then
    export grd=g242
  fi

  for valid in $fcst_valid_hour ; do

   typeset -Z2 vhh
   vhh=${valid}	  

  #**********************************************************************************************
  # Check if this sub-job has been completed in the previous run for restart
   if [ ! -e $restart/run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.completed ] ; then
  #************************************************************************************************
    echo "#!/bin/ksh" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
    echo "set -x" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh

    save_dir=$DATA/plots/run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}
    plot_dir=$save_dir/sfc_upper/${valid_beg}-${valid_end}
    mkdir -p $plot_dir
    mkdir -p $save_dir/data 

    echo "export save_dir=$save_dir" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
    echo "export log_metplus=$save_dir/log_${grid}.${score_type}.${var}.${line_type}.${valid}.out" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
    echo "export prune_dir=$save_dir/data" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh

    if [ $grid = G130 ] ; then
      echo "export mask=buk_conus" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
    elif [ $grid = G242 ] ; then
      echo "export mask=alaska" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
    fi

      echo "export PLOT_TYPE=$score_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh

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

     echo "export vx_mask_list=$grid" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "export verif_case=grid2obs" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "export verif_type=conus_sfc" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh

     echo "export log_level=INFO" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "export model=NARRE_MEAN" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh

     echo "export eval_period=TEST" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh

     if [ $score_type = valid_hour_average ] ; then
       echo "export date_type=INIT" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     else
       echo "export date_type=VALID" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     fi

     echo "export var_name=$var" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "export fcts_level=$FCST_LEVEL_value" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "export obs_level=$OBS_LEVEL_value" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh


     echo "export line_type=$line_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "export interp=NEAREST" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "export score_py=$score_type" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh

     sed -e "s!stat_list!$stat_list!g"  -e "s!thresh_list!$thresh!g" -e "s!fcst_init_hour!$fcst_init_hour!g" -e "s!fcst_valid_hour!$valid!g" -e "s!fcst_lead!$fcst_lead!g"  $USHevs/narre/evs_narre_plots.sh > run_py.${var}_${line_type}.${score_type}.${grid}.${valid}.sh

     chmod +x run_py.${var}_${line_type}.${score_type}.${grid}.${valid}.sh

     echo "${DATA}/scripts/run_py.${var}_${line_type}.${score_type}.${grid}.${valid}.sh" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
 
     echo "if [ -s ${plot_dir}/${score_type}_regional_${grd}_valid_${vhh}z_${vname}_*.png ] ; then" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "  cp -v ${plot_dir}/${score_type}_regional_${grd}_valid_${vhh}z_${vname}_*.png $all_plots" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "  >${plot_dir}/run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.completed" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "  echo \"run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.completed\" >> ${plot_dir}/run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.completed" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "  if [ $SENDCOM = YES ] ; then" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "    cp $all_plots/${score_type}_regional_${grd}_valid_${vhh}z_${vname}_*.png $restart" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "    cp ${plot_dir}/run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.completed $restart" >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "  fi " >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "fi " >> run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh

     chmod +x run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh
     echo "${DATA}/scripts/run_narre_${grid}.${score_type}.${var}.${line_type}.${valid}.sh" >> run_all_poe.sh

    else
      #Copy stat files from restart to working directory
      if [ -s $restart/${score_type}_regional_${grd}_valid_${vhh}z_${vname}_*.png ] ; then
	cp $restart/${score_type}_regional_${grd}_valid_${vhh}z_${vname}_*.png $all_plots
      fi
    fi      

     done

    done 

  done 

 done 

done  

chmod +x run_all_poe.sh

#***************************************************************************
# Run the POE script in parallel or in sequence order to generate png files
# **************************************************************************
if [ $run_mpi = yes ] ; then
   mpiexec -np 16 -ppn 16 --cpu-bind verbose,core cfp ${DATA}/scripts/run_all_poe.sh
   export err=$?; err_chk
else
  ${DATA}/scripts/run_all_poe.sh
  export err=$?; err_chk
fi

#**************************************************
# Change plot file names to meet the EVS standard
#**************************************************
cd $all_plots

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

   for valid in 00 03 06 09 12 15 18 21 ; do

    if [ -s performance_diagram_regional_${grid}_valid_${valid}z_${var}_f1_to_f12_${thrsh}.png ] ; then
      mv  performance_diagram_regional_${grid}_valid_${valid}z_${var}_f1_to_f12_${thrsh}.png evs.narre.ctc.${field}.last${last_days}days.perfdiag_valid${valid}z.${domain}.png
    fi 
   done
  done
done

if [ -s evs*.png ] ; then
 tar -cvf evs.plots.narre.grid2obs.last${last_days}days.v${VDATE}.tar evs*.png
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

if [ $SENDCOM = YES ] && [ -s evs.plots.narre.grid2obs.last${last_days}days.v${VDATE}.tar ] ; then
   cp -v evs.plots.narre.grid2obs.last${last_days}days.v${VDATE}.tar  $COMOUT/.
fi

if [ $SENDDBN = YES ] ; then    
   $DBNROOT/bin/dbn_alert MODEL EVS_RZDM $job $COMOUT/evs.plots.narre.grid2obs.last${last_days}days.v${VDATE}.tar
fi 

