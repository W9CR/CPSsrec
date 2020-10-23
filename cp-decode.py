#!/usr/bin/python
from __future__ import division
import struct
import sys
print sys.argv
import fileinput
import binascii
from optparse import OptionParser
from StringIO import StringIO
import struct

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE" )

parser.add_option("-t", "--tuning", action="store_true", dest="SHOW_TUNE", default="False", help="show tuning block")

parser.add_option("-F", "--feature", action="store_true", dest="SHOW_FEATURE", default="False", help="show feature block")

parser.add_option("-p", "--programing", action="store_true", dest="SHOW_PROGRAMING", default="False", help="show programing block")

(options, args) = parser.parse_args()

#print options

#def chunks(f):
#    skip = 0
#    while True:
#        byte = f.read(1)
#        if byte == "":
#            break
#        if ord(byte) == 0x80:
#            print "80 field found"
#            print "skipped:", skip
#            skip = 0
#            
#            size = ord(f.read(1))
#            repeat = ord(f.read(1)) or 1
#            chunk = f.read(size * repeat)
#            checksum = ord(f.read(1))
#            yield size, repeat, chunk, checksum
#        else:
#            skip += 1


def chunks(f):
    skip = 0
    while True:
        byte = f.read(1)
        if byte == "":
            break
        if ord(byte) == 0x80:
            print ""
            print "80 field found"
            print "skipped:", skip
            skip = 0
            size = ord(f.read(1))
            repeat = ord(f.read(1)) or 1
            chunk = f.read(size * repeat)
            checksum = ord(f.read(1))
            yield size, repeat, chunk, checksum
        elif ord(byte) == 0x84: #llrrnnnn if ll == 0, each element is nnnnn long and there are rr of them if ll != 0: ll is the length of each item and and there are rr+1 of them
            print ""
            print "84 field found"
            print "skipped:", skip
            if skip != 0:
                break
            skip = 0
            SIZE_TUPLE = (struct.unpack('>bbH',(f.read(4))))
            print "SIZE TUPLE = %s" % (SIZE_TUPLE,)
            print "SIZE TUPLE ll = %s" % SIZE_TUPLE[0]
            print "SIZE TUPLE rr = %s" % SIZE_TUPLE[1]
            print "SIZE TUPLE nnnn = %s" % SIZE_TUPLE[2]
            if SIZE_TUPLE[0] == 0:
               size = int(SIZE_TUPLE[2] * SIZE_TUPLE[1])
            elif SIZE_TUPLE[0] != 0:
                size = int(SIZE_TUPLE[0] * (SIZE_TUPLE[1] + 1))
            size = int(SIZE_TUPLE[0] + SIZE_TUPLE[1])
            print "size"  "0x%x" % size
            repeat =  1
            chunk = f.read(size)
            print "SIZZZZZZZZZE    " "0x%x" % size
            checksum = ord(f.read(1))
            yield size, repeat, chunk, checksum
        else:
            skip += 1




def hexprint(data, addrfmt=None):
    """Return a hexdump-like encoding of @data"""
    if addrfmt is None:
        addrfmt = '%(addr)03i'
    
    block_size = 8
    
    lines = len(data) / block_size
    
    if (len(data) % block_size) != 0:
        lines += 1
        data += "\x00" * ((lines * block_size) - len(data))
    
    out = ""
    
    for block in range(0, (len(data)/block_size)):
        addr = block * block_size
        try:
            out += addrfmt % locals()
        except (OverflowError, ValueError, TypeError, KeyError):
            out += "%03i" % addr
        out += ': '
        
        left = len(data) - (block * block_size)
        if left < block_size:
            limit = left
        else:
            limit = block_size
        
        for j in range(0, limit):
            out += "%02x " % ord(data[(block * block_size) + j])
        
        out += "  "
        
        for j in range(0, limit):
            char = data[(block * block_size) + j]
            
            if ord(char) > 0x20 and ord(char) < 0x7E:
                out += "%s" % char
            else:
                out += "."
        
        out += "\n"
    
    return out


def chksm8 (s):
    sum = 0
    for c in s:
        sum += ord(c)
        sum = sum % 0x100
#    return '0x%2x' % (sum)
    return sum  # this returns it as an int.


def parse_toc(string, size=0x2, start=2):
    length = (int(ord(string[0:1]) + ord(string[1:2])) + 0x1)
    print "number of pointers in TOC =", (length - 1)
    returnarray = []
    for i in range(start, length * size, size):
        returnarray.append(string[i:i+size])
    return returnarray


#example of
#print "0x%x" % ((sum(map(ord, (binascii.a2b_hex('000a03ffdf03ff7f3faf'))))) % 0x100 )


class BinaryReaderEOFException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return 'Not enough bytes in file to satisfy read request'



#import fileinput
#for line in fileinput.input():
#    process(line)

#print options.filename
#read data from file

with open(options.filename, 'rb') as f:
    data = f.read()

# load the tuning cp and print the length and checksum is valid
#open file, look at first 2 bytes, this is the legth of the tuning CP including checksum
#print length and checksum is valid
#store the tuning data including checksum as TUNING_BLOCK

#def get_bytes_from_file(filename):
#    return open(filename, "rb").read()

#with open(options.filename, 'rb') as f:
#    data = f.read()

#for line in data:
#    print line'

reader = StringIO(data)
integer, short = struct.unpack('>ih', reader.read(6))
STRING_MAGIC = 0x80

# load the Tuning data and find the length

TUNING_LENGTH = (ord(data[0]) << 8) + ord(data[1])
TUNING_BLOCK = data[:TUNING_LENGTH]

#load the FDB and print length and is the checksum valid

FEATURE_BLOCK_START = TUNING_LENGTH
FEATURE_BLOCK_LENGTH = (ord(data[FEATURE_BLOCK_START]) << 8) + ord(data[FEATURE_BLOCK_START+1])
FEATURE_BLOCK_END = FEATURE_BLOCK_START + FEATURE_BLOCK_LENGTH
FEATURE_BLOCK = data[FEATURE_BLOCK_START+2:FEATURE_BLOCK_END]





#load the rest of the CP and print length and checksum valid  the CP starts with 0x0400 on a byte boundry.  I should check for this

