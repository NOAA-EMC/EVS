C  raw data
       use grib_mod
       real,allocatable,dimension(:,:) :: apcp3_09,
     +                          apcp3_15,apcp3_12    

       integer iyr,imon,idy,ihr
       character*50 gdss(400)
       integer IENS, GRIDID, kgdss(200), lengds,im,jm,km,jf
       character*40 filename09(30), filename12(30),filename15(30)
       integer iunit,ounit, jpdt_09(100), jpdt_12(100), jpdt_15(100)
       integer idsect_09(100), idsect_12(100), idsect_15(100)
       type(gribfield) :: gfld
       character*2 cyc, fhr12(30),fhr09(30), fhr15(30) 
       character*3  pair, snow,fog
       character*8 mdl 
       integer ifhr12

        data (fhr12(i),i=1,28)
     +  /'03','06','09','12','15','18','21','24','27','30','33',
     +   '36','39','42','45','48','51','54','57','60','63','66',
     +   '69','72','75','78','81','84'/

        data (fhr09(i),i=1,28)
     +  /'06','09','12','15','18','21','24','27','30','33','36',
     +   '39','42','45','48','51','54','57','60','63','66','69',
     +   '72','75','78','81','84','87'/

        data (fhr15(i),i=1,28)
     +  /'03','03','06','09','12','15','18','21','24','27','30',
     +   '33','36','39','42','45','48','51','54','57','60','63',
     +   '66','69','72','75','78','81'/

       GRIDID=212          
       read(*,*) nfhr 
       write(*,*)'nfhr=', nfhr
       if(GRIDID.eq.255) then   !For NARRE 13km RAP grid#130
         im=1799
         jm=1059
         jf=im*jm
       else
         call makgds(GRIDID, kgdss, gdss, lengds, ier)
         im=kgdss(2)
         jm=kgdss(3)
         jf=kgdss(2)*kgdss(3)
       end if

       write(*,*) 'jf=',jf

       allocate(apcp3_09(jf,nfhr))
       allocate(apcp3_12(jf,nfhr))
       allocate(apcp3_15(jf,nfhr))
       
        jpdt_09=-1 
        jpdt_12=-1 
        jpdt_15=-1
        idsect_09=-1 
        idsect_12=-1 
        idsect_15=-1

       !do 1000 i=1,nfhr    !fhr(i):00 03 06 09, ....or 00 01 02 03 04 .... 
       do 1000 i=nfhr,nfhr       !fhr(i):00 03 06 09, ....or 00 01 02 03 04 .... 
        filename09(i)='sref.t09z.pgrb212.mean.fhr'//fhr09(i)//'.grib2'
        filename12(i)='sref.t12z.pgrb212.mean.fhr'//fhr12(i)//'.grib2'
        filename15(i)='sref.t15z.pgrb212.mean.fhr'//fhr15(i)//'.grib2'


        iunit09=10
        call baopenr(iunit09,filename09(i) ,ierr)
        write(*,*) 'open ', filename09(i), 'ierr=',ierr

        if (i.ge.2) then
         iunit15=15
         call baopenr(iunit15,filename15(i) ,ierr)
         write(*,*) 'open ', filename15(i), 'ierr=',ierr
        end if

        ifhr12=3*nfhr

ccc  Read APCP
 
        jpdtn=12  
        jpd1=1
        jpd2=8
        jpd10=1
        jpd12=0

        jpd30=-9999
        call readGB2(iunit09,jpdtn,jpd1,jpd2,1,0,jpd30,gfld,iret)
        if (iret.eq.0) then
         apcp3_09(:,i)=gfld%fld(:)
         jpdt_09(:)=gfld%ipdtmpl(:)
         idsect_09(:)=gfld%idsect(:)
        else
         write(*,*)'read file error: ',filename09(i)
        end if

        if (i.ge.2) then
          call readGB2(iunit15,jpdtn,jpd1,jpd2,1,0,jpd30,gfld,iret)
          if (iret.eq.0) then
            apcp3_15(:,i)=gfld%fld(:)
            jpdt_15(:)=gfld%ipdtmpl(:)
            idsect_15(:)=gfld%idsect(:)
          else
            write(*,*)'read file error: ',filename15(i)
          end if
        end if

        jpdt_12=jpdt_09
        idsect_12=idsect_09
        idsect_12(9)=12
        jpdt_12(9)=ifhr12-3

        if (i.eq.1) then
          apcp3_12(:,i)=apcp3_09(:,i)
        else
          apcp3_12(:,i)=(apcp3_09(:,i)+apcp3_15(:,i))/2.0 
        end if

        do k=1,30
         write(*,'(i10,6i5)')k,idsect_09(k),idsect_12(k),idsect_15(k),
     +        jpdt_09(k), jpdt_12(k), jpdt_15(k)
        end do


        call baclose(iunit09,ierr)
        call baclose(iunit15,ierr)
 
        iunit12=20
        call baopen(iunit12,filename12(i),ierr)
        if (ierr.ne.0) then
           write(*,*) 'open file error', filename12(i)
        end if
 
        gfld%fld(:)=apcp3_12(:,i)
        !do j=1,jf 
        !  write(*,*)j, apcp3_09(j,i), apcp3_15(j,i),gfld%fld(j)
        !end do


        gfld%idsect(9)=idsect_12(9)
        gfld%ipdtmpl(9)=jpdt_12(9)

        call putgb2(iunit12,gfld,iret)
        if (iret .ne. 0) then
         write (*,*) iret, ' putgb2  error'
        end if

        call baclose(iunit12,ierr)

1000  continue

      stop
      end


      subroutine readGB2(igrb2,jpdtn,jpd1,jpd2,jpd10,jpd12,jpd30,
     +                   gfld,iret)

        use grib_mod

        type(gribfield) :: gfld 
 
        integer jids(200), jpdt(200), jgdt(200)
        integer jpd1,jpd2,jpdtn
        logical :: unpck=.true. 

C        write(*,*) 'jpdtn,jpd1,jpd2,jpd10,jpd12,jpd30=',
C     +     jpdtn,jpd1,jpd2,jpd10,jpd12,jpd30

        jids=-9999  !array define center, master/local table, year,month,day, hour, etc, -9999 wildcard to accept any
        jpdt=-9999  !array define Product, to be determined
        jgdt=-9999  !array define Grid , -9999 wildcard to accept any

        jdisc=-1    !discipline#  -1 wildcard 
        jgdtn=-1    !grid template number,    -1 wildcard 
        jskp=0      !Number of fields to be skip, 0 search from beginning
        ifile=0

        jpdt(1)=jpd1   !Category #     
        jpdt(2)=jpd2   !Product # under this category     
        jpdt(10)=jpd10
        if(jpd10.eq.100) then
           jpdt(12)=jpd12*100   !pressure level     
        else
           jpdt(12)=jpd12
        end if

        jpdt(30)=jpd30  !Time range (1 hour, 3 hr etc)
        
         call getgb2(igrb2,ifile,jskp,jdisc,jids,jpdtn,jpdt,jgdtn,jgdt,
     +        unpck, jskp1, gfld,iret)

        return
        end 
         
