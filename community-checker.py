import subprocess
import os
import re
from datetime import date
import argparse

def extended_communities_prober(path, suffix=''):
    today = date.today()
    colored_asn = {}
    total_files = len([name for name in os.listdir(path)])
    parsed_files = 0
    filename = f"color-extended-communities-{suffix}-{today}.txt"
    for entry in os.scandir(path):
        parsed_files += 1
        print(f'\rFiles parsed: {parsed_files} ('
              f'{parsed_files * 100 / total_files:.2f}%)', end='')
        result = subprocess.Popen(['bgpscanner', '-t', 'EXTENDED_COMMUNITY',
                                   entry.path],
                                  stdout=subprocess.PIPE)
        result = subprocess.run(['cut', '-d', '|', '-f', '3,8'],
                                stdin=result.stdout,
                                stdout=subprocess.PIPE).stdout.decode('utf-8')
        for cut_entry in result.split(sep='\n'):
            if cut_entry == '|' or not cut_entry:
                continue
            as_path, communities = cut_entry.split(sep='|')
            # print(communities)
            for community in communities.split():
                tokens = community.split(sep=":")
                if len(tokens) < 2:
                    continue
                if '779' == tokens[0]:
                    if community not in colored_asn:
                        print(f"\r{community} found in {communities}"
                              f" with AS path {as_path}")
                        f = open(filename, "w+")
                        f.write(f"{cut_entry}\n")
                        f.close()
                    colored_asn[community] = {"communities": communities,
                                              "as_path": as_path}

    f = open(filename, "w+")
    f.write(f"\n\n\n\n\n{colored_asn}\n")
    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--suffix', type=str, required=True)
    args = parser.parse_args()
    path = args.path

    extended_communities_prober(path, suffix=args.suffix)
