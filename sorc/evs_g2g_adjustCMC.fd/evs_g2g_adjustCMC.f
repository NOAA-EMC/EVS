        use grib_mod
C  raw data
       real,allocatable,dimension(:,:) :: gfsa,gefs,cmca,cmce,cmce_adj

       character*10 gdss(400)
       integer GRIBID, kgdss(200), lengds,im,jm,jf
       character*60 gefsmbr, gfsanl, cmcembr, cmcanl, cmcembr_adj
        character*60 gefs_file_list, cmce_file_list
       integer kpd1(100),kpd2(100),kpd12_gefs(100),kpd12_cmce(100),
     +    kpd11_gefs(100),  kpd11_cmce(100), kpd10_gefs(100),
     +    kpd10_cmce(100) 

       type(gribfield) :: gfld_gfsanl,gfld_cmcanl,gfld_gefs,gfld_cmce

       !GRIBID=227
       GRIBID=3

       kpd1(1)=3
       kpd2(1)=5
       kpd12_gefs(1)=50000
       kpd12_cmce(1)=5
       kpd11_gefs(1)=0
       kpd11_cmce(1)=-4
       kpd10_gefs(1)=100
       kpd10_cmce(1)=100


       kpd1(2)=3
       kpd2(2)=5
       kpd12_gefs(2)=100000
       kpd12_cmce(2)=1
       kpd11_gefs(2)=0
       kpd11_cmce(2)=-5
       kpd10_gefs(2)=100
       kpd10_cmce(2)=100


       kpd1(3)=0
       kpd2(3)=0
       kpd12_gefs(3)=85000
       kpd12_cmce(3)=85
       kpd11_gefs(3)=0
       kpd11_cmce(3)=-3
       kpd10_gefs(3)=100
       kpd10_cmce(3)=100


       kpd1(4)=2
       kpd2(4)=2
       kpd12_gefs(4)=25000
       kpd12_cmce(4)=25
       kpd11_gefs(4)=0
       kpd11_cmce(4)=-3
       kpd10_gefs(4)=100
       kpd10_cmce(4)=100


       kpd1(5)=2
       kpd2(5)=3
       kpd12_gefs(5)=25000
       kpd12_cmce(5)=25
       kpd11_gefs(5)=0
       kpd11_cmce(5)=-3
       kpd10_gefs(5)=100
       kpd10_cmce(5)=100



       kpd1(6)=2
       kpd2(6)=2
       kpd12_gefs(6)=85000
       kpd12_cmce(6)=85
       kpd11_gefs(6)=0
       kpd11_cmce(6)=-3
       kpd10_gefs(6)=100
       kpd10_cmce(6)=100


       kpd1(7)=2
       kpd2(7)=3
       kpd12_gefs(7)=85000
       kpd12_cmce(7)=85
       kpd11_gefs(7)=0
       kpd11_cmce(7)=-3
       kpd10_gefs(7)=100
       kpd10_cmce(7)=100


       kpd1(8)=3
       kpd2(8)=1
       kpd12_gefs(8)=0
       kpd12_cmce(8)=0
       kpd11_gefs(8)=0
       kpd11_cmce(8)=0
       kpd10_gefs(8)=101
       kpd10_cmce(8)=101


       kpd1(9)=3
       kpd2(9)=5
       kpd12_gefs(9)=70000
       kpd12_cmce(9)=7
       kpd11_gefs(9)=0
       kpd11_cmce(9)=-4
       kpd10_gefs(9)=100
       kpd10_cmce(9)=100


       kpd1(10)=0
       kpd2(10)=0
       kpd12_gefs(10)=50000
       kpd12_cmce(10)=5
       kpd11_gefs(10)=0
       kpd11_cmce(10)=-4
       kpd10_gefs(10)=100
       kpd10_cmce(10)=100


       kpd1(11)=2
       kpd2(11)=2
       kpd12_gefs(11)=10
       kpd12_cmce(11)=10
       kpd11_gefs(11)=0
       kpd11_cmce(11)=0
       kpd10_gefs(11)=103
       kpd10_cmce(11)=103

       kpd1(12)=2
       kpd2(12)=3
       kpd12_gefs(12)=10
       kpd12_cmce(12)=10
       kpd11_gefs(12)=0
       kpd11_cmce(12)=0
       kpd10_gefs(12)=103
       kpd10_cmce(12)=103
  


        read (*,*) gefs_file_list, cmce_file_list


cc     RAP has one-hour accumu precip, so only one file is used
cc     NAM has no one-hour accumu precip, so two files are needed

       if(GRIBID.eq.255) then   !For MOSAIC 255 grid
         im=1401
         jm=701
         jf=im*jm
       else
         call makgds(GRIBID, kgdss, gdss, lengds, ier)
         im=kgdss(2)
         jm=kgdss(3)
         jf=kgdss(2)*kgdss(3)
       end if

       !write(*,*) 'jf=',jf

       allocate(gfsa(10,jf)) 
       allocate(cmca(10,jf))
       allocate(gefs(10,jf))
       allocate(cmce(10,jf)) 
       allocate(cmce_adj(10,jf)) 
 
       
        open(1, file=gefs_file_list, status='old')
        open(2, file=cmce_file_list, status='old')

        call baopenr(8,'gfsanl',ierr8)
        call baopenr(9,'cmcanl',ierr9)
        !write(*,*) 'open ierr8, ierr9=', ierr8, ierr9
 
       do 100 i = 1,12

          jpd1=kpd1(i)
          jpd2=kpd2(i)
          

          gfld_gfsanl%fld=0.0
          gfld_cmcanl%fld=0.0


          jpd12=kpd12_gefs(i)
          jpd11=kpd11_gefs(i)
          jpd10=kpd10_gefs(i)

          jpdtn=0
          call readGB2(8,jpdtn,jpd1,jpd2,jpd10,jpd11,jpd12,
     +      gfld_gfsanl,iret)
          if ( iret.eq.0) then
           gfsa(i,:) = gfld_gfsanl%fld(:)
          else
           !write(*,*) 'gfsanl read iret=', iret
           goto 100
          end if

          jpd12=kpd12_cmce(i)
          jpd11=kpd11_cmce(i)
          jpd10=kpd10_cmce(i)

          jpdtn=1
          call readGB2(9,jpdtn,jpd1,jpd2,jpd10,jpd11,jpd12,
     +      gfld_cmcanl,iret)
          if ( iret.eq.0) then
           cmca(i,:) = gfld_cmcanl%fld(:)
          else
           !write(*,*) 'cmcanl read iret=', iret
           goto 100
          end if

