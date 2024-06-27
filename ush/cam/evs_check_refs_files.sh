#!/bin/ksh
#**************************************************************************
#  Purpose: check the required input forecast and validation data files
#           for refs stat jobs
#  Last update: 10/30/2023, by Binbin Zhou Lynker@EMC/NCEP
#************************************************************************
set -x

vday=$VDATE

typeset -Z2 vhr

if [ $VERIF_CASE = grid2obs ] || [ $VERIF_CASE = spcoutlook ] ; then
   echo "Checking prepbufr files...." 
   
   missing=0 
   for vhr in 00 01 02 03 04 05 06 07 08  09 10 11 12 13 14 15 16 17 18 19 20  21 22 23 ; do
      if [ ! -s $COMINobsproc/rap.${vday}/rap.t${vhr}z.prepbufr.tm00 ] ; then
         missing=$((missing + 1 ))
         echo  "WARNING: $COMINobsproc/rap.${vday}/rap.t${vhr}z.prepbufr.tm00 is missing"
      fi
   done
   echo "Missing prepbufr files = " $missing
   if [ $missing -eq 24  ] ; then
      echo "WARNING: All of the preppbufr files are missing."
      export verif_all=no
   fi

fi


if [ $VERIF_CASE = precip ] ; then
   echo "Checking precip files...." 

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
      ccpa=$COMINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${vhr}z.01h.hrap.conus.gb2
      if [ ! -s $ccpa ] ; then
         missing=$((missing + 1 ))
         echo "WARNING: $ccpa is missing"
      fi
   done
   echo "Missing ccpa01h files = " $missing
   if [ $missing -eq 24  ] ; then
      echo "WARNING: All of the ccpa files are missing"
      export verif_precip=no
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
      ccpa=$COMINccpa/ccpa.${init}/${cyc_dir}/ccpa.t${vhr}z.03h.hrap.conus.gb2
      if [ ! -s $ccpa ] ; then
         missing=$((missing + 1 ))
	     echo "WARNING: $ccpa is missing"
      fi
   done
   echo "Missing ccpa03h files = " $missing
   if [ $missing -eq 8  ] ; then
      echo "WARNING: All of the ccpa03h files are missing"
      export verif_precip=no
   fi

   missing=0
   for vhr in 12 ; do
      if [ ! -s $COMINccpa/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 ] ; then
         missing=$((missing+1))
         echo "WARNING: $COMINccpa/ccpa.${vday}/12/ccpa.t12z.06h.hrap.conus.gb2 is missing"
      elif [ ! -s $COMINccpa/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 ] ; then
         missing=$((missing+1))
         echo "WARNING: $COMINccpa/ccpa.${vday}/06/ccpa.t06z.06h.hrap.conus.gb2 is missing"
      elif [ ! -s $COMINccpa/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 ] ; then
         missing=$((missing+1))
         echo "WARNING: $COMINccpa/ccpa.${vday}/00/ccpa.t00z.06h.hrap.conus.gb2 is missing"
      elif [ ! -s $COMINccpa/ccpa.${prev}/18/ccpa.t18z.06h.hrap.conus.gb2 ] ; then
         missing=$((missing+1))
         echo "WARNING: $COMINccpa/ccpa.${prev}/18/ccpa.t18z.06h.hrap.conus.gb2 is missing"
      fi
   done
   echo "Missing ccpa06h files = " $missing
   if [ $missing -ge 1  ] ; then
      echo "WARNING: At least one of the ccpa06h files are missing"
      export verif_precip=no
   fi

   accum=01
   missing=0
   for vhr in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 ; do
      mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
      if [ ! -s $mrms ] ; then
         missing=$((missing+1))
         echo "WARNING: $mrms is missing"
      fi
   done
   echo "Missing mrms01h files = " $missing
   if [ $missing -eq 24  ] ; then
      echo "WARNING: All of mrms01h files are missing"
      export verif_precip=no
   fi

   accum=03
   missing=0
   for vhr in 00 03 06 09 12 15 18 21 ; do
      mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
      if [ ! -s $mrms ] ; then
         missing=$((missing+1))
         echo "WARNING: $mrms is missing"
      fi
   done
   echo "Missing mrms03h files = " $missing
   if [ $missing -eq 8  ] ; then
      echo "WARNING: All of mrms03h files are missing"
      export verif_precip=no
   fi

   accum=24
   missing=0
   for vhr in 00 06 12 18 ; do
      mrms=$DCOMINmrms/MultiSensor_QPE_${accum}H_Pass2_00.00_${vday}-${vhr}0000.grib2.gz
      if [ ! -s $mrms ] ; then
         missing=$((missing+1))
         echo "WARNING: $mrms is missing"
      fi
   done
   echo "Missing mrms24h files = " $missing
   if [ $missing -eq 4  ] ; then
      echo "WARNING: All of the mrms24h files are missing"   
      export verif_precip=no
   fi
