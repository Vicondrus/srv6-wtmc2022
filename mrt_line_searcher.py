#!/usr/bin/env python3

import argparse
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', type=str, required=True)
    suffix = parser.parse_args().suffix
    f = open('suspect-ases.json')
    suspects = {x['asn']: x['company_name'] for x in json.load(f)['as_list']}
    path = f'./{suffix}-mrt-rows-comms-and-ases'
    with open(path, 'r') as f:
        lines = f.readlines()
    li = []
    for line in lines:
        hits = 0
        pool = []
        for x in line.split('|')[0].split(' '):
            if x in suspects:
                if suspects[x] not in pool:
                    pool.append(suspects[x])
                    hits += 1
        if hits == 0:
            print('WTF')
        elif hits > 1:
            print(line)
            li.append(line)

    print(f'{len(li)} hits')

