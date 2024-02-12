#!/bin/ksh
#***********************************************************************************
# Purpose:  Process/prepare ECM analysis data files and ECME ensemble member files
#  
#  Last update: 11/16/2023, by Binbin Zhou (Lynker@NCPE/EMC)
#***********************************************************************************         
set -x

cd $WORK

#########################################################
# !!! DEFINE MAXIMUM NUMBER OF PERTURBATION RECORDS
# (This number does NOT include the LRC or HRC)
#########################################################

CDATE=$1  #day+running init hour
ihour=$2
inithour=t${ihour}z

#####################################################################
# Set date variables to process CDATE data  
#####################################################################
tdate=`$NDATE 0 $CDATE | cut -c1-8`
cent=`echo $tdate | cut -c1-2 `
yy=`  echo $tdate | cut -c3-4 `
mm=`  echo $tdate | cut -c5-6 `
dd=`  echo $tdate | cut -c7-8 `
indate=$cent$yy$mm$dd
cent=`echo $indate | cut -c1-2 `
yy=`  echo $indate | cut -c3-4 `
mm=`  echo $indate | cut -c5-6 `
dd=`  echo $indate | cut -c7-8 `
yyyymmdd=$indate
yyyymmddhh=${yyyymmdd}${ihour}
ymdh=${indate}${ihour}
imdh=${mm}${dd}${ihour}
hh=${ihour}
echo " Date to copy is $indate"
yymmddhh=${yy}${mm}${dd}${hh}

get_ecme='yes'

if [ $get_ecme = 'yes' ] ; then

tmpDir=$WORK/ecmetmp
mkdir -p $tmpDir

#**********************************************
# List all required fields to be retrieved
#**********************************************	
VAR[1]=':10U:'
VAR[2]=':10V:'
VAR[3]=':U:kpds5=131:kpds6=100:kpds7=850:'
VAR[4]=':V:kpds5=132:kpds6=100:kpds7=850:'
VAR[5]=':U:kpds5=131:kpds6=100:kpds7=250:'
VAR[6]=':V:kpds5=132:kpds6=100:kpds7=250:'
VAR[7]=':GH:kpds5=156:kpds6=100:kpds7=500:'
VAR[8]=':GH:kpds5=156:kpds6=100:kpds7=700:'
VAR[9]=':GH:kpds5=156:kpds6=100:kpds7=1000:'
VAR[10]=':T:kpds5=130:kpds6=100:kpds7=500:'
VAR[11]=':T:kpds5=130:kpds6=100:kpds7=850:'
VAR[12]=':2T:'
VAR[13]=':TCC:'
VAR[14]=':MSL:'
VAR[15]=':2D:'
VAR[20]=':TP:'
VAR[21]=':SF:'

pat0=${tmpDir}/pattern.file0.${ihour}
if [ -e ${pat0} ]; then rm ${pat0}; fi
>${pat0}
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 ; do
  echo "${VAR[$n]}" >> ${pat0}
done

pat=${tmpDir}/pattern.file.${ihour}
if [ -e ${pat} ]; then rm ${pat}; fi
>${pat}
for n in 1 2 12 13 14 15 ; do
  echo "${VAR[$n]}" >> ${pat}
done

