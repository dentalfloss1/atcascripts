#!/bin/bash

vis=$1
# 0.1asec is for 6km baselines

[[ -e target10GHz-MFS-image.fits ]] || { wsclean -mem 90 -no-update-model-required -weight briggs 0 -name target10GHz -size 5120 5120 -scale 0.1asec -channels-out 4 -spws 30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,46,47,48,49,50,51,52,53,54,55,56,57,58,59 -niter 5000 -nmiter 5 -threshold 0.00008 -join-channels -fit-spectral-pol 4 $vis ; }
[[ -e target6GHz-MFS-image.fits ]] || { wsclean -mem 90 -no-update-model-required -weight briggs 0 -name target6GHz -size 5120 5120 -scale 0.1asec -channels-out 4 -spws 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29 -niter 5000 -nmiter 5 -threshold 0.00008 -join-channels -fit-spectral-pol 4 $vis ; }
[[ -e target8GHz-MFS-image.fits ]] || { wsclean -mem 90 -no-update-model-required -weight briggs 0 -name target8GHz -size 5120 5120 -scale 0.1asec -channels-out 8 -niter 5000 -nmiter 5 -threshold 0.00008 -join-channels -fit-spectral-pol 4 $vis ; }
[[ -e naturaltarget8GHz-MFS-image.fits ]] || { wsclean -mem 90 -no-update-model-required -weight natural -name naturaltarget8GHz -size 5120 5120 -scale 0.1asec -channels-out 8 -niter 5000 -nmiter 5 -threshold 0.00008 -join-channels -fit-spectral-pol 4 $vis ; }
[[ -e naturaltarget10GHz-MFS-image.fits ]] || { wsclean -mem 90 -no-update-model-required -weight natural -name naturaltarget10GHz -size 5120 5120 -scale 0.1asec -channels-out 4 -spws 30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,46,47,48,49,50,51,52,53,54,55,56,57,58,59 -niter 5000 -nmiter 5 -threshold 0.00008 -join-channels -fit-spectral-pol 4 $vis ; }
[[ -e naturaltarget8GHz-MFS-image.fits ]] || { wsclean -mem 90 -no-update-model-required -weight natural -name naturaltarget6GHz -size 5120 5120 -scale 0.1asec -channels-out 4 -spws 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29 -niter 5000 -nmiter 5 -threshold 0.00008 -join-channels -fit-spectral-pol 4 $vis ; }
