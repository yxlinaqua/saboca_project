
#!/bin/sh
#monthday=`date | cut -d' ' -f 2-3 | sed 's/ //g'`
#year=`date | cut -d' ' -f 6`
#dirname=${year}${monthday}


dirpath=/Users/yuxinlin/saboca_sources/gauss_clump/data_files/gaussclumps_tcs/
rms_dirpath=/Users/yuxinlin/saboca_sources/gauss_clump/data_files/
outpath=/Users/yuxinlin/saboca_sources/gauss_clump/tests/
##############initial input###########################
ff=`ls ${dirpath}*zero_db*fits`
for file in ${ff}
do
echo ${file}
#done
dirname=""   #reduction date
dataname=`ls ${file}`
filename=`ls ${file}| cut -d '/' -f 8`
outname=${dirpath}data #sourcename
sourcename=`echo ${filename}| cut -d 's' -f 1`
echo ${sourcename} "sourcename"
rmsname=`find ${rms_dirpath} -name "${sourcename}*rms.txt"`
echo ${rmsname} "rms name"
#
research=${output}  #output directory

echo "attention!!!" 
sourcename=`echo ${filename}| cut -d 's' -f 1`
echo ${sourcename} "sourcename"


cp ${rmsname} rms.txt
rms_level=`cat rms.txt`

mininteg=-0.15
cp gaussclumps_orig.init gaussclumps.init


for s0 in `cat stiffness.txt`
do
    for sa in `cat stiffness.txt`
    do
        for sc in `cat stiffness.txt`
            do
                for mininteg in `cat mininte.txt`
                do
                echo ${s0} ${sa} ${sc} #${mininteg}
                

                let "thres=rms_level*3" #change y value for different thresholds of n*rms
                for ((lv=3;lv<=3;lv=lv+3))
                do
                    for ((li=0;li<=0;li=li+3))#
                    do
                            cp gaussclumps_orig.init gaussclumps.init
                            sed -i .bak "s/RMS\$\ 1/RMS\$\ ${rms_level}/g" run
                            thres=`awk -v "x=${rms_level}" -v y=${lv} 'BEGIN {printf "%.4f\n",x*y}'`
                            sed -i .bak "s/THRESHHOLD\$\ 1./THRESHHOLD\$\  ${thres}/g" gaussclumps.init
                            minint=`awk -v "x=${mininteg}" -v y=${li} 'BEGIN {printf "%.4f\n",x*y}'`
                            sed -i .bak "s/MININTEGRAL\$\ 0/MININTEGRAL\$\  ${minint}/g" gaussclumps.init
                            sed -i .bak "s/FWHM_START\$\ 1.1/FWHM_START\$\ 1.5/g" gaussclumps.init
                            sed -i .bak "s/FWHM_START\$\ 1.1/FWHM_START\$\ 1.1/g" gaussclumps.init
                            sed -i .bak "s/APERTURE_FWHM\$\ 1.1/APERTURE_FWHM\$\  1.1/g" gaussclumps.init
                            sed -i .bak "s/APERTURE_LMTS\$\ 6/APERTURE_LMTS\$\ 8.0/g" gaussclumps.init
                            sed -i .bak "s/STIFFNESS\$\[3\]\ \ 1.\ 1.\ 1./STIFFNESS\$\[3\]\ \ ${s0}\ ${sa}\ ${sc}/g" gaussclumps.init
                            #sed -i .bak "s/MININTEGRAL\$\ 0/MININTEGRAL\$\ -6./g" gaussclumps.init
                            greg @run_gauss.greg ${filename} ${rms_level} ${s0} ${sa} ${sc} ${lv} ${minint}
                        
                            minamp=`sed -n '$p'  GAUSSCLUMPS_3D.list | awk '{print $5}'`
                            #ratio=`awk -v "x=${thres}" -v y=${minamp} 'BEGIN {printf "%.4f\n",y/x}'`
                        
                             c=$(echo "$thres>$minamp"|bc)        #if a>b，c=1;or c=0#man bc for details
                            if [[ $c -eq 1 ]] ; then
                                echo $minamp > ${sourcename}_${thres}_${minint}.txt
                                echo ${thres} >>${sourcename}_${thres}_${minint}.txt
                            else
                                echo "Min amp of identified clump failed to reach below threshold setting!"
                            fi
                            echo ${rms_level}
                            echo ${thres}
                            echo ${filename}
                            sed -n '$p'  GAUSSCLUMPS_3D.list | awk '{print $5}' >${sourcename}_${thres}_${minint}.txt
                        
                    done
                done
            done
        done
    done
done
#sed -i .bak "s/STIFFNESS\$\[3\]\ \ 1.\ 1.\ 1./STIFFNESS\$\[3\]\ \ 1.\ 0.8\ 0.8/g" gaussclumps.init
#sed -i .bak "s/MININTEGRAL\$\ 0/MININTEGRAL\$\ -0.1/g" gaussclumps.init



#.bak (or any other extension names) is needed for the temporary file when using 'sed' to file content editting


done