PROGRAMING_BLOCK_START = TUNING_LENGTH + FEATURE_BLOCK_LENGTH
PROGRAMING_BLOCK_LENGTH = (ord(data[PROGRAMING_BLOCK_START+2]) << 8) + ord(data[PROGRAMING_BLOCK_START+3])
PROGRAMING_BLOCK_END = PROGRAMING_BLOCK_START + PROGRAMING_BLOCK_LENGTH
PROGRAMING_BLOCK = data[PROGRAMING_BLOCK_START:PROGRAMING_BLOCK_END]




TOC_HEADER_START = (ord(data[PROGRAMING_BLOCK_START+4]) << 8) + ord(data[PROGRAMING_BLOCK_START+5])
TOC_START = (ord(data[PROGRAMING_BLOCK_START+6]) << 8) + ord(data[PROGRAMING_BLOCK_START+7])

print "toc start 1 (hex) = ", "0x%x" % TOC_START

PROGRAMING_BLOCK = data[PROGRAMING_BLOCK_START:PROGRAMING_BLOCK_END]



#TOC_HEADER_LENGTH = struct.unpack(">h", (data[TOC_HEADER_START:(TOC_HEADER_START+2)]))
TOC_HEADER_LENGTH = (ord(data[TOC_HEADER_START]) << 8) + ord(data[TOC_HEADER_START+1])

print "toc Header length 1 (hex) = ", "0x%x" % TOC_HEADER_LENGTH

TOC_HEADER_DATA = data[TOC_HEADER_START:(TOC_HEADER_START+TOC_HEADER_LENGTH)]

# TOC has the first 2 bytes as the number of 2 byte pointers + 1 byte for checksum + the 2 byte header
TOC_LENGTH = ((ord(data[TOC_START]) << 8) + ord(data[TOC_START+1]) <<1) + 3

print "toc start 1 (hex) = ", "0x%x" % TOC_START

print "toc Length 1 (hex) = ", "0x%x" % TOC_LENGTH

    
TOC_DATA = data[TOC_START:(TOC_START+TOC_LENGTH)]
#print "toc data (hex) = ", "0x%x" % TOC_DATA


#tuning block unpack

RX_PIERS = TUNING_BLOCK[0x139:0x147]
TX_PIERS = TUNING_BLOCK[0x147:0x155]
#find the offest based on the magicnumber preceding the RF TEST PIERS location the tuning block, then read 14 sets of 2 bytes
RF_TEST_PIERS_OFFSET = (TUNING_BLOCK.index('\xFF\xFF\xFF\xFF\x07'))+5
RF_TEST_PIERS = TUNING_BLOCK[RF_TEST_PIERS_OFFSET:RF_TEST_PIERS_OFFSET+28]

RX_PIERS_TUPLE = struct.unpack('>HHHHHHH',RX_PIERS)
TX_PIERS_TUPLE = struct.unpack('>HHHHHHH',TX_PIERS)
RF_TEST_PIERS_TUPLE = struct.unpack('>HHHHHHHHHHHHHH',RF_TEST_PIERS)



# feature block decoding
reader = StringIO(FEATURE_BLOCK)
FEATURElist = list()


#for size, repeat, chunk, checksum in chunks(reader):
        # print "\nsize:", "0x%x" % size
        #print "repeat:", "0x%x" % repeat
        #print "total:", "0x%x" % size * repeat
        #print "data:"
        #print hexprint(chunk)
#    FEATURElist.append(chunk)
        #print "checksum:", "0x%x" % checksum
    
    #print "freature list number of items = " , len(FEATURElist)
    #for item in FEATURElist:
    #print item.encode('hex')
    
