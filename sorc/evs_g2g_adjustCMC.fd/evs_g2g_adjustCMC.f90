program generate_NAEFS_ensemble
  use grib_mod
  real, allocatable, dimension(:,:) :: gfsa, gefs, cmca, cmce, cmce_adj
  character(10) :: gdss(400)
  integer, parameter :: GRIBID = 3
  integer, dimension(200) :: kpd1, kpd2, kpd12_gefs, kpd12_cmce, kpd11_gefs, kpd11_cmce, kpd10_gefs, kpd10_cmce
  character(60) :: gefsmbr, gfsanl, cmcembr, cmcanl, cmcembr_adj
  character(60) :: gefs_file_list, cmce_file_list
  type(gribfield) :: gfld_gfsanl, gfld_cmcanl, gfld_gefs, gfld_cmce
  integer :: kpd1_idx, jpdtn, i, m, ngefs, ncmce, nadj, ierr8, ierr9, iret, jf, im, jm, iunit, jids(200), jpdt(200), jgdt(200), jdisc, jgdtn, jskp, jskp1
  real :: diff

  read(*, *) gefs_file_list, cmce_file_list

  if (GRIBID.eq.255) then
    im = 1401
    jm = 701
    jf = im * jm
  else
    call makgds(GRIBID, gdss, lengds, ier)
    im = gdss(2)
    jm = gdss(3)
    jf = gdss(2) * gdss(3)
  end if

  allocate(gfsa(10, jf))
  allocate(cmca(10, jf))
  allocate(gefs(10, jf))
  allocate(cmce(10, jf))
  allocate(cmce_adj(10, jf))

  ! Open gefs and cmce member files to read
  open(1, file=gefs_file_list, status='old')
  open(2, file=cmce_file_list, status='old')

  ! Open gfs and cmc analysis files to read
  call baopenr(8, 'gfsanl', ierr8)
  call baopenr(9, 'cmcanl', ierr9)

  do kpd1_idx = 1, 12
    kpd1 = [3, 3, 0, 2, 2, 2, 2, 2, 3, 3, 0, 2]
    kpd2 = [5, 5, 0, 2, 3, 2, 3, 1, 5, 0, 2, 3]
    kpd12_gefs = [50000, 100000, 85000, 25000, 25000, 85000, 85000, 70000, 50000, 10, 10, 10]
    kpd12_cmce = [5, 1, 85, 25, 25, 85, 85, 7, 5, 10, 10, 10]
    kpd11_gefs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    kpd11_cmce = [-4, -5, -3, -3, -3, -3, -3, -4, -4, 0, 0, 0]
    kpd10_gefs = [100, 100, 100, 100, 100, 100, 100, 100, 100, 101, 100, 103]
    kpd10_cmce = [100, 100, 100, 100, 100, 100, 100, 100, 100, 101, 100, 103]

    jpd1 = kpd1(kpd1_idx)
    jpd2 = kpd2(kpd1_idx)
    jpd12_gefs = kpd12_gefs(kpd1_idx)
    jpd12_cmce = kpd12_cmce(kpd1_idx)
    jpd11_gefs = kpd11_gefs(kpd1_idx)
    jpd11_cmce = kpd11_cmce(kpd1_idx)
    jpd10_gefs = kpd10_gefs(kpd1_idx)
    jpd10_cmce = kpd10_cmce(kpd1_idx)

    ! Read gfs analysis data
    jpdtn = 0
    call readGB2(8, jpdtn, jpd1, jpd2, jpd10, jpd11, jpd12, gfld_gfsanl, iret)
    if (iret.ne.0) then
      write(*, *) 'gfsanl read iret=', iret
      exit
    end if

    ! Read cmc analysis data
    jpdtn = 1
    call readGB2(9, jpdtn, jpd1, jpd2, jpd10, jpd11, jpd12, gfld_cmcanl, iret)
    if (iret.ne.0) then
      write(*, *) 'cmcanl read iret=', iret
      exit
    end if

    ! Store gfs analysis and cmc analysis
    gfsa(kpd1_idx, :) = gfld_gfsanl%fld(:)
    cmca(kpd1_idx, :) = gfld_cmcanl%fld(:)
  end do

  call baclose(8, ierr)
  call baclose(9, ierr)

  ! Process gefs and cmce member files
  do m = 1, 20
    read(1, *) gefsmbr
    read(2, *) cmcembr

    cmcembr_adj = trim(cmcembr) // '.adj'

    ngefs = 10 + m
    ncmce = 30 + m
    nadj = 50 + m

    call baopenr(ngefs, gefsmbr, ierr)
    if (ierr.ne.0) then
      write(*, *) ngefs, trim(gefsmbr), ' open gefs error'
      exit
    end if
    call baopenr(ncmce, cmcembr, ierr)
    if (ierr.ne.0) then
      write(*, *) ncmce, trim(cmcembr), ' open cmce error'
      exit
    end if

    ! Open output file name to write out
    call baopen(nadj, cmcembr_adj, ierr)
    if (ierr.ne.0) then
      write(*, *) nadj, ' open cmcembr_adj error'
      exit
    end if

    do kpd1_idx = 1, 12
      jpd1 = kpd1(kpd1_idx)
      jpd2 = kpd2(kpd1_idx)

      jpd12_gefs = kpd12_gefs(kpd1_idx)
      jpd11_gefs = kpd11_gefs(kpd1_idx)
      jpd10_gefs = kpd10_gefs(kpd1_idx)

      jpd12_cmce = kpd12_cmce(kpd1_idx)
      jpd11_cmce = kpd11_cmce(kpd1_idx)
      jpd10_cmce = kpd10_cmce(kpd1_idx)

      ! Read gefs member files
      jpdtn = 1
      call readGB2(ngefs, jpdtn, jpd1, jpd2, jpd10_gefs, jpd11_gefs, jpd12_gefs, gfld_gefs, iret)
      if (iret.ne.0) then
        write(*, *) 'gefsmbr read iret=', iret
        exit
      end if

      ! Read cmce member files
      jpdtn = 1
      call readGB2(ncmce, jpdtn, jpd1, jpd2, jpd10_cmce, jpd11_cmce, jpd12_cmce, gfld_cmce, iret)
      if (iret.ne.0) then
        write(*, *) 'cmcembr read iret=', iret
        exit
      end if

      ! Calculate the difference between GFS and CMC analysis
      do i = 1, jf
        if (gfsa(kpd1_idx, i).ne.-9999.99.and.cmca(kpd1_idx, i).ne.-9999.99) then
          diff = gfsa(kpd1_idx, i) - cmca(kpd1_idx, i)
        else
          diff = 0.0
          gfsa(kpd1_idx, i) = -9999.99
        end if
        if (cmce(kpd1_idx, i).ne.-9999.99) then
          cmce_adj(kpd1_idx, i) = cmce(kpd1_idx, i) + diff
        else
          cmce_adj(kpd1_idx, i) = -9999.99
        end if
      end do

      ! Write out the results
      gfld_cmce%fld(:) = cmce_adj(kpd1_idx, :)
      call putgb2(nadj, gfld_cmce, iret)
      if (iret.ne.0) then
        write(*, *) iret, ' putgb2 to nadj error'
        exit
      end if
    end do

    call baclose(ngefs, ierr)
    call baclose(ncmce, ierr)
    call baclose(nadj, ierr)
  end do

  close(1)
  close(2)
  stop
end program generate_NAEFS_ensemble

subroutine readGB2(iunit, jpdtn, jpd1, jpd2, jpd10, jpd11, jpd12, gfld, iret)
  use grib_mod
  type(gribfield) :: gfld
  integer, intent(in) :: iunit, jpdtn, jpd1, jpd2, jpd10, jpd11, jpd12
  integer, intent(out) :: iret
  logical :: unpack=.true.

  integer :: jids(200), jpdt(200), jgdt(200), jdisc, jgdtn, jskp, jskp1

  jids = -9999
  jpdt = -9999
  jgdt = -9999

  jdisc = -1
  jgdtn = -1
  jskp = 0
  jskp1 = 0

  jpdt(1) = jpd1
  jpdt(2) = jpd2
  jpdt(10) = jpd10
  jpdt(11) = jpd11
  jpdt(12) = jpd12

  call getgb2(iunit, 0, jskp, jdisc, jids, jpdtn, jpdt, jgdtn, jgdt, unpack, jskp1, gfld, iret)
end subroutine readGB2

