      program pcpconform

! TAKEN FROM VERF_PRECIP FOR USE IN EVS GLOBAL_DET ATMOS
!
! the program reads in a precip grib file and convert it to 'regular'
! GRIB format, i.e. parameter is No. 61 (APCP) in GRIB1 Table 2.
!
      parameter(lmax=10000000)
!
      dimension f1(lmax), f2(lmax)
      integer ipopt(20), jpds(25), jgds(22), kpds(25), kgds(22)
      logical*1 bit(lmax) 
      character arg*256,file1*200, file2*200, model*20
!
      call getarg(1,arg)
      model=trim(arg)
      lmodel=len_trim(model)
!
      call getarg(2,arg)
      file1=trim(arg)
      len1=len_trim(file1)
!
      call getarg(3,arg)
      file2=trim(arg)
      len2=len_trim(file2)
!
! read in the input precip file using getgb:
!
      write(6,*) 'file1=', file1(1:len1)
      call baopenr(11,file1(1:len1),ibaret) 
      call baopenw(51,file2,ibaret)
!
      jpds=-1
      call getgb(11,0,lmax,-1,jpds,jgds,kf,k,kpds,kgds,bit,f1,iret)       
      write(6,*) 'finished getgb, ibaret=', ibaret, ' iret=', iret
!
      if (model(1:3).eq.'gfs') then
        if (kpds(5).ne.59) then
          write(6,*) 'KPDS(5)=', kpds(5),' for ',model, ' STOP!'
          stop
        endif
!
        kpds(5)=61
        dt = float(kpds(15)-kpds(14))*3600.
        f2 = f1*dt
! Change time range indicator from '3' (average) to '4' (accumulated
!   from t1 to t2):
        kpds(16)=4
! The original GFS precip rate (kg/m^2/s) has a Decimal Scaling factor of 6.  
! This is way too high when we're converting the value to APCP.  When testing
! the (3072 x 1536) GFS para output (Jan-Feb 2014), this leads to occasional
! errors in the output (no errors shown by putgb, but "missing end section ..." 
! msg from wgrib and "GRIB header not found in scanning between records ..." 
! from gribscan.
        kpds(22)=3

      elseif (model(1:3).eq.'dwd') then
! 2014/7/1
! DWD precip changed from GRIB1 to GRIB2 on 2014/6/25, but the GRIB2 parm 
! is not 'precip'.  Coping with it by converting it to GRIB1, then change
! it to the standard 'Table 2, parm 61' for precip.
! Also, after 'cnvgrib -g21', the DWD data somehow has decimal scale factor
! of 0 (even though the field - before I converted it to 'Table 2, parm 61' -
! seemed to have sufficient significant digits after decimal point: 
! "min/max data 0 342.406"), and after resetting the grib1 file to
! 'Table 2, parm 61', it had no significant digits after the decimal point
! "min/max data 0 342").  So, set the decimal scaling factor to 3.  
! 
! 2015/1/26 DWD time info needs special treatment.  Get the starting/ending
!   hour from the last seven characters of the file name 
!
! 2016/10/07 DWD GRIB2 changed again (see verflog.txt for details).  Use
!   cnvgrib2to1.py instead of cnvgrib for conversion.  Still need some
!   tweaking in pcpconform:
!   1) After cnvgrib2to1, kpds(13)=12: the forecast time unit is '12 hours'.  
!      this is inconsistent with kpds(14) and kpds(15):
!      e.g., for dwd_2016100500_012_036.cnvgrib2to1, 
!      kpds(14)=60, kpds(15)=180, should have been '1' and '3' if the unit were
!      indeed '12 hours'.  Seems a bit dangerous simply devide kpds(14/15) by 
!      '60' - what if python library changes in the future in an unpredicted 
!      way?  I'll use the time label in the file name and set time unit as
!      'hour', as in 2015/1/26.
!   2) Change longitude range from [0,-0.25] to [0,359.75]
!   3) Some small negative precip values - set min value to 0.
!   4) Still need to set the decimal scale factor to 3 - other wise the
!      dec scaling factor is 0 and the field has no significant digits after
!      the decimal point. 
!
! 2016/10/25 pygrib not in production and too hard to have it installed in
!   production.  Revert to using cnvgrib.  
!
!   1) Change parameter table to version 2, parameter to 61 (APCP)
!   1) Use the time label in the file name and set time unit as
!      'hour', as in 2015/1/26.
!   2) Change longitude range from [0,-0.25] to [0,359.75]
!   3) Some small negative precip values - set min value to 0.
!   4) Still need to set the decimal scale factor to 3 - other wise the
!      dec scaling factor is 0 and the field has no significant digits after
!      the decimal point. 
!
!  file1=dwd_2016100500_012_036.tmp
!        ----:----|----:----|----:----|
                                 
        read(file1(len1-10:len1-4),'(i3,x,i3)') kpds(14), kpds(15)
        kpds(5)=61     ! parameter: APCP (was '255')
        kpds(13)=1     ! forecast time unit is 'hour' (was '0')
        kpds(16)=4     ! forecast time indiciator accumulation
        kpds(19)=2     ! Version number of parameter table (was '255') 
        kpds(22)=3     ! Decimal scale factor (was '0')
        kgds(8)=359750 ! Longitude of the extreme point; was '-2147233)
        f2=max(0.,f1)
        
      elseif (model(1:5).eq.'ecmwf') then
        if (kpds(5).ne.228) then
         write(6,*) 'KPDS(5)=', kpds(5),' for ',model, ' STOP!'
        endif
!
        kpds(5)=61
! Flip time range #1 and #2:
        kpds(15)=kpds(14)
        kpds(14)=0
! Change time range indicator from '0' (instantaneous) to '4' (accumulated
!   from t1 to t2):
        kpds(16)=4
! Flip latitude range #1 and #2:
        kgdsdum=kgds(4)
        kgds(4)=kgds(7)
        kgds(7)=kgdsdum
!
! Flip the array in the north-south direction; also change precip 
! accumulation unit from m to mm (i.e. kg/m2):
        nx=kgds(2)
        ny=kgds(3)
        k2 = 0
        do 20 j = 1, ny
          do 10 i = 1, nx
            k2 = k2 + 1
            k1 = (ny-j)*nx + i
            f2(k2) = f1(k1)*1000.      
 10       continue
 20     continue
!
! Change PDS(1) from 98 (originating center: ECMWF) to 07 (NCEP).  It seems
! that GEMPAK is hard-wired to flip the ECMWF plots, since the original 
! ECMWF data are oriented north-to-south.
        kpds(1)=7
!
! 'lspa' is #154 on Table 130.  Convert to #61 on Table 2.
      elseif (model(lmodel-3:lmodel).eq.'soil') then 
        kpds(5)=61
        kpds(19)=2
        f2=f1
      endif
!
      call putgb(51,kf,kpds,kgds,bit,f2,iret)      
      write(6,*) 'finished putgb, iret=', iret
!
      close(51)
!
      stop
      end