#Feature_List_1 = FEATURElist[0]
#Feature_List_2 = FEATURElist[1]
#FDB_TUPLE_1 = struct.unpack('>10sH16sHBBBBBBBBBBHHH16sBB10sBBBBBBBB',Feature_List_1) # This is the unpack for the first FDB with serial number an frequency limits
#SERIAL_NUMBER = FDB_TUPLE_1[0]
#SPACE_1_FDB_1 = FDB_TUPLE_1[1]
#MODEL_NUMBER = FDB_TUPLE_1[2]
#SPACE_2_FDB_1 = FDB_TUPLE_1[3] #null 0x2A1:2A2
#CP_VER_MAJOR = FDB_TUPLE_1[4] #cp ver major 0x2A3
#CP_VER_MINOR = FDB_TUPLE_1[5] #cp ver Minor 0x2A4
#CP_SOURCE = FDB_TUPLE_1[6] #CP source 0x2A5
#CP_DATE_YEAR_UPPER = FDB_TUPLE_1[7] #cp date Year upper 0x2A6
#CP_DATE_YEAR_LOWER = FDB_TUPLE_1[8] #cp date Year lower 0x2A7
#CP_DATE_MONTH = FDB_TUPLE_1[9] #cp date Month  0x2A8
#CP_DATE_DAY = FDB_TUPLE_1[10] #cp date Day 0x2A9
#CP_DATE_HOUR = FDB_TUPLE_1[11] #cp Date Hour 0x2AA
#CP_DATE_MINUTE = FDB_TUPLE_1[11] #cp Date Minute 0x2AB
#CHANNEL_STEP = FDB_TUPLE_1[13] #
#BASEBAND_RAW = int(FDB_TUPLE_1[14])
#LOWER_LIMIT_RAW = FDB_TUPLE_1[15]
#UPPER_LIMIT_RAW = FDB_TUPLE_1[16]
#FIRMWARE_PN = FDB_TUPLE_1[17] # 0x2b3:2c2
#FDB_UNK_BLK_B_INT_1 = FDB_TUPLE_1[18] #0x2C3
#FDB_UNK_BLK_B_INT_2 = FDB_TUPLE_1[19] #0x2C4 Nullpad
#TANAPA = FDB_TUPLE_1[20] #0x2c5:2ce
#FDB_UNK_BLK_C_INT_1 = FDB_TUPLE_1[22] # 0x2cf
#FDB_UNK_BLK_C_INT_2 = FDB_TUPLE_1[23] # 0x2D0
#FDB_UNK_BLK_C_INT_3 = FDB_TUPLE_1[23] # 0x2D1
#FDB_UNK_BLK_C_INT_4 = FDB_TUPLE_1[24] # 0x2d2
#FDB_UNK_BLK_C_INT_5 = FDB_TUPLE_1[25] # 0x2d3
#FDB_UNK_BLK_C_INT_6 = FDB_TUPLE_1[26] # 0x2d4
#FDB_UNK_BLK_C_INT_7 = FDB_TUPLE_1[27] # 0x2d5
#REGION_CODE = FDB_TUPLE_1[28] # region code 0x2d6
#
#
#
#
#MODEL_NUMBER_TUPLE = struct.unpack('>c2scccc2sccccccc',MODEL_NUMBER)
#MODEL_NUMBER_TEST_BYTE = MODEL_NUMBER_TUPLE[1]
#
#if (MODEL_NUMBER_TUPLE[1]).isdigit() == True:
#    if (MODEL_NUMBER_TUPLE[0]).isalpha() == True:  # tests the unit type is alpha only
#        print "DEBUG: Model is 1 clause"
#        MODEL_NUMBER_BYTE_0 = MODEL_NUMBER_TUPLE[0]
#        MODEL_NUMBER_BYTE_1 = MODEL_NUMBER_TUPLE[1]
#        MODEL_NUMBER_BYTE_2 = MODEL_NUMBER_TUPLE[2]
#        MODEL_NUMBER_BYTE_3 = MODEL_NUMBER_TUPLE[3]
#        MODEL_NUMBER_BYTE_4 = MODEL_NUMBER_TUPLE[4]
#        MODEL_NUMBER_BYTE_5 = MODEL_NUMBER_TUPLE[5]
#        MODEL_NUMBER_BYTE_6 = MODEL_NUMBER_TUPLE[6]
#        MODEL_NUMBER_BYTE_7 = MODEL_NUMBER_TUPLE[7]
#        MODEL_NUMBER_BYTE_8 = MODEL_NUMBER_TUPLE[8]
#        MODEL_NUMBER_BYTE_9 = MODEL_NUMBER_TUPLE[9]
#        MODEL_NUMBER_BYTE_10 = MODEL_NUMBER_TUPLE[10]
#        MODEL_NUMBER_BYTE_11 = MODEL_NUMBER_TUPLE[11]
#        MODEL_NUMBER_BYTE_12 = MODEL_NUMBER_TUPLE[12]
#        MODEL_NUMBER_BYTE_13 = MODEL_NUMBER_TUPLE[13]
#else:
#    MODEL_NUMBER_TUPLE = struct.unpack('>2s2scccc2scccccc',MODEL_NUMBER)
#    print "ERROR: model number series is not 2 digits"
#
#
##handle model numbers begining with 2 alphas
#
#
#if(MODEL_NUMBER_TUPLE[1]).isdigit() == True:
#    if (MODEL_NUMBER_TUPLE[0]).isalpha() == True:  # tests the unit type is alpha only
#        print "DEBUG: Model is 2 clause"
#        MODEL_NUMBER_BYTE_0 = MODEL_NUMBER_TUPLE[0]
#        MODEL_NUMBER_BYTE_1 = MODEL_NUMBER_TUPLE[1]
#        MODEL_NUMBER_BYTE_2 = MODEL_NUMBER_TUPLE[2]
#        MODEL_NUMBER_BYTE_3 = MODEL_NUMBER_TUPLE[3]
#        MODEL_NUMBER_BYTE_4 = MODEL_NUMBER_TUPLE[4]
#        MODEL_NUMBER_BYTE_5 = MODEL_NUMBER_TUPLE[5]
#        MODEL_NUMBER_BYTE_6 = MODEL_NUMBER_TUPLE[6]
#        MODEL_NUMBER_BYTE_7 = MODEL_NUMBER_TUPLE[7]
#        MODEL_NUMBER_BYTE_8 = MODEL_NUMBER_TUPLE[8]
#        MODEL_NUMBER_BYTE_9 = MODEL_NUMBER_TUPLE[9]
#        MODEL_NUMBER_BYTE_10 = MODEL_NUMBER_TUPLE[10]
#        MODEL_NUMBER_BYTE_11 = MODEL_NUMBER_TUPLE[11]
#        MODEL_NUMBER_BYTE_12 = MODEL_NUMBER_TUPLE[12]
#        MODEL_NUMBER_BYTE_13 = ""
#else:
#    print "ERROR: model number series is not 2 digits"
#    MODEL_NUMBER_TUPLE = struct.unpack('>3s2scccc2sccccc',MODEL_NUMBER)
#
#        #handle model numbers begining with 3 alphas
#
#if (MODEL_NUMBER_TUPLE[1]).isdigit() == True:
#    if (MODEL_NUMBER_TUPLE[0]).isalpha() == True:  # tests the unit type is alpha only
#        print "DEBUG: Model is 3 clause"
#        MODEL_NUMBER_BYTE_0 = MODEL_NUMBER_TUPLE[0]
#        MODEL_NUMBER_BYTE_1 = MODEL_NUMBER_TUPLE[1]
#        MODEL_NUMBER_BYTE_2 = MODEL_NUMBER_TUPLE[2]
#        MODEL_NUMBER_BYTE_3 = MODEL_NUMBER_TUPLE[3]
#        MODEL_NUMBER_BYTE_4 = MODEL_NUMBER_TUPLE[4]
#        MODEL_NUMBER_BYTE_5 = MODEL_NUMBER_TUPLE[5]
#        MODEL_NUMBER_BYTE_6 = MODEL_NUMBER_TUPLE[6]
#        MODEL_NUMBER_BYTE_7 = MODEL_NUMBER_TUPLE[7]
#        MODEL_NUMBER_BYTE_8 = MODEL_NUMBER_TUPLE[8]
#        MODEL_NUMBER_BYTE_9 = MODEL_NUMBER_TUPLE[9]
#        MODEL_NUMBER_BYTE_10 = MODEL_NUMBER_TUPLE[10]
#        MODEL_NUMBER_BYTE_11 = MODEL_NUMBER_TUPLE[11]
#        MODEL_NUMBER_BYTE_12 = ""
#        MODEL_NUMBER_BYTE_13 = ""
#    else:
#        print "ERROR: model number series is not 2 digits"
#        exit()
#
#
#else:
#    print "ERROR: model number is not single alpha"
#    print "model number tuple %r" % MODEL_NUMBER_TUPLE[0]
#    print "model number tuple state %s" % ((MODEL_NUMBER_TUPLE[1]).isdigit())
#    exit()
#
#
#BASEBAND_MHz = (BASEBAND_RAW * .025)
#LOWER_LIMIT_MHz = (LOWER_LIMIT_RAW*5/1000 + BASEBAND_MHz )
#UPPER_LIMIT_MHz = (UPPER_LIMIT_RAW*5/1000 + BASEBAND_MHz )
#
##calc the tuning piers
#RX_PIERS_1 = (RX_PIERS_TUPLE[0]/200)+BASEBAND_MHz
#RX_PIERS_2 = (RX_PIERS_TUPLE[1]/200)+BASEBAND_MHz
#RX_PIERS_3 = (RX_PIERS_TUPLE[2]/200)+BASEBAND_MHz
#RX_PIERS_4 = (RX_PIERS_TUPLE[3]/200)+BASEBAND_MHz
#RX_PIERS_5 = (RX_PIERS_TUPLE[4]/200)+BASEBAND_MHz
#RX_PIERS_6 = (RX_PIERS_TUPLE[5]/200)+BASEBAND_MHz
#RX_PIERS_7 = (RX_PIERS_TUPLE[6]/200)+BASEBAND_MHz
#
#TX_PIERS_1 = (TX_PIERS_TUPLE[0]/200)+BASEBAND_MHz
#TX_PIERS_2 = (TX_PIERS_TUPLE[1]/200)+BASEBAND_MHz
#TX_PIERS_3 = (TX_PIERS_TUPLE[2]/200)+BASEBAND_MHz
#TX_PIERS_4 = (TX_PIERS_TUPLE[3]/200)+BASEBAND_MHz
#TX_PIERS_5 = (TX_PIERS_TUPLE[4]/200)+BASEBAND_MHz
#TX_PIERS_6 = (TX_PIERS_TUPLE[5]/200)+BASEBAND_MHz
#TX_PIERS_7 = (TX_PIERS_TUPLE[6]/200)+BASEBAND_MHz
#
#RF_TEST_PIERS_TX_1 = (RF_TEST_PIERS_TUPLE[0]/200)+BASEBAND_MHz
#RF_TEST_PIERS_RX_1 = (RF_TEST_PIERS_TUPLE[1]/200)+BASEBAND_MHz
#RF_TEST_PIERS_TX_2 = (RF_TEST_PIERS_TUPLE[2]/200)+BASEBAND_MHz
#RF_TEST_PIERS_RX_2 = (RF_TEST_PIERS_TUPLE[3]/200)+BASEBAND_MHz
#RF_TEST_PIERS_TX_3 = (RF_TEST_PIERS_TUPLE[4]/200)+BASEBAND_MHz
#RF_TEST_PIERS_RX_3 = (RF_TEST_PIERS_TUPLE[5]/200)+BASEBAND_MHz
#RF_TEST_PIERS_TX_4 = (RF_TEST_PIERS_TUPLE[6]/200)+BASEBAND_MHz
#RF_TEST_PIERS_RX_4 = (RF_TEST_PIERS_TUPLE[7]/200)+BASEBAND_MHz
#RF_TEST_PIERS_TX_5 = (RF_TEST_PIERS_TUPLE[8]/200)+BASEBAND_MHz
#RF_TEST_PIERS_RX_5 = (RF_TEST_PIERS_TUPLE[9]/200)+BASEBAND_MHz
#RF_TEST_PIERS_TX_6 = (RF_TEST_PIERS_TUPLE[10]/200)+BASEBAND_MHz
#RF_TEST_PIERS_RX_6 = (RF_TEST_PIERS_TUPLE[11]/200)+BASEBAND_MHz
#RF_TEST_PIERS_TX_7 = (RF_TEST_PIERS_TUPLE[12]/200)+BASEBAND_MHz
#RF_TEST_PIERS_RX_7 = (RF_TEST_PIERS_TUPLE[13]/200)+BASEBAND_MHz



