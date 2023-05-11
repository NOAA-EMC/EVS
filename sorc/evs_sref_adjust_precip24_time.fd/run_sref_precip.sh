#!/bin/bash
>out.all

for nfhr in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 1 20 21 22 23 24 25 26 27 28 ; do
  echo $nfhr |../../exec/sref_precip.x > out.$nfhr
  cat out.$nfhr >> out.all
done

