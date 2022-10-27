program jma_merge                                        

!-----------------------------------------------------------------
! Merges JMA NH and SH forecast data into one single forecast file
! Fanglin Yang, June 2013

real, parameter :: res=2.5                          !data resolution
integer, parameter :: nptz=360/res                  !number of points for each longitude cicrle
integer, parameter :: npt=(180/res+1)*nptz          !number of points for global array
integer, parameter :: npth=(90/res+1)*(360/res)     !number of points for hemispheric array
integer, parameter :: mmax=200000                   !maximum number of points to unpack 

real          :: varn(mmax), vars(mmax), varg(npt)
logical*1     :: lb(mmax)
character*200 :: inputn,inputs,output    
integer       :: iargc
external       :: iargc
integer        :: nargs       ! number of command-line arguments
character*1000  :: argument    ! space for command-line argument
integer       :: jpds(200),jgds(200)
integer       :: kpds(200),kgds(200)
 
 nargs = iargc()              !  iargc() - number of arguments
 if (nargs.lt.3) then
   write(*,*)'usage : postjma.x inputn inputs output'
   stop
 endif
 call getarg(1,inputn)
 call getarg(2,inputs)
 call getarg(3,output)
! call getarg(1,argument)      
! read(argument,*) inputn    
! call getarg(2,argument)      
! read(argument,*) inputs      
! call getarg(3,argument)      
! read(argument,*) output      
 print*, inputn, inputs, output


 call baopenr(11,trim(inputn),iret)
 if (iret .ne. 0) write(6,*)" failed to open ", inputn  
 call baopenr(12,trim(inputs),iret)
 if (iret .ne. 0) write(6,*)" failed to open ", inputs  
 call baopen(13,trim(output),iret)
 if (iret .ne. 0) write(6,*)" failed to open ", output  
 if (iret .ne. 0) goto 200    

j=-1
10 continue

     jgds=-1; jpds=-1
     call getgb(11,0,mmax,j,jpds,jgds,kf,k,kpds,kgds,lb,varn,iretn)
!     print*, "iretn=",iretn, k, kf, "kpds: ",(kpds(i),i=5,15), "kgds: ",(kgds(i),i=1,10)
     if(iretn.ne.0) goto 100   !reached end of record or incorrect file 

     jpds=-1; jgds=-1
     jpds(5)=kpds(5)
     jpds(6)=kpds(6)
     jpds(7)=kpds(7)
     call getgb(12,0,mmax,-1,jpds,jgds,mf,m,kpds,kgds,lb,vars,irets)
!     print*, "irets=",irets, m, kf, "kpds: ",(kpds(i),i=5,15), "kgds: ",(kgds(i),i=1,10)

  if(iretn.eq.0 .and. irets.eq.0) then
     do i=1,npth
      varg(i)=varn(i)
     enddo
     do i=1,npth-nptz    
      varg(npth+i)=vars(i+nptz)   !for SH, skip points at the equator  
     enddo

     kgds(3)=int(180/res)+1
     kgds(4)=90000
     kgds(7)=-90000
     call putgb(13,npt,kpds,kgds,lb,varg,iret)
  endif

j=j-1
goto 10

100  call baclose(11,iret)
     call baclose(12,iret)
     call baclose(13,iret)
CALL W3TAGE('jma_merge ')
200  end

