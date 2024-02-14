#!/bin/ksh
#************************************************************************************
#  Purpose: Generate href spcoutlook job's  poe and sub-jobs files
#           and system (ecnt line type)
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#***********************************************************************************
set -x 

#******************************************
# Get prefix of $EVSINspcotlk 
# *****************************************
tail='/cam'
prefix=${EVSINspcotlk%%$tail*}
index=${#prefix}
echo $index

day1=`$NDATE -24 ${VDATE}00 |cut -c1-8`
day2=`$NDATE -48 ${VDATE}00 |cut -c1-8`
day3=`$NDATE -72 ${VDATE}00 |cut -c1-8`

mask_day1=${EVSINspcotlk:0:$index}/cam/spc_otlk.$day1
mask_day2=${EVSINspcotlk:0:$index}/cam/spc_otlk.$day2
mask_day3=${EVSINspcotlk:0:$index}/cam/spc_otlk.$day3

write_job_cards=yes
if ([ ! -d  $mask_day1 ] || (! ls $mask_day1/spc_otlk.day1_*G227.nc 1> /dev/null 2>&1)) \
  && ([ ! -d  $mask_day2 ] || (! ls $mask_day2/spc_otlk.day2_*G227.nc 1> /dev/null 2>&1)) \
  && ([ ! -d  $mask_day3 ] || (! ls $mask_day3/spc_otlk.day3_*G227.nc 1> /dev/null 2>&1)) ; then
  if [ $SENDMAIL = YES ] ; then
    export subject="SPC outlook mask files are Missing for EVS ${COMPONENT}"
    echo "Warning:  No SPC outlook mask files available for ${VDATE}" > mailmsg
    echo Missing mask files are $mask_day1/spc_otlk.day1_*G227.nc , $mask_day2/spc_otlk.day2_*G227.nc and $mask_day3/spc_otlk.day3_*G227.nc   >> mailmsg
    echo "Job ID: $jobid" >> mailmsg
    cat mailmsg | mail -s "$subject" $MAILTO
    export err=$?; err_chk
  else
    echo "WARNING:  No SPC outlook mask files available for ${VDATE}."
    echo "Missing mask files are $mask_day1/spc_otlk.day1_*G227.nc , $mask_day2/spc_otlk.day2_*G227.nc and $mask_day3/spc_otlk.day3_*G227.nc"
    echo "This will occur if no outlooks were issued on ${VDATE}."
  fi
  write_job_cards=no
fi


if ([ -d $mask_day1 ] && (ls $mask_day1/spc_otlk.day1_*G227.nc 1> /dev/null 2>&1)); then
    cd $mask_day1 
    files=`ls spc_otlk.day1_*G227.nc`
    set -A file $files
    len=${#file[@]}

    spc_otlk_masks=$mask_day1/${file[0]}

    for (( i=1; i<$len; i++ )); do
      mask="${file[$i]}"
      export spc_otlk_masks="$spc_otlk_masks, $mask_day1/${mask}"
    done
fi

if ([ -d $mask_day2 ] && (ls $mask_day2/spc_otlk.day2_*G227.nc 1> /dev/null 2>&1)); then
    cd $mask_day2
    files=`ls spc_otlk.day2_*G227.nc`
    set -A file $files
    len=${#file[@]}

    for (( i=0; i<$len; i++ )); do
      mask="${file[$i]}"
      export spc_otlk_masks="$spc_otlk_masks, $mask_day2/${mask}"
    done
fi

if ([ -d $mask_day3 ] && (ls $mask_day3/spc_otlk.day3_*G227.nc 1> /dev/null 2>&1)); then
    cd $mask_day3
    files=`ls spc_otlk.day3_*G227.nc`
    set -A file $files
    len=${#file[@]}

    for (( i=0; i<$len; i++ )); do
      mask="${file[$i]}"
      export spc_otlk_masks="$spc_otlk_masks, $mask_day3/${mask}"
    done
fi

echo $spc_otlk_masks

cd $WORK

#*******************************************
# Build POE script to collect sub-jobs
#******************************************
>run_all_href_spcoutlook_poe.sh

obsv='prepbufr'
if [ "$write_job_cards" = "yes" ] ; then
for prod in mean ; do

 PROD=`echo $prod | tr '[a-z]' '[A-Z]'`

 model=HREF${prod}

 for dom in CONUS ; do

   for valid in 0 12 ; do

    export domain=$dom

     #******************************
     # Build sub-jobs
     # *****************************
     >run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export model=HREF${prod} " >>  run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export domain=$dom " >> run_href_${model}.${dom}.${valid}_spcoutlook.sh     
       echo  "export regrid=G227" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export output_base=${WORK}/grid2obs/run_href_${model}.${dom}.${valid}_spcoutlook" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export OBTYPE='PREPBUFR'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export domain=CONUS" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export obsvgrid=G227" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export modelgrid=conus.${prod}" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export obsvhead=$obsv" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export obsvpath=$WORK" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export vbeg=$valid" >>run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export vend=$valid" >>run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export valid_increment=3600" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export lead='6,12,18,24,30,36,42,48'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export MODEL=HREF_${PROD}" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export regrid=G227" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export modelhead=$model" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export modelpath=$COMHREF" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export modeltail='.grib2'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo  "export extradir='ensprod/'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "export verif_grid=''" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo "export verif_poly='$spc_otlk_masks'" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo  "${METPLUS_PATH}/ush/run_metplus.py -c ${PARMevs}/metplus_config/machine.conf -c ${GRID2OBS_CONF}/PointStat_fcstHREF${prod}_obsPREPBUFR_SPCoutlook.conf " >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       echo "cp \$output_base/stat/\${MODEL}/*.stat $COMOUTsmall" >> run_href_${model}.${dom}.${valid}_spcoutlook.sh

       chmod +x run_href_${model}.${dom}.${valid}_spcoutlook.sh
       echo "${DATA}/run_href_${model}.${dom}.${valid}_spcoutlook.sh" >> run_all_href_spcoutlook_poe.sh

    done # end of valid

  done #end of dom loop

done #end of prod loop
fi

chmod 775 run_all_href_spcoutlook_poe.sh
export err=$?; err_chk