100       continue

          call baclose(8,ierr)
          call baclose(9,ierr)

        !write(*,*) 'read gfs and cmc analysis done'

      do 2000  m =1,20
          read (1, *) gefsmbr
          read (2, *) cmcembr

        cmcembr_adj=trim(cmcembr)//'.adj' 

        !write (*,*) trim(gefsmbr) 
        !write (*,*) trim(cmcembr)
        !write (*,*) trim(cmcembr_adj)
 
        ngefs=10+m
        ncmce=30+m
        nadj=50+m

        call baopenr(ngefs,gefsmbr,ierr)
        if (ierr.ne.0) then
         write(*,*) ngefs, trim(gefsmbr),' open gefs error'
        end if
        call baopenr(ncmce,cmcembr,ierr)
        if (ierr.ne.0) then
         write(*,*) ncmce, trim(cmcembr),' open cmce error'
        end if

        call baopen(nadj,cmcembr_adj,ierr)
        if (ierr.ne.0) then
         write(*,*) nadj, ' open cmcembr_adj error'
        end if



       do 1000 i = 1,12 
          jpd1=kpd1(i)
          jpd2=kpd2(i)


          gfld_gefs%fld=0.0
          gfld_cmce%fld=0.0

          jpd12=kpd12_gefs(i)
          jpd11=kpd11_gefs(i)
          jpd10=kpd10_gefs(i)

          jpdtn=1
          call readGB2(ngefs,jpdtn,jpd1,jpd2,jpd10,jpd11,jpd12,
     +      gfld_gefs,iret)
          if ( iret.eq.0) then
            gefs(i,:) = gfld_gefs%fld(:)
          else
           !write(*,*) 'gefsmbr read iret=', iret
           goto 1000
          end if

          jpd12=kpd12_cmce(i)
          jpd11=kpd11_cmce(i)
          jpd10=kpd10_cmce(i)

          jpdtn=1
          call readGB2(ncmce,jpdtn,jpd1,jpd2,jpd10,jpd11,jpd12,
     +      gfld_cmce,iret)
          if ( iret.eq.0) then
            cmce(i,:) = gfld_cmce%fld(:)
          else
           !write(*,*) 'cmcembr read iret=', iret
           goto 1000
          end if

          
          do k=1,jf
       
            if(gfsa(i,k).ne.-9999.99.and.cmca(i,k).ne.-9999.99) then
               diff=gfsa(i,k)-cmca(i,k)
            else
               diff=0.0
               gfsa(i,k)=-9999.99
            end if
            if ( cmce(i,k).ne.-9999.99) then
              cmce_adj(i,k) = cmce(i,k) + diff
            else
              cmce_adj(i,k) = -9999.99
            end if
          end do


           !write(*,*) 'm=',m,' i=',i
           !do k = 5011, 5020
           !  write(*,'(5f10.2)')gfsa(i,k),cmca(i,k),gefs(i,k),
     +     !      cmce(i,k),cmce_adj(i,k)
           !end do

           gfld_cmce%fld(:)=cmce_adj(i,:)
           call putgb2(nadj,gfld_cmce,iret)
           if (iret .ne. 0) then
            write (*,*) iret, ' putgb2 to nadj error' 
           end if
           !write(*,*) 'putgb2 for ',m,i,' done' 

1000    continue

          call baclose(ngefs,ierr)
          call baclose(ncmce,ierr)
          call baclose (nadj,ierr)

2000    continue
          close (1)
          close (2)       
      stop
      end


      subroutine readGB2(iunit,jpdtn,jpd1,jpd2,jpd10,jpd11,jpd12,
     +    gfld,iret)

        use grib_mod

        type(gribfield) :: gfld
 
        integer jids(200), jpdt(200), jgdt(200)
        integer jpd1,jpd2,jpd10,jpd12,jpdtn
        logical :: unpack=.true. 

        jids=-9999  !array define center, master/local table, year,month,day, hour, etc, -9999 wildcard to accept any
        jpdt=-9999  !array define Product, to be determined
        jgdt=-9999  !array define Grid , -9999 wildcard to accept any

        jdisc=-1    !discipline#  -1 wildcard 
        jgdtn=-1    !grid template number,    -1 wildcard
        jskp=0      !Number of fields to be skip, 0 search from beginning

        jpdt(1)=jpd1   !Category #     
        jpdt(2)=jpd2   !Product # under this category     
        jpdt(10)=jpd10
        jpdt(11)=jpd11
        jpdt(12)=jpd12

         call getgb2(iunit,0,jskp, jdisc,jids,jpdtn,jpdt,jgdtn,jgdt,
     +        unpack, jskp1, gfld,iret)
         
        return
        end 
       
  
        
       