if options.SHOW_TUNE == True:



    print "tuning block length (hex) = ", "0x%x" % TUNING_LENGTH
   


    print TUNING_BLOCK.encode('hex')
    print "rx piers = ", RX_PIERS.encode('hex')
    print "tx piers = ", TX_PIERS.encode('hex')
    print "RF_TEST_PIERS = ", RF_TEST_PIERS.encode('hex')
    print "Baseband MHz = ", BASEBAND_MHz
    print "RX_PIERS_1 = %.3f MHz" % RX_PIERS_1
    print "RX_PIERS_2 = %.3f MHz" % RX_PIERS_2
    print "RX_PIERS_3 = %.3f MHz" % RX_PIERS_3
    print "RX_PIERS_4 = %.3f MHz" % RX_PIERS_4
    print "RX_PIERS_5 = %.3f MHz" % RX_PIERS_5
    print "RX_PIERS_6 = %.3f MHz" % RX_PIERS_6
    print "RX_PIERS_7 = %.3f MHz" % RX_PIERS_7
    print " "
    print "TX_PIERS_1 = %.3f MHz" % TX_PIERS_1
    print "TX_PIERS_2 = %.3f MHz" % TX_PIERS_2
    print "TX_PIERS_3 = %.3f MHz" % TX_PIERS_3
    print "TX_PIERS_4 = %.3f MHz" % TX_PIERS_4
    print "TX_PIERS_5 = %.3f MHz" % TX_PIERS_5
    print "TX_PIERS_6 = %.3f MHz" % TX_PIERS_6
    print "TX_PIERS_7 = %.3f MHz" % TX_PIERS_7
    print " "
    print "RF_TEST_PIERS 1, TX = %.3f MHz , RX = %.3f MHz " % (RF_TEST_PIERS_TX_1, RF_TEST_PIERS_RX_1)
    print "RF_TEST_PIERS 2, TX = %.3f MHz , RX = %.3f MHz " % (RF_TEST_PIERS_TX_2, RF_TEST_PIERS_RX_2)
    print "RF_TEST_PIERS 3, TX = %.3f MHz , RX = %.3f MHz " % (RF_TEST_PIERS_TX_3, RF_TEST_PIERS_RX_3)
    print "RF_TEST_PIERS 4, TX = %.3f MHz , RX = %.3f MHz " % (RF_TEST_PIERS_TX_4, RF_TEST_PIERS_RX_4)
    print "RF_TEST_PIERS 5, TX = %.3f MHz , RX = %.3f MHz " % (RF_TEST_PIERS_TX_5, RF_TEST_PIERS_RX_5)
    print "RF_TEST_PIERS 6, TX = %.3f MHz , RX = %.3f MHz " % (RF_TEST_PIERS_TX_6, RF_TEST_PIERS_RX_6)
    print "RF_TEST_PIERS 7, TX = %.3f MHz , RX = %.3f MHz " % (RF_TEST_PIERS_TX_7, RF_TEST_PIERS_RX_7)

    
    print  "TUNING PIERS header, FILE NAME, MODEL NUMBER, TANAPA, BASEBAND_MHz, LOWER_LIMIT_MHz, UPPER_LIMIT_MHz, RX_PIERS_1, RX_PIERS_2, RX_PIERS_3, RX_PIERS_4, RX_PIERS_5, RX_PIERS_6, RX_PIERS_7, TX_PIERS_1, TX_PIERS_2, TX_PIERS_3, TX_PIERS_4, TX_PIERS_5, TX_PIERS_6, TX_PIERS_7, RF_TEST_PIERS_TX_1, RF_TEST_PIERS_RX_1, RF_TEST_PIERS_TX_2, RF_TEST_PIERS_RX_2, RF_TEST_PIERS_TX_3, RF_TEST_PIERS_RX_3, RF_TEST_PIERS_TX_4, RF_TEST_PIERS_RX_4, RF_TEST_PIERS_TX_5, RF_TEST_PIERS_RX_6, RF_TEST_PIERS_TX_7, RF_TEST_PIERS_RX_7"
    print  "TUNING PIERS, %30s, %16s, %10s, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f" % (options.filename,  MODEL_NUMBER, TANAPA, BASEBAND_MHz, LOWER_LIMIT_MHz, UPPER_LIMIT_MHz, RX_PIERS_1, RX_PIERS_2, RX_PIERS_3, RX_PIERS_4, RX_PIERS_5, RX_PIERS_6, RX_PIERS_7, TX_PIERS_1, TX_PIERS_2, TX_PIERS_3, TX_PIERS_4, TX_PIERS_5, TX_PIERS_6, TX_PIERS_7, RF_TEST_PIERS_TX_1, RF_TEST_PIERS_RX_1, RF_TEST_PIERS_TX_2, RF_TEST_PIERS_RX_2, RF_TEST_PIERS_TX_3, RF_TEST_PIERS_RX_3, RF_TEST_PIERS_TX_4, RF_TEST_PIERS_RX_4, RF_TEST_PIERS_TX_5, RF_TEST_PIERS_RX_6, RF_TEST_PIERS_TX_7, RF_TEST_PIERS_RX_7)


