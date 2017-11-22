#to extract from a project all the scan lists of individual sources
#return a list list of all the sources' scans
import re
import numpy as np
list_each = []
all_dict1={}
all_dict2 = {}
def extract_scan(filename):
    f= open(filename,'r')
    scan = []
    source = []
    maptype = []
    for ith, line in enumerate(f):
        print line.strip()
        line = line.strip()
	columns = line.split()
        print columns
        if columns != []: 
        	scannumber = np.asarray(re.split('[-]+',columns[0])[0],dtype=np.int32)
        	scan.append(scannumber)
        	sourcename = columns[1]
        	source.append(sourcename)
        	maptypename = columns[2]
		maptype.append(maptypename)
    return source,scan,maptype

from collections import defaultdict

def list_duplicates(seq1,seq2):
    tally = defaultdict(list)
    for i, item in enumerate(seq1):
	tally[item].append(i)
    return ((keys,locs) for keys, locs in tally.items())


def filter_sources(all_dict):
    sources_dict = {}
    other_dict = {}
    for k, v in all_dict.items():
        if 'AG' in k:
            sources_dict[k] = all_dict[k]
        else:
            other_dict[k] = all_dict[k]
    return sources_dict, other_dict


def filter_calibrator(all_dict):
    calib_dict = {}
    for k, v in all_dict.items():
	if 'AG' not in k and 'SKYDIP' not in k:
            
              calib_dict[k] = all_dict[k]

    return calib_dict

#def test():
#    filepath = r'/aux/pc20179a/saboca_raw_data_three/M-090.F-0026-2012/all_info.dat'
#    source,scan,maptype = extract_scan(filepath)
#    for dup in sorted(list_duplicates(source,scan)):
#        print dup
#        all_dict1[dup[0]] = np.asarray([scan[ind] for ind in dup[1]])
#    for dup1 in sorted(list_duplicates(maptype,scan)):
#        print dup1
#        all_dict2[dup1[0]] = np.asarray([scan[ind] for ind in dup1[1]])	
#    sources_dict,other_dict = filter_sources(all_dict1) 
#    return all_dict1,all_dict2,sources_dict,other_dict
#if __name__ == '__main__':
#    test()



###########################default script here#############
#filepath = r'/aux/pc20179a/saboca_raw_data_three/M-090.F-0026-2012/all_info.dat'
#filepath = r'/aux/pc20179a/saboca_raw_data_three/M-085.F-0055-2010/scans_abba.dat'
filepath = r'/aux/pc20179a/saboca_raw_data_three/M-085.F-0046-2010/scans_8546.dat'
source,scan,maptype = extract_scan(filepath)
for dup in sorted(list_duplicates(source,scan)):
    print dup
    all_dict1[dup[0]] = np.asarray([scan[ind] for ind in dup[1]])
for dup1 in sorted(list_duplicates(maptype,scan)):
    print dup1
    all_dict2[dup1[0]] = np.asarray([scan[ind] for ind in dup1[1]])	


sources_dict,other_dict = filter_sources(all_dict1)
calib_dict = filter_calibrator(all_dict1) 
###########################################################




