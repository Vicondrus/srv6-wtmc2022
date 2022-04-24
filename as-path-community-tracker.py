#!/usr/bin/env python3

import argparse
import os
import subprocess

import json

import pandas as pd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, required=False)
    parser.add_argument('--suffix', type=str, required=True)
    args = parser.parse_args()
    suffix = args.suffix
    path = args.path
    f = open('suspect-ases.json')
    suspects = [x['asn'] for x in json.load(f)['as_list']]
    sus_command = []
    for s in suspects:
        sus_command.append('-p')
        sus_command.append(s)
    communities = pd.read_csv(f'communities-with-ASNs-gt2-{suffix}')
    # sus_command.append('-m')
    communities = communities['community'].tolist()
    # sus_command.append(f'{" ".join(communities)}')
    total_files = len([name for name in os.listdir(path)])
    print(' '.join(sus_command))
    parsed_files = 0
    found = 0
    for entry in os.scandir(path):
        entries = []
        parsed_files += 1
        result = subprocess.Popen(['bgpscanner'] + sus_command + [entry.path],
                              stdout=subprocess.PIPE)
        result = subprocess.run(['cut', '-d', '|', '-f', f"3,8"],
                            stdin=result.stdout,
                            stdout=subprocess.PIPE).stdout.decode('utf-8')
        print(f'\rFiles parsed: {parsed_files} ('
              f'{parsed_files * 100 / total_files:.2f}%) | found {found}', end='')
        for cut_entry in result.split(sep='\n'):
            if cut_entry == '|' or not cut_entry:
                continue
            for comm in  cut_entry.split('|')[1].split(' '):
                if comm in communities:
                    found += 1
                    entries.append(cut_entry)

        if entries:
            with open(f'{suffix}-mrt-rows-comms-and-ases', 'a+') as f:
                f.write('\n'.join(entries))
                f.write('\n')


