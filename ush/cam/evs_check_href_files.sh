#!/bin/ksh
#**************************************************************************
#  Purpose: check the required input forecast and validation data files
#           for href stat jobs
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
set -x

vday=$VDATE

typeset -Z2 vhr

missing=0 
for vhr in 00 01 02 03 04 05 06 07 08  09 10 11 12 13 14 15 16 17 18 19 20  21 22 23 ; do
  if [ ! -s $COMINobsproc/rap.${vday}/rap.t${vhr}z.prepbufr.tm00 ] ; then
    missing=$((missing + 1 ))
    echo  $COMINobsproc/rap.${vday}/rap.t${vhr}z.prepbufr.tm00 is missing
  fi
done

echo "Missing prepbufr files = " $missing
if [ $missing -eq 24  ] ; then
  echo "WARNING: all of the preppbufr files are missing, exit execution!!!"
  export err=$?; err_chk
  exit
else
  echo "Continue check CCAP files...." 
fi


if [ $VERIF_CASE = precip ] ; then
next=`$NDATE +24 ${vday}12 |cut -c 1-8`
prev=`$NDATE -24 ${vday}12 |cut -c 1-8`

missing=0
for vhr in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ; do
  if [ $vhr = 00 ] ; then
    cyc_dir=00
    init=$vday
  elif [ $vhr = 01 02 03 04 05 06  ] || [ $vhr = 06 ] ; then
    cyc_dir=06
    init=$vday
  elif [ $vhr = 07 08 09 10 11 12  ] || [ $vhr = 12 ] ; then
    cyc_dir=12
    init=$vday
  elif [ $vhr = 13 14 15 16 17 18 ] || [ $vhr = 18 ] ; then
    cyc_dir=18
    init=$vday
  elif [ $vhr = 19 20 21 22 23 ] ; then
    cyc_dir=00
    init=$next
  fi	      
  if [ $VERIF_CASE = precip ] ; then
     ccpa=$COMINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${vhr}z.01h.hrap.conus.gb2
  else
     ccpa=$EVSINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${vhr}z.01h.hrap.conus.gb2
  fi
  #echo $ccpa

  if [ ! -s $ccpa ] ; then
      missing=$((missing + 1 ))
      echo $ccpa is missing
  fi
done

echo "Missing ccpa01h files = " $missing
if [ $missing -eq 24  ] ; then
  echo "WARNING: all of the ccpa files are missing, exit execution!!!"
  export err=$?; err_chk
  exit
fi

fi 

missing=0
for vhr in 00 03 06 09 12 15 18 21 ; do
  if [ $vhr = 00 ] ; then
      cyc_dir=00
      init=$vday
  elif [ $vhr = 03 06  ] || [ $vhr = 06 ] ; then
      cyc_dir=06
      init=$vday
  elif [ $vhr = 09 12  ] || [ $vhr = 12 ] ; then
       cyc_dir=12
       init=$vday
  elif [ $vhr = 15 18 ] || [ $vhr = 18 ] ; then
       cyc_dir=18
       init=$vday
  elif [ $vhr = 21 ] ; then
       cyc_dir=00
       init=$next
  fi

  if [ $VERIF_CASE = precip ] ; then
     ccpa=$COMINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${vhr}z.03h.hrap.conus.gb2
  else
     ccpa=$EVSINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${vhr}z.03h.hrap.conus.gb2
  fi
   #echo $ccpa

   if [ ! -s $ccpa ] ; then
         missing=$((missing + 1 ))
	 echo $ccpa is missing
   fi

done

echo "Missing ccpa03h files = " $missing
if [ $missing -eq 8  ] ; then
  echo "WARNING: all of the ccpa03h files are missing, exit execution!!!"
  export err=$?; err_chk
  exit
fi

