import os
from datetime import datetime
graphics = {
    'cam':{
        'headline':{
            'metar':{
                'set1, namnest, hireswarw, hireswarwmem2, hireswfv3, hrrr, href_avrg, href_mean, href_lpmm, href_pmmn': {
                    'lead_average':{
                        'DATE_TYPE':'INIT',
                        'VALID_BEG':'',
                        'VALID_END':'',
                        'INIT_BEG':'',
                        'INIT_END':'',
                        'VX_MASK_LIST':'CONUS_East,CONUS_Central,CONUS_South',
                        'EVAL_PERIODS':['LAST90DAYS'],
                        'FCST_VALID_HOURS':[''],
                        'FCST_INIT_HOURS':['0'],
                        'VARIABLES':{
                            'sl1l2':{
                                'TMP2m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z2',
                                    'OBS_LEVEL':'Z2',
                                    'FCST_THRESHs':[''],
                                    'OBS_THRESHs':[''],
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                },
                                'DPT2m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z2',
                                    'OBS_LEVEL':'Z2',
                                    'FCST_THRESHs':['',''],
                                    'OBS_THRESHs':['','>=283.15'],
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                },
                            },
                            'vl1l2':{
                                'UGRD_VGRD10m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z10',
                                    'OBS_LEVEL':'Z10',
                                    'FCST_THRESHs':[''],
                                    'OBS_THRESHs':[''], 
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                }
                            },
                        }
                    },
                },
                'set2, namnest, hireswarw, hireswarwmem2, hireswfv3, hrrr, href_avrg, href_mean, href_lpmm, href_pmmn': {
                    'lead_average':{
                        'DATE_TYPE':'INIT',
                        'VALID_BEG':'',
                        'VALID_END':'',
                        'INIT_BEG':'',
                        'INIT_END':'',
                        'VX_MASK_LIST':'CONUS_West',
                        'EVAL_PERIODS':['LAST90DAYS'],
                        'FCST_VALID_HOURS':[''],
                        'FCST_INIT_HOURS':['0'],
                        'VARIABLES':{
                            'sl1l2':{
                                'TMP2m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z2',
                                    'OBS_LEVEL':'Z2',
                                    'FCST_THRESHs':[''],
                                    'OBS_THRESHs':[''],
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                },
                                'DPT2m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z2',
                                    'OBS_LEVEL':'Z2',
                                    'FCST_THRESHs':['',''],
                                    'OBS_THRESHs':['','>=277.594'],
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                },
                            },
                            'vl1l2':{
                                'UGRD_VGRD10m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z10',
                                    'OBS_LEVEL':'Z10',
                                    'FCST_THRESHs':[''],
                                    'OBS_THRESHs':[''], 
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                }
                            },
                        }
                    },
                },
                'set3, namnest, hireswarw, hireswarwmem2, hireswfv3, hrrr, href_avrg, href_mean, href_lpmm, href_pmmn': {
                    'lead_average':{
                        'DATE_TYPE':'INIT',
                        'VALID_BEG':'',
                        'VALID_END':'',
                        'INIT_BEG':'',
                        'INIT_END':'',
                        'VX_MASK_LIST':'Alaska',
                        'EVAL_PERIODS':['LAST90DAYS'],
                        'FCST_VALID_HOURS':[''],
                        'FCST_INIT_HOURS':['0'],
                        'VARIABLES':{
                            'sl1l2':{
                                'TMP2m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z2',
                                    'OBS_LEVEL':'Z2',
                                    'FCST_THRESHs':[''],
                                    'OBS_THRESHs':[''],
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                },
                                'DPT2m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z2',
                                    'OBS_LEVEL':'Z2',
                                    'FCST_THRESHs':['',''],
                                    'OBS_THRESHs':['','>=272.039'],
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                },
                            },
                            'vl1l2':{
                                'UGRD_VGRD10m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z10',
                                    'OBS_LEVEL':'Z10',
                                    'FCST_THRESHs':[''],
                                    'OBS_THRESHs':[''], 
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                }
                            },
                        }
                    },
                },
                'set4, namnest, hireswarw, hireswarwmem2, hireswfv3, hrrr, href_avrg, href_mean, href_lpmm, href_pmmn': {
                    'lead_average':{
                        'DATE_TYPE':'INIT',
                        'VALID_BEG':'',
                        'VALID_END':'',
                        'INIT_BEG':'',
                        'INIT_END':'',
                        'VX_MASK_LIST':'Hawaii',
                        'EVAL_PERIODS':['LAST90DAYS'],
                        'FCST_VALID_HOURS':[''],
                        'FCST_INIT_HOURS':['0'],
                        'VARIABLES':{
                            'sl1l2':{
                                'TMP2m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z2',
                                    'OBS_LEVEL':'Z2',
                                    'FCST_THRESHs':[''],
                                    'OBS_THRESHs':[''],
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                },
                                'DPT2m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z2',
                                    'OBS_LEVEL':'Z2',
                                    'FCST_THRESHs':['',''],
                                    'OBS_THRESHs':['','>=288.706'],
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                },
                            },
                            'vl1l2':{
                                'UGRD_VGRD10m':{
                                    'STATSs':['bcrmse,me'],
                                    'FCST_LEADS':['0,3,6,9,12,15,18,21,24'],
                                    'FCST_LEVEL':'Z10',
                                    'OBS_LEVEL':'Z10',
                                    'FCST_THRESHs':[''],
                                    'OBS_THRESHs':[''], 
                                    'CONFIDENCE_INTERVALS':'False',
                                    'INTERP':'BILIN',
                                    'INTERP_PNTSs':[''],
                                }
                            },
                        }
                    },
                },
            }
        }
    },
}
