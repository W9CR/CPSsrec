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
                  help="input file to convert", metavar="FILE" )

parser.add_option("-t", "--tuning", action="store_true", dest="SHOW_TUNE", default="False", help="show tuning block")

parser.add_option("-F", "--feature", action="store_true", dest="SHOW_FEATURE", default="False", help="show feature block")

parser.add_option("-p", "--programing", action="store_true", dest="SHOW_PROGRAMING", default="False", help="show programing block")

(options, args) = parser.parse_args()

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

reader = StringIO(data)
integer, short = struct.unpack('>ih', reader.read(6))
STRING_MAGIC = 0x80

