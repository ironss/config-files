#! /usr/bin/env python3
# Secret generation
# Copyright © Stephen Irons 2026

import argparse
import base64
import math
#import os
import random
#import sys

RFC4648_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
TRANSLATION_TABLE = str.maketrans(RFC4648_ALPHABET, CROCKFORD_ALPHABET)

def b32encode_crockford(data):
    return base64.b32encode(data).decode('ascii').rstrip('=').translate(TRANSLATION_TABLE)

def group_str(s, size=4, separator='-'):
    return separator.join([ s[i:i+size] for i in range(0, len(s), size)])

def gen_crockford(nbytes=10):
    data = random.randbytes(nbytes)
    data_b32_crockford = b32encode_crockford(data)
    return data_b32_crockford 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a Crockford base32 secret')
    parser.add_argument(
        '-c',
        '--chars',
        type=int,
        default=16,
        help='Number of random characters to generate'
    )
    args = parser.parse_args()
    
    if args.chars <= 0:
        parser.error('--chars must be a positive integer')

    nchars = args.chars
    nbits = int(math.ceil(args.chars * 5))
    nbytes = int(math.ceil(nbits / 8))

    data_b32 = gen_crockford(nbytes=nbytes)[:nchars]
    secret = group_str(data_b32)
    print(secret)


def calculate_group_size(size, group_size_max=5):
    if size < group_size_max:
        return size

    for group_size in range(group_size_max, 0, -1):
        ngroups, other = divmod(size, group_size)
        print(size, group_size, ngroups, other)
        
for i in range(1, 128):
    calculate_group_size(i)
    
