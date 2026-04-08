#! /usr/bin/env python3
# Secret generation
# Copyright © Stephen Irons 2026

import argparse
import base64
import math
#import os
import random
#import sys

alphabets = {
    'base32-crockford': '0123456789ABCDEFGHJKMNPQRSTVWXYZ', 
    'base32-rfc4648'  : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
    'base24-microsoft': 'BCDFGHJKMPQRTVWXY2346789',
}

def gen_secret(group_spec, separator='-'):
    data = []
    total_bits = 0
    for ngroups, group_size, alphabet in group_spec:
        nint = len(alphabet)
        partial_bits = math.log(nint, 2)
        for _ in range(ngroups):
            gr = ''.join([alphabet[random.randrange(0, nint)] for _ in range(group_size)])
            data.append(gr)
            total_bits += group_size * partial_bits

    secret = separator.join(data)
    return (secret, total_bits)
    
    
def calculate_group_size(size, group_size_max=5):
    if size < group_size_max:
        return size
    diffs = {}
    
    # if size < group_size_max:
    #    return size
 
    for group_size in range(group_size_max, 0, -1):
        if group_size > size:
            continue
            
        ngroups, other = divmod(size, group_size)
        print(size, group_size, ngroups, other)
        if ngroups == 0:
            ngroups = 1
            other = 0
            
        if other == 0:
            diff = 0
        else:
            diff = group_size - other

        # print(size, group_size, ngroups, other, diff)

        if diff not in diffs:
            diffs[diff] = []
        if ngroups <= group_size:
            diffs[diff].append((ngroups, group_size, other))

    for diff in sorted(diffs):
        print(diff, diffs[diff])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a Crockford base32 secret')
    parser.add_argument(
        '-c',
        '--chars',
        type=int,
        default=16,
        help='Number of random characters to generate'
    )
    parser.add_argument(
        '-a',
        '--alphabet',
        default='base32-crockford',
        help='Character alphabet'
    )
    args = parser.parse_args()
    
    if args.chars <= 0:
        parser.error('--chars must be a positive integer')

    group_spec = [[4, 5, alphabets[args.alphabet]]]

    secret, bits = gen_secret(group_spec)
    print(secret)
    print(bits)


# Bits
# Alphabet name
# Alphabet chars
# Group-spec
#   * number of groups
#   * group_size
#   * alphabet-name or 
        
         
#for i in range(1, 128):
#    print(i)
#    print('----')
#    calculate_group_size(i)
#    
#    print()