if options.SHOW_FEATURE == True:
    print "feature block length (hex) = ", "0x%x" % FEATURE_BLOCK_LENGTH
    print "feature block start (hex) = ", "0x%x" % FEATURE_BLOCK_START
    print "feature block end (hex) = ", "0x%x" % FEATURE_BLOCK_END
    # print FEATURE_BLOCK.find(STRING_MAGIC)
    print FEATURE_BLOCK.encode('hex')
   



# unpack tuple 2 now, but it size varies
    if len(Feature_List_2) == 0x9:
        FDB_TUPLE_2 = struct.unpack('>BBBBBBBBB',Feature_List_2) # This is the unpack for the Second FDB with channel sizes and such
        FDB2_LEN_9_INT_1 = FDB_TUPLE_2[0] # Trunking personalities 0x2db
        FDB2_LEN_9_INT_2 = FDB_TUPLE_2[1] # Signaling 0x2dc trunking high and conventional low, FF is everything
        FDB2_LEN_9_INT_3 = FDB_TUPLE_2[2] # control head (nibble based) 0x2dd
        FDB2_LEN_9_INT_4 = FDB_TUPLE_2[3] # 0x2de UNK (nibbles)
        FDB2_LEN_9_INT_5 = FDB_TUPLE_2[4] # 0x2df UNK (nibbles)
        FDB2_LEN_9_INT_6 = FDB_TUPLE_2[5] # 0x2e0 UNK (nibbles)
        FDB2_LEN_9_INT_7 = FDB_TUPLE_2[6] # 0x2e1 UNK (nibbles)
        FDB2_LEN_9_INT_8 = FDB_TUPLE_2[7] # 0x2e2 Conventional Pers number
        FDB2_LEN_9_INT_9 = FDB_TUPLE_2[8] # 0x2e3 UNK (nibbles)
        print "FDB2, %60s, MODEL -, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, Size = %2d, %x, %x, %x, %x, %x, %x, %x, %x, %x" % (options.filename, MODEL_NUMBER_BYTE_0, MODEL_NUMBER_BYTE_1, MODEL_NUMBER_BYTE_2, MODEL_NUMBER_BYTE_3, MODEL_NUMBER_BYTE_4, MODEL_NUMBER_BYTE_5, MODEL_NUMBER_BYTE_6, MODEL_NUMBER_BYTE_7, MODEL_NUMBER_BYTE_8, MODEL_NUMBER_BYTE_9, MODEL_NUMBER_BYTE_10, MODEL_NUMBER_BYTE_11, MODEL_NUMBER_BYTE_12, MODEL_NUMBER_BYTE_13, (len(Feature_List_2)),  FDB2_LEN_9_INT_1, FDB2_LEN_9_INT_2, FDB2_LEN_9_INT_3, FDB2_LEN_9_INT_4, FDB2_LEN_9_INT_5, FDB2_LEN_9_INT_6, FDB2_LEN_9_INT_7, FDB2_LEN_9_INT_8, FDB2_LEN_9_INT_9)

    elif len(Feature_List_2) == 0xA:
        FDB_TUPLE_2 = struct.unpack('>BBBBBBBBBB',Feature_List_2)
        FDB2_LEN_A_INT_1  = FDB_TUPLE_2[0]
        FDB2_LEN_A_INT_2  = FDB_TUPLE_2[1]
        FDB2_LEN_A_INT_3  = FDB_TUPLE_2[2]
        FDB2_LEN_A_INT_4  = FDB_TUPLE_2[3]
        FDB2_LEN_A_INT_5  = FDB_TUPLE_2[4]
        FDB2_LEN_A_INT_6  = FDB_TUPLE_2[5]
        FDB2_LEN_A_INT_7  = FDB_TUPLE_2[6]
        FDB2_LEN_A_INT_8  = FDB_TUPLE_2[7]
        FDB2_LEN_A_INT_9  = FDB_TUPLE_2[8]
        FDB2_LEN_A_INT_10 = FDB_TUPLE_2[9] # 0x2e4 UNK (nibbles)
        print "FDB2, %60s, MODEL -, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, Size = %2d, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x" % (options.filename, MODEL_NUMBER_BYTE_0, MODEL_NUMBER_BYTE_1, MODEL_NUMBER_BYTE_2, MODEL_NUMBER_BYTE_3, MODEL_NUMBER_BYTE_4, MODEL_NUMBER_BYTE_5, MODEL_NUMBER_BYTE_6, MODEL_NUMBER_BYTE_7, MODEL_NUMBER_BYTE_8, MODEL_NUMBER_BYTE_9, MODEL_NUMBER_BYTE_10, MODEL_NUMBER_BYTE_11, MODEL_NUMBER_BYTE_12, MODEL_NUMBER_BYTE_13, (len(Feature_List_2)), FDB2_LEN_A_INT_1, FDB2_LEN_A_INT_2, FDB2_LEN_A_INT_3, FDB2_LEN_A_INT_4, FDB2_LEN_A_INT_5, FDB2_LEN_A_INT_6, FDB2_LEN_A_INT_7, FDB2_LEN_A_INT_8, FDB2_LEN_A_INT_9, FDB2_LEN_A_INT_10)

    elif len(Feature_List_2) == 0xE:
        FDB_TUPLE_2 = struct.unpack('>BBBBBBBBBBBBBB',Feature_List_2)
        FDB2_LEN_E_INT_1  = FDB_TUPLE_2[0]
        FDB2_LEN_E_INT_2  = FDB_TUPLE_2[1]
        FDB2_LEN_E_INT_3  = FDB_TUPLE_2[2]
        FDB2_LEN_E_INT_4  = FDB_TUPLE_2[3]
        FDB2_LEN_E_INT_5  = FDB_TUPLE_2[4]
        FDB2_LEN_E_INT_6  = FDB_TUPLE_2[5]
        FDB2_LEN_E_INT_7  = FDB_TUPLE_2[6]
        FDB2_LEN_E_INT_8  = FDB_TUPLE_2[7]
        FDB2_LEN_E_INT_9  = FDB_TUPLE_2[8]
        FDB2_LEN_E_INT_10 = FDB_TUPLE_2[9]  # 0x2e4 UNK (nibbles)
        FDB2_LEN_E_INT_11 = FDB_TUPLE_2[10] # 0x2e5 UNK (nibbles)
        FDB2_LEN_E_INT_12 = FDB_TUPLE_2[11] # 0x2e6 UNK (nibbles)
        FDB2_LEN_E_INT_13 = FDB_TUPLE_2[12] # 0x2e7 UNK (nibbles)
        FDB2_LEN_E_INT_14 = FDB_TUPLE_2[13] # 0x2e8 UNK (nibbles)
        print "FDB2, %60s, MODEL -, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, Size = %2d, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x" % (options.filename, MODEL_NUMBER_BYTE_0, MODEL_NUMBER_BYTE_1, MODEL_NUMBER_BYTE_2, MODEL_NUMBER_BYTE_3, MODEL_NUMBER_BYTE_4, MODEL_NUMBER_BYTE_5, MODEL_NUMBER_BYTE_6, MODEL_NUMBER_BYTE_7, MODEL_NUMBER_BYTE_8, MODEL_NUMBER_BYTE_9, MODEL_NUMBER_BYTE_10, MODEL_NUMBER_BYTE_11, MODEL_NUMBER_BYTE_12, MODEL_NUMBER_BYTE_13, (len(Feature_List_2)), FDB2_LEN_E_INT_1, FDB2_LEN_E_INT_2, FDB2_LEN_E_INT_3, FDB2_LEN_E_INT_4, FDB2_LEN_E_INT_5, FDB2_LEN_E_INT_6, FDB2_LEN_E_INT_7, FDB2_LEN_E_INT_8, FDB2_LEN_E_INT_9, FDB2_LEN_E_INT_10, FDB2_LEN_E_INT_11, FDB2_LEN_E_INT_12, FDB2_LEN_E_INT_13, FDB2_LEN_E_INT_14)

    elif len(Feature_List_2) == 0x10:
        FDB_TUPLE_2 = struct.unpack('>BBBBBBBBBBBBBBBB',Feature_List_2)
        FDB2_LEN_10_INT_1  = FDB_TUPLE_2[0]
        FDB2_LEN_10_INT_2  = FDB_TUPLE_2[1]
        FDB2_LEN_10_INT_3  = FDB_TUPLE_2[2]
        FDB2_LEN_10_INT_4  = FDB_TUPLE_2[3]
        FDB2_LEN_10_INT_5  = FDB_TUPLE_2[4]
        FDB2_LEN_10_INT_6  = FDB_TUPLE_2[5]
        FDB2_LEN_10_INT_7  = FDB_TUPLE_2[6]
        FDB2_LEN_10_INT_8  = FDB_TUPLE_2[7]
        FDB2_LEN_10_INT_9  = FDB_TUPLE_2[8]
        FDB2_LEN_10_INT_10 = FDB_TUPLE_2[9]  # 0x2e4 UNK (nibbles)
        FDB2_LEN_10_INT_11 = FDB_TUPLE_2[10] # 0x2e5 UNK (nibbles)
        FDB2_LEN_10_INT_12 = FDB_TUPLE_2[11] # 0x2e6 UNK (nibbles) 0 or 1?
        FDB2_LEN_10_INT_13 = FDB_TUPLE_2[12] # 0x2e7 UNK (nibbles) Unused?
        FDB2_LEN_10_INT_14 = FDB_TUPLE_2[13] # 0x2e8 UNK (nibbles) Unused
        FDB2_LEN_10_INT_15 = FDB_TUPLE_2[14] # 0x2e9 UNK (nibbles) Unused
        FDB2_LEN_10_INT_16 = FDB_TUPLE_2[15] # 0x2ea UNK (nibbles) Unused
        print "FDB2, %60s, MODEL -, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, Size = %2d, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x" % (options.filename, MODEL_NUMBER_BYTE_0, MODEL_NUMBER_BYTE_1, MODEL_NUMBER_BYTE_2, MODEL_NUMBER_BYTE_3, MODEL_NUMBER_BYTE_4, MODEL_NUMBER_BYTE_5, MODEL_NUMBER_BYTE_6, MODEL_NUMBER_BYTE_7, MODEL_NUMBER_BYTE_8, MODEL_NUMBER_BYTE_9, MODEL_NUMBER_BYTE_10, MODEL_NUMBER_BYTE_11, MODEL_NUMBER_BYTE_12, MODEL_NUMBER_BYTE_13, (len(Feature_List_2)), FDB2_LEN_10_INT_1, FDB2_LEN_10_INT_2, FDB2_LEN_10_INT_3, FDB2_LEN_10_INT_4, FDB2_LEN_10_INT_5, FDB2_LEN_10_INT_6, FDB2_LEN_10_INT_7, FDB2_LEN_10_INT_8, FDB2_LEN_10_INT_9, FDB2_LEN_10_INT_10, FDB2_LEN_10_INT_11, FDB2_LEN_10_INT_12, FDB2_LEN_10_INT_13, FDB2_LEN_10_INT_14, FDB2_LEN_10_INT_15, FDB2_LEN_10_INT_16)


