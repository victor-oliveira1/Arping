# Arping
Arping CLI implemented in Python3  
This is my attempt at recreate arping CLI in Python3  
It's necessary root permissions  

usage: arping.py [-h] [-b] [-D] [-A] [-c count] -I device [-s source] [-F]
                 destination

positional arguments:  
  destination  Ask for what ip address  

optional arguments:  
  -h, --help   show this help message and exit  
  -b           Keep broadcasting, don't go unicast  
  -D           Duplicate address detection mode  
  -A           ARP answer mode, update your neighbours  
  -c count     How many packets to send  
  -I device    Which ethernet device to use  
  -s source    Source ip address  
  -F           Flood MODE!!!  
  
  

![ARPING](https://raw.githubusercontent.com/victor-oliveira1/Arping/master/Arping.png)
