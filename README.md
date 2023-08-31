A description of the EMC Verification System (EVS) will go here. 

The branch of EVSforAQMv7 is created to preserve the structure of running both AQM v6 and v7 output.

NCO does not allow EVSv1.0 to have the code/scripts handling AQMv7 output.  Thus, in the PR#204 aqm restart, all *v6* has been removed from the filename and used in EVSiv1.0.  All *v7* files has been removed.

After the sync of develop with PR#204, replacing the v6 code with v7 code for EVSv1.x that handling AQMv7 output.