# print "FDB2, %60s, Size = %2d, %s" % (options.filename, (len(Feature_List_2)), )

#SERIAL_NUMBER = struct.unpack('>10s',Feature_List_1[0:10])
#  print  options.filename, " FDBTUPLE1", FDB_TUPLE_1
#unpak = int(struct.unpack('>2s',Feature_List_1[10:12])[0])
    if int(SPACE_1_FDB_1) != 0x0000:
            print "Serial number space NOT found"
#print  "%30s, %10s, 0x%x, %16s, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x,  %d, %d, %d, %16s, 0x%x, 0x%x, %10s, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x" % (options.filename, SERIAL_NUMBER, SPACE_1_FDB_1, MODEL_NUMBER, SPACE_2_FDB_1, CP_VER_MAJOR, CP_VER_MINOR, CP_SOURCE, CP_DATE_YEAR_UPPER, CP_DATE_YEAR_LOWER, CP_DATE_MONTH, CP_DATE_DAY, SPACE_3_FDB_1, CHANNEL_STEP, BASEBAND_RAW,  LOWER_LIMIT_RAW, UPPER_LIMIT_RAW, FIRMWARE_PN, FDB_UNK_BLK_B_INT_1,  FDB_UNK_BLK_B_INT_2, TANAPA, FDB_UNK_BLK_C_INT_1, FDB_UNK_BLK_C_INT_2, FDB_UNK_BLK_C_INT_3, FDB_UNK_BLK_C_INT_4, FDB_UNK_BLK_C_INT_5, FDB_UNK_BLK_C_INT_6, FDB_UNK_BLK_C_INT_7, REGION_CODE)
    print  "FDB1, %30s, %10s, %x, %16s, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x,  %.1f MHz, %.1f MHz, %.1f MHz, %16s, %x, %x, %10s, %x, %x, %x, %x, %x, %x, %x, %x" % (options.filename, SERIAL_NUMBER, SPACE_1_FDB_1, MODEL_NUMBER, SPACE_2_FDB_1, CP_VER_MAJOR, CP_VER_MINOR, CP_SOURCE, CP_DATE_YEAR_UPPER, CP_DATE_YEAR_LOWER, CP_DATE_MONTH, CP_DATE_DAY, CP_DATE_HOUR, CP_DATE_MINUTE, CHANNEL_STEP, BASEBAND_MHz,  LOWER_LIMIT_MHz, UPPER_LIMIT_MHz, FIRMWARE_PN, FDB_UNK_BLK_B_INT_1,  FDB_UNK_BLK_B_INT_2, TANAPA, FDB_UNK_BLK_C_INT_1, FDB_UNK_BLK_C_INT_2, FDB_UNK_BLK_C_INT_3, FDB_UNK_BLK_C_INT_4, FDB_UNK_BLK_C_INT_5, FDB_UNK_BLK_C_INT_6, FDB_UNK_BLK_C_INT_7, REGION_CODE)



