
# Allows converting binary codeplugs to .srec format and back for Waris Radios

> Copyright Bryan Fields 2020
> Licensed under the GPLv2.

## This is really crappy code, it needs to be rewritten.  

# Overview

The Motorola CPS allows you to load and save a *.srec file, which is
a Srecord, but with some extra crap on it.  You can't save it as .srec
if it's a .cpg, but you can open and save it as the same file as .srec.

This can be really handy for testing features in the binary codeplug files
such as what bit does what.  Note that the binary file either from the 
Codeplug tool, or the default codeplugs will have 0x0000-0x027F in it which
is the tuning area.  The CPS doesn't save this data, it starts at 0x0280, 
so don't just write this back into your radio blindly!

# Requirements 

* bash (sh might work)
* dd 
* xxd
* srec_cat
 
The only thing up there that's not a default *nix utility is [srec_cat](http://srecord.sourceforge.net/)
'apt-get install srecord' should be all you need.

# Questions?
bryan@bryanfields.net

I will not reply to basic questions you should know if you're doing this.  I will not do phone support for this.
I don't want to hear about your VFD duties, or other banal shit.  

That said, I'd really love to hear about other hacking you might be doing.  There is the elusive FPP for mobileswhich still needs to be found.  

