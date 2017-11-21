
#!/bin/sh
#monthday=`date | cut -d' ' -f 2-3 | sed 's/ //g'`
#year=`date | cut -d' ' -f 6`
#dirname=${year}${monthday}

dirpath=/Users/yuxinlin/saboca_sources/gauss_clump/data_files1/
rms_dirpath=${dirpath}rms_file/
outpath=/Users/yuxinlin/saboca_sources/gauss_clump/output1/
##############initial input###########################
ff=`ls ${dirpath}*.fits`
for file in ${ff}
do
echo ${file}
#done
dirname=""   #reduction date
dataname=`ls ${file}`
filename=`ls ${file}| cut -d '/' -f 7`
outname=${dirpath}data #sourcename
echo ${outname}
sourcename=`echo ${filename}| cut -d 's' -f 1`
rmsname=`find ${rms_dirpath} -name "${sourcename}*"`
research=${output}  #output directory
###############convert fits to sdf####################
##convert
/star-2015A/bin/convert/fits2ndf ${dataname} ${outname}.sdf
#/star-2015A/bin/convert/fits2ndf ${rmsname} ${outname}_rms.sdf
##kappa
outname=`echo ${outname}| cut -d '/' -f 7`
#echo ${outname_rms}
#/star-2015A/bin/kappa/maths 'ia/ib' ia=${outname}.sdf ib=${outname_rms}.sdf out=${outname}_snr.sdf
#echo ${outname}_snr
#cupid
#/star-2015A/bin/cupid/findback IN=${outname}_snr.sdf OUT=${outname}_snr_back.sdf SUB=TRUE BOX=63 RMS=0.3
#echo "findback finished!"
#echo '-----Hi, there. Back found!-----'
## use pixel coordinate, set WCSPAR=FALSE
## out put a catalogue, set OUTCAT to the name of the output file
#cupid
#/star-2015A/bin/cupid/findclumps IN=${outname}_snr_back.sdf OUT=data_snr_out1.sdf BACKOFF=TRUE METHOD=GaussClumps LOGFILE=${outname}_snr.log NCLUMPS=100 OUTCAT=${outname}_snr_cat SHAPE=Ellipse WCSPAR=TRUE MSG_FILTER=5 RMS=1.0 CONFIG=^test.para
#echo "findclumps on the snr file finished."
#sourcename=`echo ${filename}| cut -d 'c' -f 1`

cp ../data_files/${sourcename}*-rms.txt rms.txt
rms_level=`cat rms.txt`
#
#/star-2015A/bin/cupid/findback IN=${outname}.sdf OUT=${outname}_data_back.sdf SUB=TRUE BOX=63 RMS=${rms_level}
#echo "findback of the data file finished!"
#find clumps on the snr data **not work for gauss clumps but work for fellwalker, the error info is about dimensional error, not sure how to solve yet
#/star-2015A/bin/cupid/extractclumps MASK=${outname}_snr_out1.sdf DATA=${outname}_data_back.sdf OUT=${outname}_data_out.sdf OUTCAT=${outname}_data_cat BACKOFF=TRUE DECONV=FALSE SHAPE=Ellipse WCSPAR=TRUE
#
#find clumps directly on the data file, need to use skimage pywt to calculate the rms level

/star-2015A/bin/cupid/findclumps IN=${outname}_data_back.sdf OUT=data_out1.sdf BACKOFF=TRUE METHOD=GaussClumps LOGFILE=${outname}_out1_gc.log NCLUMPS=100 OUTCAT=${outname}_data_out1_cat SHAPE=Ellipse WCSPAR=TRUE MSG_FILTER=5 RMS=${rms_level} CONFIG=^test.para 
echo "findclumps on the data file finished."
#

#echo '-----Finished, byebye!-----'
rm -rf ${outname}_data_out.fits
rm -rf ${outname}_data_back.fits

##convert

/star-2015A/bin/convert/ndf2fits ${outname}_out1.sdf ${outname}_data_out.fits
##convert
/star-2015A/bin/convert/ndf2fits ${outname}_data_back.sdf ${outname}_data_back.fits


/star-2015A/bin/kappa/gdset apscol_l
/star-2015A/bin/kappa/display IN=${outname}_data_back MODE=current
/star-2015A/bin/kappa/listshow IN=${outname}_data_out1_cat PLOT=STCS
mv pgplot.ps ../output/${sourcename}_Gauss.ps
mv ${outname}_out1_gc.log ../output1/${outname}_${sourcename}_Gauss.log
mv ${outname}_data_out.fits ../output1/${outname}_out_${sourcename}_Gauss.fits
mv ${outname}_data_out1_cat.FIT ../output1/${outname}_cat_${sourcename}_Gauss.FIT
mv ${outname}_data_back.fits ../output1/${outname}_back_${sourcename}_Gauss.fits

#rm -rf ${outname}.sdf
#rm -rf ${outname}_rms.sdf
#rm -rf ${outname_rms}.sdf
#rm -rf ${outname}_snr.sdf
#rm -rf ${outname}_snr_back.sdf
#
#rm -rf ${outname}_data_out.sdf
#rm -rf ${outname}.para
#rm -rf data_snr_out.sdf
#rm -rf data_snr_cat.FIT
#rm -rf data_data_back.sdf
#rm -rf data_data_out.sdf
#rm -rf data_data_cat.FIT

done