# print "buffer",  unpak.encode('hex')
    print "Serial Number  = ","%r" % SERIAL_NUMBER
    print "Model Number   = ","%r" % MODEL_NUMBER
    print "Channel Step   = ","0x%x" % CHANNEL_STEP
    print "TANAPA         = ","%r" % TANAPA
    print "Firmware P/N   = ","%r" % FIRMWARE_PN
    print "Base band      = ","%r MHz" % BASEBAND_MHz
    print "Lower limit    = ","%r MHz" % LOWER_LIMIT_MHz
    print "Upper limit    = ","%r MHz" % UPPER_LIMIT_MHz

# print the model and unk blocks
    if len(Feature_List_2) == 0x9:
        print "UNKNOWN BYTES, %s, %s, %s, %s, %s, %s, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x" % (MODEL_NUMBER_BYTE_0, MODEL_NUMBER_BYTE_1, MODEL_NUMBER_BYTE_4, MODEL_NUMBER_BYTE_6, MODEL_NUMBER_BYTE_7, TANAPA, FDB_UNK_BLK_B_INT_1, FDB_UNK_BLK_C_INT_1, FDB_UNK_BLK_C_INT_2, FDB_UNK_BLK_C_INT_3, FDB_UNK_BLK_C_INT_4, FDB_UNK_BLK_C_INT_5, FDB_UNK_BLK_C_INT_6, FDB_UNK_BLK_C_INT_7, FDB2_LEN_9_INT_3, FDB2_LEN_9_INT_4, FDB2_LEN_9_INT_5, FDB2_LEN_9_INT_6, FDB2_LEN_9_INT_7, FDB2_LEN_9_INT_9)

    elif len(Feature_List_2) == 0xA:
        print "UNKNOWN BYTES, %s, %s, %s, %s, %s, %s, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x" % (MODEL_NUMBER_BYTE_0, MODEL_NUMBER_BYTE_1, MODEL_NUMBER_BYTE_4, MODEL_NUMBER_BYTE_6, MODEL_NUMBER_BYTE_7, TANAPA, FDB_UNK_BLK_B_INT_1, FDB_UNK_BLK_C_INT_1, FDB_UNK_BLK_C_INT_2, FDB_UNK_BLK_C_INT_3, FDB_UNK_BLK_C_INT_4, FDB_UNK_BLK_C_INT_5, FDB_UNK_BLK_C_INT_6, FDB_UNK_BLK_C_INT_7, FDB2_LEN_A_INT_3, FDB2_LEN_A_INT_4, FDB2_LEN_A_INT_5, FDB2_LEN_A_INT_6, FDB2_LEN_A_INT_7, FDB2_LEN_A_INT_9, FDB2_LEN_A_INT_10)
                                        
    elif len(Feature_List_2) == 0xE:
        print "UNKNOWN BYTES, %s, %s, %s, %s, %s, %s, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x" % (MODEL_NUMBER_BYTE_0, MODEL_NUMBER_BYTE_1, MODEL_NUMBER_BYTE_4, MODEL_NUMBER_BYTE_6, MODEL_NUMBER_BYTE_7, TANAPA, FDB_UNK_BLK_B_INT_1, FDB_UNK_BLK_C_INT_1, FDB_UNK_BLK_C_INT_2, FDB_UNK_BLK_C_INT_3, FDB_UNK_BLK_C_INT_4, FDB_UNK_BLK_C_INT_5, FDB_UNK_BLK_C_INT_6, FDB_UNK_BLK_C_INT_7, FDB2_LEN_E_INT_3, FDB2_LEN_E_INT_4, FDB2_LEN_E_INT_5, FDB2_LEN_E_INT_6, FDB2_LEN_E_INT_7, FDB2_LEN_E_INT_9, FDB2_LEN_E_INT_10, FDB2_LEN_E_INT_11, FDB2_LEN_E_INT_12, FDB2_LEN_E_INT_13, FDB2_LEN_E_INT_14)


    elif len(Feature_List_2) == 0x10:
        print "UNKNOWN BYTES, %s, %s, %s, %s, %s, %s, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x, %x" % (MODEL_NUMBER_BYTE_0, MODEL_NUMBER_BYTE_1, MODEL_NUMBER_BYTE_4, MODEL_NUMBER_BYTE_6, MODEL_NUMBER_BYTE_7, TANAPA, FDB_UNK_BLK_B_INT_1, FDB_UNK_BLK_C_INT_1, FDB_UNK_BLK_C_INT_2, FDB_UNK_BLK_C_INT_3, FDB_UNK_BLK_C_INT_4, FDB_UNK_BLK_C_INT_5, FDB_UNK_BLK_C_INT_6, FDB_UNK_BLK_C_INT_7, FDB2_LEN_10_INT_3, FDB2_LEN_10_INT_4, FDB2_LEN_10_INT_5, FDB2_LEN_10_INT_6, FDB2_LEN_10_INT_7, FDB2_LEN_10_INT_9, FDB2_LEN_10_INT_10, FDB2_LEN_10_INT_11, FDB2_LEN_10_INT_12, FDB2_LEN_10_INT_13, FDB2_LEN_10_INT_14, FDB2_LEN_10_INT_15, FDB2_LEN_10_INT_16)
                      