fi

echo "Checking REFS members files ..." 
for domain in conus ak ; do
 refs_mbrs=0
 for obsv_cyc in 00 03 06 09 12 15 18 21 ; do 
   for fhr in 03 06 09 12 15 18 21 24 27 30 33 36 39 42 45 48 51 54 57 60 ; do 
      fcst_time=`$NDATE -$fhr ${vday}${obsv_cyc}`
      fday=${fcst_time:0:8}
      fcyc=${fcst_time:8:2}
      if [ $fcyc = 00 ] || [ $fcyc = 06 ] || [ $fcyc = 12 ] || [ $fcyc = 18 ] ; then

          if [ $fhr -le 48 ] ; then

	   for mb in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 ; do
               refs=$COMINrefs/refs.${fday}/verf_g2g/refs.m${mb}.t${fcyc}z.${domain}.f${fhr}
               if [ -s $refs ] ; then
                  refs_mbrs=$((refs_mbrs+1))
               else
                  echo "WARNING: $refs is missing"
               fi
	    done

	  elif [ $fhr -le 51 ] && [ $fhr -gt 48 ] ; then
      
            for mb in 01 02 03 04 05 06 07 08 09 10 11 12 ; do
	       refs=$COMINrefs/refs.${fday}/verf_g2g/refs.m${mb}.t${fcyc}z.${domain}.f${fhr}
               if [ -s $refs ] ; then
	          refs_mbrs=$((refs_mbrs+1))
	       else
	          echo "WARNING: $refs is missing"
               fi
            done		    
          
          elif [ $fhr -gt 51 ] ; then

             for mb in 01 02 03 04 05 06 ; do
                refs=$COMINrefs/refs.${fday}/verf_g2g/refs.m${mb}.t${fcyc}z.${domain}.f${fhr}
                if [ -s $refs ] ; then
                   refs_mbrs=$((refs_mbrs+1))
                else
                  echo "WARNING: $refs is missing"
                fi
            done
	    
          fi  

         if [ $refs_mbrs -lt 14 ] ; then
            echo "WARNING: REFS members at all cycles and fcst hours = " $refs_mbrs " which < 14 "
            REFS:export verif_precip=no
            REFS:export verif_snowfall=no
            REFS:export verif_all=no
         fi
      fi
   done
 done
done

for domain in conus ak ; do
 refs_prod=0      	
 for obsv_cyc in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23  ; do 
    typeset -Z2 fhr
    fhr=01
    while [ $fhr -le 48 ] ; do 
       fcst_time=`$NDATE -$fhr ${vday}${obsv_cyc}`
       fday=${fcst_time:0:8}
       fcyc=${fcst_time:8:2}
       if [ $fcyc = 00 ] || [ $fcyc = 06 ] || [ $fcyc = 12 ] || [ $fcyc = 18 ] ; then
          for  prod in mean prob eas pmmn lpmm avrg ; do 
             refs=$COMINrefs/refs.${fday}/ensprod/refs.t${fcyc}z.${domain}.${prod}.f${fhr}.grib2
	         if [ -s $refs ] ; then
                refs_prod=$((refs_prod+1))
	         else
                echo "WARNING: $refs is missing"		 
             fi	    
          done
          if [ $refs_prod -eq 0 ] ; then
            echo "WARNING: REFS Products at all cycsand fhrs = " $refs_prod = 0", no one product existing "
            REFS:export verif_precip=no
            REFS:export verif_snowfall=no
            REFS:export verif_all=no
          fi
      fi
      fhr=$((fhr+1))  
   done
 done
done
