A description of the EMC Verification System (EVS) will go here. 

The branch of EVSforAQMv7 is created to preserve the structure of running AQM v7 output.

NCO does not allow EVSv1.0 to have the code/scripts handling AQMv7 output.  Thus, in the PR#204 aqm restart, all *v6* has been removed from the filename and used in EVSiv1.0.  All *v7* files will be removed.

To preserve the v7 ability, copy current *v7* files to a non-tracked file (using cp only but not "git add"), as well as a copy of ~/jobs/aqm/*/J*.  Later J* and need to remove the dependence of vfcst_ver/fcst_input_ver.  After the sync of develop with PR#204, replacing the v6 code with v7 code for EVSv1.x that handling AQMv7 output.
