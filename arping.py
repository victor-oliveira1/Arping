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
import time

ETH_P_ARP = 0x0806
mac_broadcast = binascii.unhexlify('FF' * 6)
ipaddr_local = socket.gethostbyname(socket.gethostname())
buffer = 2048
mac_recv = None
sleep_time = 1

def GetInterfaces():
    '''Returns a list of available interfaces'''
    interface = list()
    for i in socket.if_nameindex():
        interface.append(i[1])
    return interface

def _create_packet():
    if mac_recv:
        mac_dst = mac_recv
        tha = mac_recv
    else:
        mac_dst = mac_broadcast
        tha = mac_broadcast

    if args.b or args.s != ipaddr_local:
        mac_dst = mac_broadcast
        tha = mac_broadcast

    if args.A:
        op = 0x02
    else:
        op = 0x01
    mac_src = mac_local
    ether_type = ETH_P_ARP
    hrd = 0x01
    pro = 0x0800
    hln = 0x06
    pln = 0x04
    sha = mac_local
    spa = socket.inet_aton(args.s)
    tpa = socket.inet_aton(args.destination)
    packet = struct.pack('!6s6sHHHBBH6s4s6s4s',
                             mac_dst, mac_src, ether_type,
                             hrd, pro, hln, pln, op, sha,
                             spa, tha, tpa)
    return packet








parser = argparse.ArgumentParser()
parser.add_argument('destination',
                    help='Ask for what ip address',
                    type=ipaddress.ip_address)
parser.add_argument('-b',
                    help='Keep broadcasting, don\'t go unicast',
                    action='store_true')
parser.add_argument('-D',
                    help='Duplicate address detection mode',
                    action='store_true')
parser.add_argument('-A',
                    help='ARP answer mode, update your neighbours',
                    action='store_true')
parser.add_argument('-c',
                    metavar='count',
                    help='How many packets to send',
                    type=int)
parser.add_argument('-I',
                    metavar='device',
                    help='Which ethernet device to use',
                    choices=GetInterfaces(),
                    required=True)
parser.add_argument('-s',
                    metavar='source',
                    help='Source ip address',
                    type=ipaddress.ip_address,
                    default=ipaddr_local)
parser.add_argument('-F',
                    help='Flood MODE!!!',
                    action='store_true',
                    default=False)
args = parser.parse_args()

args.s = args.s.exploded   
args.destination = args.destination.exploded

try:
    sock = socket.socket(socket.AF_PACKET,
                         socket.SOCK_RAW,
                         ETH_P_ARP)
except PermissionError:
    print('You need to be root.')
    exit(1)
sock.bind((args.I, ETH_P_ARP))
mac_local = sock.getsockname()[4]

if args.F:
        sleep_time = 0

if args.D:
        args.s = '0.0.0.0'
        args.c = 1
        sleep_time = 0

print('ARPING {} from {} {}'.format(args.destination,
                                args.s, args.I))
i = 0
while True:
    try:
        if args.c:
            if i == args.c:
                break
            
        sock.send(_create_packet())
        if args.A:
            pass
        else:
            while True:
                recv = sock.recv(buffer)
                mac_src_recv = recv[0:6]
                op = recv[21]
                if mac_src_recv == mac_local \
                   and op == 2:
                    break
            mac_recv = recv[6:12]
            mac_recv_decoded = binascii.hexlify(mac_recv).decode().upper()
            mac_recv_formatted = ':'.join(mac_recv_decoded[i:i+2] for i in range(0,12,2))
            print('Unicast reply from {} [{}]  {}ms'.format(args.destination,
                                                            mac_recv_formatted,
                                                            10))

        i += 1
        time.sleep(sleep_time)
    except KeyboardInterrupt:
        break

print('Sent {0} probes\nReceived {0} response(s)'.format(i))
exit(0)
