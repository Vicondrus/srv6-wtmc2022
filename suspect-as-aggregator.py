#!/usr/bin/env python3

import argparse
from collections import Counter

import pandas as pd


def count_by_community(suffix):
    # df_full = pd.read_csv("./communities-by-ASN")
    df = pd.read_csv(f"./communities-by-ASN-{suffix}-no-suspects")
    df_sus = pd.read_csv(f"./communities-by-ASN-{suffix}-suspects")
    counts = df.groupby(['community']).agg({'as': ['nunique'],
                                            'hits': ['sum', 'mean']}). \
        sort_values(by=[('as', 'nunique'), ('hits', 'mean')], ascending=False)
    counts_sus = df_sus.groupby(['community']).agg({'as': ['nunique'],
                                                    'hits': ['sum', 'mean']}). \
        sort_values(by=[('as', 'nunique'), ('hits', 'mean')], ascending=False)

    x = pd.merge(counts, counts_sus, left_index=True, right_index=True,
                 how='outer', suffixes=('_rv_nonsus', '_rv_sus'))

    x = x.fillna(0)
    x = x[[('as_rv_nonsus', 'nunique'), ('as_rv_sus', 'nunique')]]. \
        sort_values(by=[('as_rv_sus', 'nunique')], ascending=False)
    zero = x[(x[('as_rv_nonsus', 'nunique')] == 0)].sort_values(
        by=[('as_rv_sus', 'nunique'), ('as_rv_sus', 'nunique')],
        ascending=False)
    return x, zero


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--suffix', type=str, required=True)
    suffix = parser.parse_args().suffix
    x, zero = count_by_community(suffix)
    freq = Counter([community.split(':')[0] for community in
                    zero.index.values])
    popularity = sorted(freq,
                        key=lambda item: -freq[item])

    greater_than_two = zero[zero[('as_rv_sus', 'nunique')] > 1.0]
    print(zero.shape[0], greater_than_two.shape[0])
    x = greater_than_two.reset_index()[['community']]
    x.to_csv(f'communities-with-ASNs-gt2-{suffix}')

    # Non location communities
    # rv2 = 159
    # rv6 = 57
    # rv-amsix = 140
    # rrc00 = 203
    # rrc04 = 101
    # rrc05 = 122
    # rrc06 = 50