# print "Serial number = " , "%r"  % SERIAL_NUMBER[0]

#print "Model number = " , "%r"  % MODEL_NUMBER[0]






if options.SHOW_PROGRAMING == True:
 
    

    print "programing block length (hex) = ", "0x%x" % PROGRAMING_BLOCK_LENGTH
    print "programing block start (hex) = ", "0x%x" % PROGRAMING_BLOCK_START
    print "programing block end (hex) = ", "0x%x" % PROGRAMING_BLOCK_END
    #print PROGRAMING_BLOCK.encode('hex')
    print "toc header start (hex) = ", "0x%x" % TOC_HEADER_START
    print "toc header length (hex) = ", "0x%x" % TOC_HEADER_LENGTH
    print "toc header data (hex) = ", TOC_HEADER_DATA.encode('hex')
    print "toc header checksum = ", "0x%x" % chksm8(TOC_HEADER_DATA)

    print "toc start (hex) = ", "0x%x" % TOC_START
    print "toc length (hex) = ", "0x%x" % TOC_LENGTH
    print "toc data (hex) = ", TOC_DATA.encode('hex')
    print "toc header checksum = ", "0x%x" % chksm8(TOC_DATA)
    TOC_POINTERS= parse_toc(TOC_DATA)
    print "tocpointers length",  len(TOC_POINTERS)
    for i in range(len(TOC_POINTERS)):
        print "Block ", "0x%02X" % i ," =>" ,TOC_POINTERS[i].encode('hex')



    #setup the Progaming list tuple
    #    PROGRAMMING_LIST = list()
    #
    #    reader = StringIO(PROGRAMING_BLOCK)
    #    for size, repeat, chunk, checksum in chunks(reader):
    #        print "\nsize:", "0x%x" % size
    #        print "repeat:", "0x%x" % repeat
    #        print "total:", "0x%x" % (size * repeat)
    #        print "data:"
    #        #print hexprint(chunk)
    #        PROGRAMMING_LIST.append(chunk)
    #        print "checksum:", "0x%x" % checksum
    #
    #
    #
    #    print "number of programing block = ", "0x%x" % len(PROGRAMMING_LIST)
    #    print "PRG-BLK-0 = ", PROGRAMMING_LIST[0].encode('hex')
    #    PRG_BLK_1 = PROGRAMMING_LIST[1].encode('hex')
    #
    #    #ProgramingBlock1struct.unpack('>10sH16sHBBBBBBBHBHHH16sBB10sBBBBBBBB',)
    #    print  "PROG-BLK-1, %30s, %16s, %10s, 0x%s" % (options.filename, MODEL_NUMBER, TANAPA, PRG_BLK_1)
    #
    #    print "PRG-BLK-2 = ", PROGRAMMING_LIST[2].encode('hex')
    #    print "PRG-BLK-3 = ", PROGRAMMING_LIST[3].encode('hex')
    #    print "PRG-BLK-4 = ", PROGRAMMING_LIST[4].encode('hex')
    #    print "PRG-BLK-5 = ", PROGRAMMING_LIST[5].encode('hex')
    #    print "PRG-BLK-6 = ", PROGRAMMING_LIST[6].encode('hex')
    #    print "PRG-BLK-7 = ", PROGRAMMING_LIST[7].encode('hex')
    #    print "PRG-BLK-8 = ", PROGRAMMING_LIST[8].encode('hex')
if options.SHOW_PROGRAMING == "False" and options.SHOW_FEATURE == "False" and options.SHOW_TUNE == "False":
    print "no data shown"



