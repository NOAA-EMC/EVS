      program diffpcp
!
! BASED ON DIFFPCP FROM VERF_PRECIP AND MODIFIED
!
!$$$  MAIN PROGRAM DOCUMENTATION BLOCK
!                .      .    .                                       .
! MAIN PROGRAM: ADDPCP
!  
!   Programmer: Mallory Row
!
! ABSTRACT: program to read in two precip files, then subtracts the two
! 
! nam_2007060712_000_012  ! Input #1
! nam_2007060712_012_024  ! Input #2
! nam_2007060712_000_030  ! output file
!
! ATTRIBUTES:
!   LANGUAGE: Intel FORTRAN 90
!
!$$$
      integer jpds(200),jgds(200),kpds1(200),kpds2(200),kgds(200)
      integer kpdso(200),kgdso(200)
      parameter(ji=5000*2000)
      logical*1 bitdiff(ji),bit1(ji),bit2(ji)
      real diff(ji),pcp1(ji), pcp2(ji)
      character*200 infile1,infile2,prefx,outfile
      character*18 datstr
      character*3 timeflag
      character*2 orflag
      INTEGER IDAT(8),JDAT(8)
      REAL RINC(5)

! Read agrument
nargs = iargc()              !  iargc() - number of arguments
if (nargs.lt.3) then
  write(*,*)'usage : diffpcp infile1 infile2 outfile'
  stop
endif

call getarg(1,infile1)
call getarg(2,infile2)
call getarg(3,outfile)


!
!   Get precip.  ETA and most others have pds(5)=61, but AVN and MRF
!   have pds(5)=59 (precip rates), and in those cases we should 
!   add up the files and then divde the result by the number of files
!   that contributed to the sum (i.e. calculate the average precip rate
!   during the entire period
!

      jpds=-1
      jgds=-1
      call baopenr(11,infile1,ierr)
      if (ierr .ne. 0) write(6,*)" failed to open ", infile1
      call getgb(11,0,ji,0,jpds,jgds,kf1,kr,kpds1,kgds,bit1,pcp1,iret1)
      write(6,*) 'getgb ', infile1, 'kf1= ',kf1, '  iret=', iret1
      call baopenr(12,infile2,ierr)
      call getgb(12,0,ji,0,jpds,jgds,kf2,kr,kpds2,kgds,bit2,pcp2,iret2)
      write(6,*) 'getgb ', infile2, 'kf2= ',kf2, ' iret=', iret2

!
!   Calculate the difference (subtract file1 from file2):
!
      if (iret1.ne.0 .or. iret2.ne.0)                                         &
          STOP 'iret1 and/or iret2 not zero!'

!
! Check to see if the two files have the same length:
      if (kf1.ne.kf2)                                                         &
          STOP 'File lengths (kf1,kf2) differ!  STOP.'

!
! Check to see if the two time stamps are identical:
      if (kpds1(21).ne.kpds2(21) .or. kpds1( 8).ne.kpds2( 8) .or.             &
          kpds1( 9).ne.kpds2( 9) .or. kpds1(10).ne.kpds2(10) .or.             &
          kpds1(11).ne.kpds2(11) .or. kpds1(12).ne.kpds2(12) .or.             &
          kpds1(13).ne.kpds2(13)) then
        write(6,30)                                                           &
         (kpds1(21)*100+kpds1(8))/100-1, mod(kpds1(8),100),                   &
          kpds1(9),kpds1(10),kpds1(11),kpds1(12),kpds1(13),                   &
         (kpds2(21)*100+kpds2(8))/100-1, mod(kpds2(8),100),                   &
          kpds2(9),kpds2(10),kpds2(11),kpds2(12),kpds2(13)
 30     format('Time stamps differ! Date1=',7i2.2,' Date2=',7i2.2, '  STOP')
        stop
      endif

        write(6,*) 'Infile1 Time range 1 : kpds1(14)=', kpds1(14)
        write(6,*) 'Infile1 Time range 2 : kpds1(15)=', kpds1(15)
        write(6,*) 'Infile2 Time range 1 : kpds2(14)=', kpds2(14)
        write(6,*) 'Infile2 Time range 2 : kpds2(15)=', kpds2(15)

! Check to see if the two 'time range 1' are identical:
      if (kpds1(14).ne.kpds2(14)) then
        write(6,*) 'Time range 1 differ: kpds1(14)=', kpds1(14),              &
          ' kpds2(14)=', kpds2(14),'  STOP'
        stop
      endif

! Check 'time range 2' to make sure that kpds2(15) > kpds1(15):

      if (kpds1(15).ge.kpds2(15)) then
        write(6,*) 'Time range 2 problem: kpds1(15)=', kpds1(15),             &
          ' kpds2(15)=', kpds2(15),'  STOP'
        stop
      endif

      kpdso=kpds2
      kgdso=kgds
!
      kpdso(14) = kpds1(15)

      do 40 N=1,kf1
        bitdiff(N)=bit2(N).and.bit1(N)
        if (bitdiff(N)) then
          diff(N)=pcp2(N)-pcp1(N)
          write(54,54) n, diff(n), pcp2(n), pcp1(n)
 54       format(i8,2x,3(3x,f8.3))
        else
          diff(N)=0.
        endif
 40   continue
!
 999  continue
!
! set unit decimal scale factor
      kpdso(22) = 1

! set output time stamp
         WRITE(DATSTR,50) (KPDSO(21)-1)*100+KPDSO(8),KPDSO(9),                &
           KPDSO(10),KPDSO(11),KPDSO(14),KPDSO(15)
 50      FORMAT(I4.4,3I2.2,'_',I3.3,'_',I3.3)
      OUTFILE = outfile
      CALL BAOPEN(51,OUTFILE,ierr)
      call putgb(51,kf1,kpdso,kgdso,bitdiff,diff,iret)
      if (iret.eq.0) then
        write(6,*) 'PUTGB successful, iret=', iret, 'for ', outfile
      else
        write(6,*) 'PUTGB failed!  iret=', iret, 'for ', outfile
      endif
      CALL BACLOSE(51,ierr)
      CALL W3TAGE('DIFFPCP ')
!
      stop

 end
