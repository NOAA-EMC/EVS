#!/bin/ksh
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
      for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 ; do
       $WGRIB $DCD|grep "${VAR[$n]}"|$WGRIB -i -grib $DCD -o x 
       chmod 640 x
       chgrp rstprod x
       cat x >> $WORK/ecmanl.t${ihour}z.grid3.f000.grib1
      done
      if [[ $SENDCOM="YES" ]]; then
          cpreq -v $WORK/ecmanl.t${ihour}z.grid3.f000.grib1 $COMOUTecme/ecmanl.t${ihour}z.grid3.f000.grib1
          chmod 640 $COMOUTecme/ecmanl.t${ihour}z.grid3.f000.grib1
          chgrp rstprod $COMOUTecme/ecmanl.t${ihour}z.grid3.f000.grib1
      fi
    else
      if [ $SENDMAIL = YES ]; then
        export subject="ECME Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No ECME data for ${ymdh}" > mailmsg
        echo "Missing file is $DCD"  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
      fi
    fi 
  fi 
  # Get E1E
  E1E=${DCOMIN}/$yyyymmdd/wgrbbul/ecmwf/E1E${imdh}00${vmdh}001
  if [ ! -s $E1E ]; then
    if [ $SENDMAIL = YES ]; then
        export subject="ECME Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No ECME data for ${ymdh}" > mailmsg
        echo "Missing files are in $E1E"  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
      fi
  else 
    >E1E.${hourinc}
    chmod 640 E1E.${hourinc}
    chgrp rstprod E1E.${hourinc}
    for n in 1 2 12 13 14 15 ; do
       $WGRIB $E1E|grep "${VAR[$n]}"|$WGRIB -i -grib $E1E -o x
       chmod 640 x
       chgrp rstprod x
       cat x >> E1E.${hourinc}
    done
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
          cpreq -v $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
          chmod 640 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
          chgrp rstprod $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      fi
      mbr=$((mbr+1))
    done
    rm E1E.${hourinc}
    let hourix=hourix+1
  fi
done 

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
        cpreq -v $WORK/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
        chmod 640 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
        chgrp rstprod $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4_apcp.f${h3}.grib1
      fi
      mbr=$((mbr+1))
     done
     rm E1E_apcp.${hourinc}
    let hourix=hourix+1
  fi
done

VAR[1]=':U:kpds5=131:kpds6=100'
VAR[2]=':V:kpds5=132:kpds6=100'
VAR[3]=':GH:kpds5=156:kpds6=100'
VAR[4]=':T:kpds5=130:kpds6=100'
VAR[5]=':R:kpds5=157:kpds6=100'

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
    for n in 1 2 3 4 5  ; do
      for level in 50 100 200 300 400 500 700 850 925 1000 ; do 
        $WGRIB $E1E|grep "${VAR[$n]}:kpds7=${level}:"|$WGRIB -i -grib $E1E -o x
        chmod 640 x
        chgrp rstprod x
        cat x >> E1E_vertical.${hourinc}
     done
    done
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
          cpreq -v $WORK/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
          chmod 640 $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
          chgrp rstprod $COMOUTecme/ecme.ens${m2}.t${ihour}z.grid4.f${h3}.grib1
      fi
      mbr=$((mbr+1))
     done
     rm E1E_vertical.${hourinc}*
  fi
  let hourix=hourix+1
done

fi #get_ecme
