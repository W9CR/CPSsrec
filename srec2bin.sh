#!/bin/bash
#
# a script to convert a binary codeplug to an srecord codeplug which is able to be loaded in CPS
# Copyright Bryan Fields 2020
# Licensed under the GPLv2
# This is a PoC.  Please don't use this.
#
#


usage() 
{
	echo "used to convert a CPS srec file to binary for ayalisis" 
	echo "Usage: srec2bin.sh input.bin output.srec"
}



while [ "$1" != "" ]; do
	case $1 in
        	-i | --in )	shift
                		inputfilename=$1
				;;
		-o | --out)	shift
				outputfilename=$1
				;;
		-h | --help )	usage
				exit
				;;
		* )		usage
				exit 1
	esac
	shift
done
# remove the header of 0x322 bytes

dd if=$inputfilename of=tmp-stage-1.srec bs=1 skip=802

#conver to binary
srec_cat -Output -Binary tmp-stage-1.srec >tmp-stage-2.bin

# Then the first 0x5 bytes must be removed from the binary file.  
# 0x0000 will be the segment starting at 0x280 in a normal code plug. 

dd if=tmp-stage-2.bin of=tmp-stage-3.bin bs=1 skip=5

# add 0x27F bytes to the file
printf '\x02\x80' >$outputfilename
dd if=/dev/zero bs=1 count=638 >> $outputfilename
dd if=tmp-stage-3.bin >> $outputfilename

#rm tmp-stage-2.bin tmp-stage-3.bin  tmp-stage-1.srec 

