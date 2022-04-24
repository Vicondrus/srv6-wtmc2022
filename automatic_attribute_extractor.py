#!/usr/bin/env python3

import argparse
import os
from datetime import datetime

import mrtparse


def extract_attributes_from_folder(folder_path, exclude_list, output_file_name=None):
    total_files = len([name for name in os.listdir(folder_path)])
    parsed_files = 0
    found_attr_dict = {}
    ignored = 0
    if output_file_name is None:
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H%M%S")
        output_file_name = f'attributes_found_{dt_string}.txt'
    for file in os.scandir(folder_path):
        parsed_files += 1
        print(f'\rFiles parsed: {parsed_files} ('
              f'{parsed_files * 100 / total_files:.2f}%) - {len(found_attr_dict)} '
              f'attributes found - ignored {ignored} files', end='')
        try:
            for entry in mrtparse.Reader(file.path):
                if 'bgp_message' in entry.data:
                    try:
                        for attribute in entry.data['bgp_message']['path_attributes']:
                            x = attribute['type']
                            if x[1] in exclude_list:
                                continue
                            found_attr_dict[x[1]] = x
                            if x[1] == 'ATTR_SET':
                                for attr in attribute['value']['path_attributes']:
                                    y = attr['type']
                                    if y[1] in exclude_list:
                                        continue
                                    found_attr_dict[y[1]] = y
                    except Exception:
                        pass
                elif 'rib_entries' in entry.data:
                    try:
                        for rib_entry in entry.data['rib_entries']:
                            for attribute in rib_entry['path_attributes']:
                                x = attribute['type']
                                if x[1] in exclude_list:
                                    continue
                                found_attr_dict[x[1]] = x
                                if x[1] == 'ATTR_SET':
                                    for attr in attribute['value']['path_attributes']:
                                        y = attr['type']
                                        if y[1] in exclude_list:
                                            continue
                                        found_attr_dict[y[1]] = y
                    except Exception:
                        pass

        except Exception:
            ignored += 1

        with open(output_file_name, 'w') as f:
            f.write(str(found_attr_dict))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--directory', '-d', type=str, required=True, help='Directory '
                                                                           'to parse')
    parser.add_argument('--output', '-o', type=str, help='Output file name')
    parser.add_argument('--exclude', '-e', nargs="+", default=[], help='Attributes to '
                                                                       'exclude')

    args = parser.parse_args()
    extract_attributes_from_folder(args.directory, args.exclude, args.output)
