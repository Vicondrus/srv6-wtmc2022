#!/usr/bin/env python3

import argparse
import os

import subprocess
import json

import pandas as pd

bgp_columns = {
    "type": "1",
    "subnets": "2",
    "as_path": "3",
    "next_hop": "4",
    "origin": "5",
    "atomic_aggregate": "6",
    "aggregator": "7",
    "communities": "8",
    "source": "9",
    "timestamp": "10",
    "asn_32_bit_flag": "11"
}


def dict_of_dicts_to_df(dict_of_dicts):
    df = pd.DataFrame()
    for key in dict_of_dicts:
        value = dict_of_dicts[key]
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        for inner_key in value:
            list1.append(inner_key)
            list2.append(value[inner_key]['hits'])
            list3.append(key)
            list4.append(value[inner_key]['first_byte_asn_count'])
        df = df.append(pd.DataFrame({'as': list3, 'community': list1,
                                     'hits': list2,
                                     'first_byte_asn_count': list4}))
    return df

def apply_suspect_cmd(entry, command, by):
    result = subprocess.Popen(['bgpscanner'] + command + [entry.path],
                              stdout=subprocess.PIPE)
    result = subprocess.run(['cut', '-d', '|', '-f', f"3,{bgp_columns[by]}"],
                            stdin=result.stdout,
                            stdout=subprocess.PIPE).stdout.decode('utf-8')
    return result


def apply_no_suspect_cmd(entry, sus_command, by):
    command1 = ['<(bgpscanner'] + [entry.path] + ['|', 'sort)']
    command2 = ['<(bgpscanner'] + sus_command + [entry.path] \
               + ['|', 'sort)']
    command = ' '.join(['comm', '-23'] + command1 + command2)
    command = ['bash', '-c', f"{command}"]
    result = subprocess.Popen(command,
                              stdout=subprocess.PIPE)
    result = subprocess.run(['cut', '-d', '|', '-f', f"3,{bgp_columns[by]}"],
                            stdin=result.stdout,
                            stdout=subprocess.PIPE).stdout.decode('utf-8')
    return result


def apply_cmd(entry, sus_command, by, no_suspects):
    if no_suspects:
        return apply_no_suspect_cmd(entry, sus_command, by)
    else:
        return apply_suspect_cmd(entry, sus_command, by)

def as_searcher(path, suspects=None, no_suspects=False,
                type_='UPDATES', by='communities', csv_name=None):
    aux = os.path.join(path, type_)
    path = aux if os.path.isdir(aux) else path
    parsed_files = 0
    as_dict = {}
    total_files = len([name for name in os.listdir(path)])
    sus_command = []
    if suspects:
        for s in suspects:
            sus_command.append('-p')
            sus_command.append(s)
    print(' '.join(sus_command))
    skipped = 0
    if csv_name:
        checkpoint = 1
    for entry in os.scandir(path):
        parsed_files += 1
        print(f'\rFiles parsed: {parsed_files} ('
              f'{parsed_files * 100 / total_files:.2f}%) | skipped {skipped}', end='')
        if csv_name:
            print(f' | passed checkpoints {checkpoint - 1}', end='')
        if 'updates' not in entry.path:
            skipped += 1
            continue
        result = apply_cmd(entry, sus_command, by, no_suspects)
        for cut_entry in result.split(sep='\n'):
            if cut_entry == '|' or not cut_entry:
                continue
            if bgp_columns[by] < '3':
                communities, as_path = cut_entry.split(sep='|')
            else:
                as_path, communities = cut_entry.split(sep='|')
            as_path = list(set(as_path.split()))
            # May be possible to make 'communities' a set so it is only counted once
            # per entry
            communities = communities.split()
            if suspects and not no_suspects:
                found_ases = list(set(as_path) & set(suspects))
            else:
                found_ases = as_path
            for AS in found_ases:
                if AS not in as_dict:
                    as_dict[AS] = {community: {
                        "hits": 0,
                        "first_byte_asn_count": 0
                    } for community in communities}
                comm_dict = as_dict[AS]
                for community in communities:
                    if community in comm_dict:
                        comm_dict[community]["hits"] += 1
                    else:
                        comm_dict[community] = {
                            "hits": 1,
                            "first_byte_asn_count": 0
                        }
                    if community.split(sep=':')[0] in as_path:
                        comm_dict[community]["first_byte_asn_count"] += 1
        if csv_name and parsed_files * 100 / total_files > checkpoint * 10:
            checkpoint += 1
            df = dict_of_dicts_to_df(as_dict)
            df.to_csv(csv_name)
    df = dict_of_dicts_to_df(as_dict)
    return df

def create_csv():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, required=False)
    parser.add_argument('--suspects', action='store_true')
    parser.add_argument('--no_suspects', action='store_true')
    parser.add_argument('--by', type=str, required=False)
    parser.add_argument('--checkpoints', action='store_true')
    parser.add_argument('--suffix', type=str, required=True)
    args = parser.parse_args()
    suspects = args.suspects
    if args.by:
        by = args.by
    else:
        by = 'communities'
    path = args.path
    csv_name = f"./{by}-by-ASN"
    if suspects:
        f = open('suspect-ases.json')
        suspects = [x['asn'] for x in json.load(f)['as_list']]
        print(suspects)
        csv_name = f'./{by}-by-ASN-{args.suffix}-suspects'
    if args.no_suspects:
        csv_name = f'./{by}-by-ASN-{args.suffix}-no-suspects'

    if args.checkpoints:
        df = as_searcher(path, suspects, by=by,
                         no_suspects=args.no_suspects, csv_name=csv_name)
    else:
        df = as_searcher(path, suspects, by=by,
                         no_suspects=args.no_suspects, csv_name=None)
    df.to_csv(csv_name)
    return df

if __name__ == '__main__':
    df = create_csv()
