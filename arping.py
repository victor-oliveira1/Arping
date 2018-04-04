#!/bin/python3
#victor.oliveira@gmx.com

'''
Packet format:
--------------

To communicate mappings from <protocol, address> pairs to 48.bit
Ethernet addresses, a packet format that embodies the Address
Resolution protocol is needed.  The format of the packet follows.

    Ethernet transmission layer (not necessarily accessible to
         the user):
        48.bit: Ethernet address of destination
        48.bit: Ethernet address of sender
        16.bit: Protocol type = ether_type$ADDRESS_RESOLUTION
    Ethernet packet data:
        16.bit: (ar$hrd) Hardware address space (e.g., Ethernet,
                         Packet Radio Net.)
        16.bit: (ar$pro) Protocol address space.  For Ethernet
                         hardware, this is from the set of type
                         fields ether_typ$<protocol>.
         8.bit: (ar$hln) byte length of each hardware address
         8.bit: (ar$pln) byte length of each protocol address
        16.bit: (ar$op)  opcode (ares_op$REQUEST | ares_op$REPLY)
        nbytes: (ar$sha) Hardware address of sender of this
                         packet, n from the ar$hln field.
        mbytes: (ar$spa) Protocol address of sender of this
                         packet, m from the ar$pln field.
        nbytes: (ar$tha) Hardware address of target of this
                         packet (if known).
        mbytes: (ar$tpa) Protocol address of target.
'''

import socket
import struct
import argparse
import binascii
import ipaddress

ETH_P_ARP = 0x0806
mac_broadcast = binascii.unhexlify('FF' * 6)
ipaddr_local = socket.gethostbyname(socket.gethostname())

class IPv4Address:
    '''Argparse helper to validate IPv4 Addresses'''
    def __init__(self, address):
        try:
            ipaddress.ip_address(address)
            pass
        except:
            raise ValueError()

def GetInterfaces():
    '''Returns a list of available interfaces'''
    interface = list()
    for i in socket.if_nameindex():
        interface.append(i[1])
    return interface

parser = argparse.ArgumentParser()
parser.add_argument('destination',
                    help='Ask for what ip address',
                    type=IPv4Address)
parser.add_argument('-f',
                    help='Quit on first reply',
                    action='store_true')
parser.add_argument('-q',
                    help='Be quiet',
                    action='store_true')
parser.add_argument('-b',
                    help='Keep broadcasting, don\'t go unicast',
                    action='store_true')
parser.add_argument('-D',
                    help='Duplicate address detection mode',
                    action='store_true')
parser.add_argument('-U',
                    help='Unsolicited ARP mode, update your neighbours',
                    action='store_true')
parser.add_argument('-A',
                    help='ARP answer mode, update your neighbours',
                    action='store_true')
parser.add_argument('-V',
                    help='Print version and exit',
                    action='store_true')
parser.add_argument('-c',
                    metavar='count',
                    help='How many packets to send',
                    type=int)
parser.add_argument('-w',
                    metavar='timeout',
                    help='How long to wait for a reply',
                    type=int)
parser.add_argument('-I',
                    metavar='device',
                    help='Which ethernet device to use',
                    choices=GetInterfaces(),
                    required=True)
parser.add_argument('-s',
                    metavar='source',
                    help='Source ip address',
                    type=IPv4Address,
                    default=ipaddr_local)
args = parser.parse_args()

interface = 'wlp2s0'
destination = '10.50.0.1'

sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, ETH_P_ARP)
sock.bind((interface, ETH_P_ARP))
mac_local = sock.getsockname()[4]

#Frame Header
mac_dst = mac_broadcast
mac_src = mac_local
ether_type = ETH_P_ARP
frame_header = struct.pack('!6s6sH', mac_dst, mac_src, ether_type)
#Frame ARP Data
hrd = 0x01
pro = 0x0800
hln = 0x06
pln = 0x04
op = 0x01
sha = mac_local
spa = socket.inet_aton(ipaddr_local)
tha = mac_broadcast
tpa = socket.inet_aton(destination)
frame_data = struct.pack('!HHBBH6s4s6s4s', hrd, pro, hln, pln, op, sha, spa, tha, tpa)

frame = frame_header + frame_data
sock.send(frame)