#***********************************************************************************
# Retrieve requried fields from  ECME's DCD analysis data files (grib1) in DCOM
#************************************************************************************
hourix=0
while [ ${hourix} -lt 31 ]; do
  # Get DCD files
  let hourinc=hourix*12
  vymdh=` ${NDATE} ${hourinc} ${ymdh}`
  vmdh=`  echo ${vymdh} | cut -c5-10`
  vhour=` ${NHOUR} ${vymdh} ${ymdh}`
  if [ ${hourix} = 0 ] ; then
    DCD=${DCOMIN}/$yyyymmdd/wgrbbul/ecmwf/DCD${imdh}00${vmdh}001
    if [ -s $DCD ] ; then
      >$WORK/ecmanl.t${ihour}z.grid3.f000.grib1
      chmod 640 $WORK/ecmanl.t${ihour}z.grid3.f000.grib1
      chgrp rstprod $WORK/ecmanl.t${ihour}z.grid3.f000.grib1
        $WGRIB $DCD|grep --file=${pat0}|$WGRIB -i -grib $DCD -o x
       chmod 640 x
       chgrp rstprod x
       cat x >> $WORK/ecmanl.t${ihour}z.grid3.f000.grib1
      if [[ $SENDCOM="YES" ]]; then
          if [ -s $WORK/ecmanl.t${ihour}z.grid3.f000.grib1 ]; then
              cp -v $WORK/ecmanl.t${ihour}z.grid3.f000.grib1 $COMOUTecme/ecmanl.t${ihour}z.grid3.f000.grib1
          fi
          chmod 640 $COMOUTecme/ecmanl.t${ihour}z.grid3.f000.grib1
          chgrp rstprod $COMOUTecme/ecmanl.t${ihour}z.grid3.f000.grib1
      fi
    else
      echo "WARNING: $DCD is not available"
      if [ $SENDMAIL = YES ]; then
        export subject="ECME Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No ECME data for ${ymdh}" > mailmsg
        echo "Missing file is $DCD"  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
    fi 
  fi 


  #******************************************************************
  # Retrieve requried fields from ECME member files E1E in DCOM
  #******************************************************************
  E1E=${DCOMIN}/$yyyymmdd/wgrbbul/ecmwf/E1E${imdh}00${vmdh}001
  if [ ! -s $E1E ]; then
    echo "WARNING: $E1E is not available"
    if [ $SENDMAIL = YES ]; then
        export subject="ECME Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No ECME data for ${ymdh}" > mailmsg
        echo "Missing files are in $E1E"  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $MAILTO
      fi
  else 
    >E1E.${hourinc}
    chmod 640 E1E.${hourinc}
    chgrp rstprod E1E.${hourinc}
        $WGRIB $E1E|grep --file=${pat}|$WGRIB -i -grib $E1E -o x
       chmod 640 x
       chgrp rstprod x
       cat x >> E1E.${hourinc}
    h3=${hourinc}
    typeset -Z3 h3
    mbr=1
     while [ ${mbr} -le 50 ]; do
      m2=$mbr
      typeset -Z2 m2
      $WGRIB E1E.${hourinc}|grep "forecast $mbr:"|$WGRIB -i -grib E1E.${hourinc} -o $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      chmod 640 $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      chgrp rstprod $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      if [[ $SENDCOM="YES" ]]; then
          if [ -s ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1 ]; then
              cp -v $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
          fi
          chmod 640 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
          chgrp rstprod $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      fi
      mbr=$((mbr+1))
    done
    rm E1E.${hourinc}
  fi
  let hourix=hourix+1
done 

#******************************************************************
#  Retrieve requried fields from ECME member files E1E in DCOM
#******************************************************************
hourix=0
while [ ${hourix} -lt 31 ]; do
  let hourinc=hourix*12
  vymdh=` ${NDATE} ${hourinc} ${ymdh}`
  vmdh=`  echo ${vymdh} | cut -c5-10`
  vhour=` ${NHOUR} ${vymdh} ${ymdh}`
  E1E=${DCOMIN}/$yyyymmdd/wgrbbul/ecmwf/E1E${imdh}00${vmdh}001
  if [ -s $E1E ]; then
    >E1E_apcp.${hourinc}
    chmod 640 E1E_apcp.${hourinc}
    chgrp rstprod E1E_apcp.${hourinc}
    for n in 20 21 ; do
       $WGRIB $E1E|grep "${VAR[$n]}"|$WGRIB -i -grib $E1E -o x
       chmod 640 x
       chgrp rstprod x
       cat x >> E1E_apcp.${hourinc}
    done
    h3=${hourinc}
    typeset -Z3 h3
    mbr=1
     while [ ${mbr} -le 50 ]; do
      m2=$mbr
      typeset -Z2 m2
      $WGRIB E1E_apcp.${hourinc}|grep "forecast $mbr:"|$WGRIB -i -grib E1E_apcp.${hourinc} -o $WORK/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
      chmod 640 $WORK/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
      chgrp rstprod $WORK/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
      if [[ $SENDCOM="YES" ]]; then
        if [ -s $WORK/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1 ]; then
            cp -v $WORK/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
        fi
        chmod 640 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
        chgrp rstprod $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
      fi
      mbr=$((mbr+1))
     done
     rm E1E_apcp.${hourinc}
  else
     echo "WARNING: $E1E is not available"
        if [ $SENDMAIL = YES ]; then
            export subject="ECME Data Missing for EVS ${COMPONENT}"
            echo "Warning:  No ECME data for ${ymdh}" > mailmsg
            echo "Missing files are in $E1E"  >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
        fi
  fi
  let hourix=hourix+1
