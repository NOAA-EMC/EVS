program jma_merge

!-----------------------------------------------------------------
! Merges JMA NH and SH forecast data into one single forecast file
! Fanglin Yang, June 2013

real, parameter :: res=2.5                          !data resolution
integer, parameter :: nptz=360/res                  !number of points for each longitude circle
integer, parameter :: npt=(180/res+1)*nptz          !number of points for global array
integer, parameter :: npth=(90/res+1)*(360/res)     !number of points for hemispheric array
integer, parameter :: mmax=200000                   !maximum number of points to unpack

real          :: varn(mmax), vars(mmax), varg(npt)
logical*1     :: lb(mmax)
character*200 :: inputn, inputs, output
integer       :: iargc
external       :: iargc
integer        :: nargs       ! number of command-line arguments
character*1000  :: argument    ! space for command-line argument
integer       :: jpds(200), jgds(200)
integer       :: kpds(200), kgds(200)

nargs = iargc()              ! iargc() - number of arguments
if (nargs.lt.3) then
   write(*,*) 'usage : postjma.x inputn inputs output'
   stop
endif
call getarg(1, inputn)
call getarg(2, inputs)
call getarg(3, output)
print*, "NH input: ", inputn
print*, "SH input:", inputs
print*, "Merged output", output

call baopenr(11, trim(inputn), iret)
if (iret .ne. 0) then
   write(6,*) 'failed to open ', inputn
   stop
endif
call baopenr(12, trim(inputs), iret)
if (iret .ne. 0) then
   write(6,*) 'failed to open ', inputs
   stop
endif
call baopen(13, trim(output), iret)
if (iret .ne. 0) then
   write(6,*) 'failed to open ', output
   stop
endif

j = -1
do while (j /= 0)
   jgds = -1
   jpds = -1
   call getgb(11, 0, mmax, j, jpds, jgds, kf, k, kpds, kgds, lb, varn, iretn)
   if (iretn.ne.0) then
       print *, "iretn=",iretn, "STOP" !reached end of record or incorrect file
       stop
   endif

   jpds = -1
   jgds = -1
   jpds(5) = kpds(5)
   jpds(6) = kpds(6)
   jpds(7) = kpds(7)
   call getgb(12, 0, mmax, -1, jpds, jgds, mf, m, kpds, kgds, lb, vars, irets)
   if (irets.ne.0) then
       print *, "irets=",irets, "STOP" !reached end of record or incorrect file
       stop
   endif

   if (iretn.eq.0 .and. irets.eq.0) then
      do i = 1, npth
         varg(i) = varn(i)
      enddo
      do i = 1, npth-nptz
         varg(npth+i) = vars(i+nptz)   !for SH, skip points at the equator
      enddo

      kgds(3) = int(180/res) + 1
      kgds(4) = 90000
      kgds(7) = -90000
      call putgb(13, npt, kpds, kgds, lb, varg, iret)
   endif

   j = j - 1
end do

call baclose(11, iret)
call baclose(12, iret)
call baclose(13, iret)
CALL W3TAGE('jma_merge ')

end

