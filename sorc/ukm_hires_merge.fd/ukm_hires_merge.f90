program ukm_hires_merge
  !-----------------------------------------------------------------
  ! Merges ukm hires data in 8 regional patches into one global array
  ! Data Source: /dcom/us007003/yyyymmdd/wgrbbul/ukmet_hires
  ! Use bi-linear interpolation to create a 1-deg global dataset.
  ! Fanglin Yang, June 2014
  !-----------------------------------------------------------------

  ! Input data info
  integer, parameter :: np = 8 ! number of patches
  integer, parameter :: nx = 108 ! number of longtudinal points for each patch
  integer, parameter :: ny = 162 ! number of latitudinal points for each patch
  integer, parameter :: nxny = nx * ny ! total points for each patch
  integer, parameter :: mmax = 200000 ! maximum number of points to unpack
  real, parameter :: resy = 556.0, resx = 833.0 ! data resolution (x1000)

  logical*1 :: lb(mmax)
  character*200 :: input, output
  integer :: iargc
  external :: iargc
  integer :: nargs ! number of command-line arguments
  character*200 :: argument ! space for command-line argument
  integer :: jpds(200), jgds(200), fhr
  integer :: kpds(200), kgds(200)

  real :: varp(mmax, np) ! data from each patch
  real :: var(nx * 4 + 1, ny * 2) ! a global high-res array
  real :: xs(np), xe(np), ys(np), ye(np) ! starting and ending lat-lon of patches
  real :: lon(nx * 4 + 1), lat(ny * 2) ! lat-lon positions

  ! Output data, 1x1 deg global
  real, parameter :: resg = 1000.0
  integer, parameter :: mx = 360000 / resg, my = 180000 / resg + 1
  integer, parameter :: mxmy = mx * my
  real :: varg(mx, my), varg1(mx * my)
  real :: long(mx), latg(my)
  real :: dy1(my), dy2(my), dx1(mx), dx2(mx)
  integer :: ix(mx), iy(my)
  real :: tmp1, tmp2, sums, sumn

  ! Starting and ending lat and lon of each patch (x1000)
  data xs / 341250, 71250, 161250, 251250, 341250, 71250, 161250, 251250 /
  data xe / 70416, 160416, 250416, 340416, 70416, 160416, 250416, 340416 /
  data ys / 279, 279, 279, 279, -89721, -89721, -89721, -89721 /
  data ye / 89722, 89722, 89722, 89722, -278, -278, -278, -278 /

  ! Source data position
  do n = 1, 4
    i0 = (n - 1) * nx
    do i = i0 + 1, i0 + nx
      lon(i) = xs(n) + resx * (i - i0 - 1)
      if (lon(i) .gt. 360000) lon(i) = lon(i) - 360000
    enddo
  enddo
  lon(4 * nx + 1) = lon(1)
  do j = 1, ny
    lat(j) = ys(5) + resy * (j - 1) ! southern hemisphere
  enddo
  do j = ny + 1, ny * 2
    lat(j) = ys(1) + resy * (j - ny - 1) ! northern hemisphere
  enddo

  ! Output data position
  do i = 1, mx
    long(i) = (i - 1) * resg
  enddo
  do j = 1, my
    latg(j) = -90000.0 + (j - 1) * resg
  enddo

  ! Temporary arrays used for linear interpolation
  do j = 1, my
    do jj = 1, 2 * ny - 1
      if (latg(j) .ge. lat(jj) .and. latg(j) .lt. lat(jj + 1)) then
        dy1(j) = latg(j) - lat(jj)
        dy2(j) = lat(jj + 1) - latg(j)
        iy(j) = jj
      endif
    enddo
  enddo

  ! Special case at 0E
  i = 1
  ii = 23
  ix(i) = 23
  dx1(i) = 360000.0 - lon(ii)
  dx2(i) = lon(ii + 1)

  do i = 2, mx
    do ii = 1, 4 * nx
      if (long(i) .ge. lon(ii) .and. long(i) .lt. lon(ii + 1)) then
        dx1(i) = long(i) - lon(ii)
        dx2(i) = lon(ii + 1) - long(i)
        ix(i) = ii
      endif
    enddo
  enddo

  nargs = iargc() ! iargc() - number of arguments
  if (nargs .lt. 3) then
    write(*, *) 'usage : ukm_hires_merge.x input output fcst_hour'
    stop
  endif
  call getarg(1, input)
  call getarg(2, output)
  call getarg(3, argument)
  read(argument, *) fhr
  print*, "input: ", trim(input)
  print*, "output: ", trim(output)
  print*, "fcst hour:", fhr
  fhrm6 = fhr - 6
  fhrm12 = fhr - 12

  call baopenr(10, trim(input), iret)
  if (iret .ne. 0) write(6, *) " failed to open ", input
  call baopen(20, trim(output), iret)
  if (iret .ne. 0) write(6, *) " failed to open ", output
  if (iret .ne. 0) then
    print *, "iret=",iret, "STOP"
    stop
  endif

  nrec = -1
  do while (nrec < 0)
    jpds = -1
    jgds = -1
    do n = 1, np
      jgds(2) = nx
      jgds(3) = ny
      jgds(9) = resx
      jgds(10) = resy
      jgds(4) = ys(n)
      jgds(5) = xs(n)
      jgds(7) = ye(n)
      jgds(8) = xe(n)
      call getgb(10, 0, mmax, nrec, jpds, jgds, kf, k, kpds, kgds, lb, varp(1, n), iret)
      if (kpds(6).ne.7) then
          if (iret.ne.0) then
            print *, "iret=",iret, "STOP" !reached end of record or incorrect file
            CALL W3TAGE('ukm_hires_merge ')
            stop
          endif
          do k = 1, 16
            jpds(k) = kpds(k)
          enddo
      endif
      nrec = nrec - 1
    enddo

    ! Assemble a global array for right forecast hour
    ! For precipitation APCP, jpds(15) = fhr
    if ((jpds(14) == fhr) .or. (jpds(5) == 61 .and. jpds(15) == fhr)) then
      do n = 1, 4 ! patches in northern hemisphere
        do j = 1, ny
          do i = 1, nx
            jj = ny + j
            ii = (n - 1) * nx + i
            var(ii, jj) = varp((j - 1) * nx + i, n)
          enddo
        enddo
      enddo
      do n = 5, 8 ! patches in southern hemisphere
        do j = 1, ny
          do i = 1, nx
            jj = j
            ii = (n - 5) * nx + i
            var(ii, jj) = varp((j - 1) * nx + i, n)
          enddo
        enddo
      enddo
      do jj = 1, 2 * ny
        var(4 * nx + 1, jj) = var(1, jj)
      enddo

      ! Interpolate to resg-deg global array
      ! For north pole and south pole
      sums = 0.0
      sumn = 0.0
      do i = 1, 4 * nx
        sums = sums + var(i, 1)
        sumn = sumn + var(i, 2 * ny)
      enddo
      do i = 1, mx
        varg(i, 1) = sums / (4 * nx)
        varg(i, my) = sumn / (4 * nx)
      enddo

      ! For other points
      do j = 2, my - 1
        do i = 1, mx
          tmp1 = (var(ix(i), iy(j)) * dy2(j) + var(ix(i), iy(j) + 1) * dy1(j)) / (dy1(j) + dy2(j))
          tmp2 = (var(ix(i) + 1, iy(j)) * dy2(j) + var(ix(i) + 1, iy(j) + 1) * dy1(j)) / (dy1(j) + dy2(j))
          varg(i, j) = (tmp1 * dx2(i) + tmp2 * dx1(i)) / (dx1(i) + dx2(i))
        enddo
      enddo

      do j = 1, my
        do i = 1, mx
          varg1((j - 1) * mx + i) = varg(i, j)
        enddo
      enddo

      ! Write out grib1 global array
      kgds(2) = mx
      kgds(3) = my
      kgds(9) = resg
      kgds(10) = resg
      kgds(4) = -90000
      kgds(5) = 0
      kgds(7) = 90000
      kgds(8) = (mx - 1) * resg
      call putgb(20, mxmy, kpds, kgds, lb, varg1, iret)
    endif
  end do

  call baclose(10, iret)
  call baclose(20, iret)
  CALL W3TAGE('ukm_hires_merge ')
end

