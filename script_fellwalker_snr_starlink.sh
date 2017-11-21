#!/bin/sh
#monthday=`date | cut -d' ' -f 2-3 | sed 's/ //g'`
#year=`date | cut -d' ' -f 6`
#dirname=${year}${monthday}

dirpath=/Users/yuxinlin/saboca_sources/gauss_clump/data_files/
rms_dirpath=${dirpath}rms_file/
outpath=/Users/yuxinlin/saboca_sources/gauss_clump/output/
##############initial input###########################
ff=`ls ${dirpath}*.fits`
for file in ${ff}
do
echo ${file}
#done
dirname=""   #reduction date
dataname=`ls ${file}`
echo ${dataname}
filename=`ls ${file}| cut -d '/' -f 7`
outname=${dirpath}data #sourcename
sourcename=`echo ${filename}| cut -d 's' -f 1`
rmsname=`find ${rms_dirpath} -name "${sourcename}*"`
#
research=${output}  #output directory
#touch ${outname}.sdf  
#touch ${outname}_back.sdf
#touch ${outname}_out.sdf
#touch $1.para #configuration parameters
#cp $1.para ${research}/${outname}.para
#cp $1.para ${outname}.para
###############convert fits to sdf####################
#csh
##convert
echo "attention!!!" ${outname} ${outname}_rms
/star-2015A/bin/convert/fits2ndf ${dataname} ${outname}.sdf
/star-2015A/bin/convert/fits2ndf ${rmsname} ${outname}_rms.sdf
##kappa
outname=`echo ${outname}| cut -d '/' -f 7`
echo ${outname}
outname_rms=`echo ${outname}_rms| cut -d '/' -f 7`
echo ${outname_rms}
/star-2015A/bin/kappa/maths 'ia/ib' ia=${outname}.sdf ib=${outname_rms}.sdf out=${outname}_snr.sdf
echo ${outname}_snr
#cupid
/star-2015A/bin/cupid/findback IN=${outname}_snr.sdf OUT=${outname}_snr_back.sdf SUB=TRUE BOX=63 RMS=0.3
echo "findback finished!"
cp test_fellwalker.para ${outname}.para
echo '-----Hi, there. Back found!-----'
## use pixel coordinate, set WCSPAR=FALSE
## out put a catalogue, set OUTCAT to the name of the output file
#cupid
/star-2015A/bin/cupid/findclumps IN=${outname}_snr_back.sdf OUT=${outname}_snr_out.sdf BACKOFF=TRUE METHOD=FellWalker 
LOGFILE=${outname}_snr.log NCLUMPS=100 CONFIG=^test_fellwalker.para OUTCAT=${outname}_snr_cat SHAPE=Ellipse WCSPAR=TRUE MSG_FILTER=5 
DECONV=FALSE PERSPECTRUM=FALSE RMS=1.0
echo "findclumps on the snr file finished!"
#
/star-2015A/bin/cupid/findback IN=${outname}.sdf
OUT=${outname}_data_back.sdf SUB=TRUE BOX=63 RMS=0.15
echo "findback of the data file finished!"
/star-2015A/bin/cupid/extractclumps MASK=${outname}_snr_out.sdf DATA=${outname}_data_back.sdf OUT=${outname}_data_out.sdf OUTCAT=${outname}_data_cat
BACKOFF=TRUE DECONV=FALSE SHAPE=Ellipse WCSPAR=TRUE
#
#
#echo '-----Finished, byebye!-----'
rm -rf ${outname}_data_out.fits
##convert
/star-2015A/bin/convert/ndf2fits ${outname}_data_out.sdf 
${outname}_data_out.fits
##convert
/star-2015A/bin/convert/ndf2fits ${outname}_data_back.sdf 
${outname}_data_back.fits

listshow ${outname}_data_back plot=STCS
gdset apscol_l
mv pgplot.ps ${sourcename}.ps
mv ${outname}.log ${research}/${outname}_${sourcename}.log
mv ${outname}_data_out.fits ${research}/${outname}_out_${sourcename}.fits
mv ${outname}_data_cat.FIT ${research}/${outname}_cat_${sourcename}.FIT
mv ${outname}_data_back.fits ${research}/${outname}_back_${sourcename}.fits

rm -rf ${outname}.sdf
rm -rf ${outname}_data_out.sdf
rm -rf ${outname}.para
done