done


#***********************************************************************
#  Retrieve requried upper air fields from ECME member files E1E in DCOM
#***********************************************************************
VAR[1]=':U:kpds5=131:kpds6=100'
VAR[2]=':V:kpds5=132:kpds6=100'
VAR[3]=':GH:kpds5=156:kpds6=100'
VAR[4]=':T:kpds5=130:kpds6=100'
VAR[5]=':R:kpds5=157:kpds6=100'

pat2=$tmpDir/pattern.file2.${ihour}
pat3=$tmpDir/pattern.file3.${ihour}

if [ -e ${pat2} ]; then rm ${pat2}; fi
>${pat2}
for n in 1 2 3 4 5 ; do
  for level in 50 100 200 300 400 500 700 850 925 1000 ; do
   echo "${VAR[$n]}:kpds7=${level}" >> ${pat2}
  done
done

hourix=0
while [ ${hourix} -lt 31 ]; do
  let hourinc=hourix*12
  vymdh=` ${NDATE} ${hourinc} ${ymdh}`
  vmdh=`  echo ${vymdh} | cut -c5-10`
  vhour=` ${NHOUR} ${vymdh} ${ymdh}`
  E1E=${DCOMIN}/$yyyymmdd/wgrbbul/ecmwf/E1E${imdh}00${vmdh}001
  if [ -s $E1E ]; then
    >E1E_vertical.${hourinc}
    chmod 640 E1E_vertical.${hourinc}
    chgrp rstprod E1E_vertical.${hourinc}
        $WGRIB $E1E|grep --file=${pat2}|$WGRIB -i -grib $E1E -o x
        chmod 640 x
        chgrp rstprod x
        cat x >> E1E_vertical.${hourinc}
    h3=${hourinc}
    typeset -Z3 h3
    mbr=1
     while [ ${mbr} -le 50 ]; do
      m2=$mbr
      typeset -Z2 m2
      $WGRIB E1E_vertical.${hourinc}|grep "forecast $mbr:"|$WGRIB -i -grib E1E_vertical.${hourinc} -o E1E_vertical.${hourinc}.mbr${mbr}
      chmod 640 E1E_vertical.${hourinc}.mbr${mbr}
      chgrp rstprod E1E_vertical.${hourinc}.mbr${mbr}
      cat E1E_vertical.${hourinc}.mbr${mbr} >> $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      chmod 640 $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      chgrp rstprod $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      if [[ $SENDCOM="YES" ]]; then
          if [ -s $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1 ]; then
              cp -v $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
          fi
          chmod 640 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
          chgrp rstprod $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      fi
      mbr=$((mbr+1))
     done
     rm E1E_vertical.${hourinc}*
  else
     echo "WARNING: $E1E is not available"
        if [ $SENDMAIL = YES ]; then
            export subject="ECME Data Missing for EVS ${COMPONENT}"
            echo "Warning:  No ECME data for ${ymdh}" > mailmsg
            echo "Missing files are in $E1E"  >> mailmsg
            echo "Job ID: $jobid" >> mailmsg
            cat mailmsg | mail -s "$subject" $MAILTO
        fi
 
  fi
  let hourix=hourix+1
done

fi #get_ecme
