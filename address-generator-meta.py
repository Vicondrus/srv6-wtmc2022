#!/usr/bin/env python3

import os

import pandas as pd
from tqdm import tqdm

from address_generator import get_addresses

if __name__ == '__main__':
    result_file = open('addresses.csv', 'a')
    result_file.write('prefix,ip\n')

    for file_name in tqdm(os.listdir('data')):
        with open('data/' + file_name, 'r') as f:
            for line in tqdm(f, leave=False):
                line = line.strip()
                if line:
                    addresses = get_addresses(100, line, type='ipv6')
                    df = pd.DataFrame(list(zip([line for i in range(100)], addresses)),
                                      columns=['prefix', 'ip'])
                    df.to_csv(result_file, index=False, header=False)

    result_file.close()