missing=0
for vhr in 12 ; do
   if [ $VERIF_CASE = precip ] ; then
      if [ ! -s $COMINccpa/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 ] ; then
          missing=$((missing+1))
      elif [ ! -s $COMINccpa/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 ] ; then
              missing=$((missing+1))
      elif [ ! -s $COMINccpa/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 ] ; then
          missing=$((missing+1))
      elif [ ! -s $COMINccpa/ccpa.${prev}/18/ccpa.t18z.06h.hrap.conus.gb2 ] ; then
          missing=$((missing+1))
      fi
   else
      if [ ! -s $EVSINccpa/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 ] ; then
          missing=$((missing+1))
	  echo $EVSINccpa/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 is missing
      elif [ ! -s $EVSINccpa/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 ] ; then
              missing=$((missing+1))
	      echo $EVSINccpa/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 is missing
      elif [ ! -s $EVSINccpa/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 ] ; then
          missing=$((missing+1))
	  echo $EVSINccpa/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 is missing
      elif [ ! -s $EVSINccpa/ccpa.${prev}/18/ccpa.t18z.06h.hrap.conus.gb2 ] ; then
          missing=$((missing+1))
	  echo $EVSINccpa/ccpa.${prev}/18/ccpa.t18z.06h.hrap.conus.gb2 is missing
      fi
   fi
done

echo "Missing ccpa06h files = " $missing
if [ $missing -ge 1  ] ; then
  echo "WARNING: At least one of the ccpa06h files are missing, exit execution!!!"
  export err=$?; err_chk
  exit
fi

missing=0
accum=01

 if [ $accum = 03 ] ; then
    cycs="00 03 06 09 12 15 18 21"
 elif [ $accum = 24 ] ; then
    cycs="00 06 12  18"
 elif [ $accum = 01 ] ; then
    cycs="00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23"
 fi

accum=01
missing=0
for vhr in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ; do
   mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
   if [ ! -s $mrms ] ; then
     missing=$((missing+1))
     echo $mrms is missing
   fi
done
echo "Missing mrms01h files = " $missing
if [ $missing -eq 24  ] ; then
  echo "WARNING: All of mrms01h files are missing, exit execution!!!"
  export err=$?; err_chk
  exit
fi

accum=03
missing=0
for vhr in 00 03 06 09 12 15 18 21 ; do
   mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
   if [ ! -s $mrms ] ; then
     missing=$((missing+1))
     echo $mrms is missing
   fi
done
echo "Missing mrms03h files = " $missing
if [ $missing -eq 8  ] ; then
  echo "WARNING: All of mrms03h files are missing, exit execution!!!"
  export err=$?; err_chk
  exit
fi

accum=24
missing=0
for vhr in 00 06 12 18 ; do
   mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
   if [ ! -s $mrms ] ; then
     missing=$((missing+1))
     echo $mrms is missing
   fi
done
echo "Missing mrms24h files = " $missing
if [ $missing -eq 4  ] ; then
 echo "WARNING: All of mrms24h files are missing, exit execution!!!"   
 export err=$?; err_chk
 exit
fi

echo "Continue checking HREF members" 

domain=conus 
for obsv_cyc in 00 03 06 09 12 15 18 21 ; do 
 for fhr in 03 06 09 12 15 18 21 24 27 30 33 36 39 42 45 48 ; do 	
    fcst_time=`$NDATE -$fhr ${vday}${obsv_cyc}`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}

   if [ $fcyc = 00 ] || [ $fcyc = 06 ] || [ $fcyc = 12 ] || [ $fcyc = 18 ] ; then

      href_mbrs=0
      for mb in 01 02 03 04 05 06 07 08 09 10 ; do 
        href=$COMINhref/href.${fday}/verf_g2g/href.m${mb}.t${fcyc}z.conus.f${fhr}
        #echo $href
	if [ -s $href ] ; then
           href_mbrs=$((href_mbrs+1))
	else
	   echo $href is missing
        fi	    
      done

      #echo fday=$fday fcyc=$fcyc fhr=$fhr href_mbrs=$href_mbrs

      if [ $href_mbrs -lt 4 ] ; then
        echo "WARNING: HREF members = " $href_mbrs " which < 4, exit METplus execution !!!"
        export err=$?; err_chk
        exit
      fi

   fi

  done
