#!/usr/bin/env python3

from random import getrandbits
from ipaddress import IPv4Network, IPv4Address, IPv6Network, IPv6Address
import argparse


def get_n_different_bit_arrays(n, array_size):
    if n > 2 ** array_size:
        raise Exception('Too many addresses to generate')
    parents = set()
    while len(parents) < n:
        a = getrandbits(array_size)
        if a not in parents:
            parents.add(a)
    parents = sorted(list(parents))
    return parents


def get_addresses(n_addresses, prefix, type='ipv4'):
    if type == 'ipv4':
        subnet_call = IPv4Network
        address_call = IPv4Address
    elif type == 'ipv6':
        subnet_call = IPv6Network
        address_call = IPv6Address
    else:
        raise Exception('Type must be ipv4 or ipv6')
    subnet = subnet_call(prefix)

    bit_list = get_n_different_bit_arrays(n_addresses, subnet.max_prefixlen -
                                          subnet.prefixlen)

    addr = [str(address_call(subnet.network_address + bits)) for bits in bit_list]

    return addr


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--number", required=True,
                    help="number of addresses to generate")
    ap.add_argument("-p", "--prefix", required=True,
                    help="prefix to generate addresses from")
    ap.add_argument("-t", "--type", required=False, default='ipv6',
                    help="type of address to generate (ipv4 or ipv6)")
    args = vars(ap.parse_args())
    for x in get_addresses(int(args['number']), args['prefix'], args['type']):
        print(x)