done

echo "All HREF member files in CONUS are available. COntinue checking ..."

domain=ak
href_mbrs=0
for obsv_cyc in 00 03 06 09 12 15 18 21 ; do 
 for fhr in 03 06 09 12 15 18 21 24 27 30 33 36 39 42 45 48 ; do 	

    fcst_time=`$NDATE -$fhr ${vday}${obsv_cyc}`
    fday=${fcst_time:0:8}
    fcyc=${fcst_time:8:2}


   if [ $fcyc = 06 ] ; then

      href_mbrs=0
      for mb in 01 02 03 04 05 06 07 08 09 10 ; do 
        href=$COMINhref/href.${fday}/verf_g2g/href.m${mb}.t${fcyc}z.ak.f${fhr}
        #echo $href
	if [ -s $href ] ; then
           href_mbrs=$((href_mbrs+1))
	else
	   echo $href is missing
        fi	    
      done

      #echo fday=$fday fcyc=$fcyc fhr=$fhr href_mbrs=$href_mbrs

      if [ $href_mbrs -lt 4 ] ; then
        echo "WARNING: HREF members = " $href_mbrs " which < 4, exit METplus execution !!!"
        export err=$?; err_chk
        exit
      fi
   fi

  done
done


echo "All HREF member files in Alaska are available. Continue checking ..." 



domain=conus 
for obsv_cyc in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23  ; do 
    typeset -Z2 fhr
    fhr=01

    while [ $fhr -le 48 ] ; do 
      fcst_time=`$NDATE -$fhr ${vday}${obsv_cyc}`
      fday=${fcst_time:0:8}
      fcyc=${fcst_time:8:2}

      if [ $fcyc = 00 ] || [ $fcyc = 06 ] || [ $fcyc = 12 ] || [ $fcyc = 18 ] ; then
      
       href_prod=0	      
       for  prod in mean prob eas pmmn lpmm avrg ; do 
         href=$COMINhref/href.${fday}/ensprod/href.t${fcyc}z.conus.${prod}.f${fhr}.grib2
         #echo $href
	 if [ -s $href ] ; then
           href_prod=$((href_prod+1))
	 else
           echo $href is missing		 
        fi	    
       done

       #echo fday=$fday fcyc=$fcyc fhr=$fhr href_prod=$href_prod

        if [ $href_prod -lt 4 ] ; then
          echo "WARNING: HREF Products = " $href_prod " which < 4, some products are missing, exit METplus execution !!!"
          export err=$?; err_chk
          exit
        fi

      fi
 
      fhr=$((fhr+1))  
  done

done

echo "All HREF ensemble products files in CONUS are available. Continue checking ..."




domain=ak
for obsv_cyc in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23  ; do 
    typeset -Z2 fhr
    fhr=01

    while [ $fhr -le 48 ] ; do 
      fcst_time=`$NDATE -$fhr ${vday}${obsv_cyc}`
      fday=${fcst_time:0:8}
      fcyc=${fcst_time:8:2}

      if [ $fcyc = 06 ] ; then
      
       href_prod=0	      
       for  prod in mean prob eas pmmn lpmm avrg ; do 
         href=$COMINhref/href.${fday}/ensprod/href.t${fcyc}z.ak.${prod}.f${fhr}.grib2
         #echo $href
	 if [ -s $href ] ; then
           href_prod=$((href_prod+1))
	 else
           echo $href is missing		 
        fi	    
       done

       #echo fday=$fday fcyc=$fcyc fhr=$fhr href_prod=$href_prod

        if [ $href_prod -lt 4 ] ; then
          echo "WARNING: HREF Products = " $href_prod " which < 4, some products are missing, exit METplus execution !!!"
          export err=$?; err_chk
          exit
        fi

      fi
 
      fhr=$((fhr+1))  
  done

done

echo "All HREF ensemble products files in Alaska are available. Continue  ..."


















