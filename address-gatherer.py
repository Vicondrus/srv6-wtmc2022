#!/usr/bin/env python3

import argparse
import os
import subprocess
import json
import requests
import pyasn


def get_ases_of_company(company):
    url = "https://www.peeringdb.com/api/org?name__contains=" + company
    resp = requests.get(url=url)
    pdb_json = json.loads(resp.text)
    ids = set([x["id"] for x in pdb_json["data"]])
    asns = []
    for id in ids:
        url = "https://www.peeringdb.com/api/net?org_id=" + str(id)
        resp = requests.get(url=url)
        pdb_json = json.loads(resp.text)
        asns.extend([x["asn"] for x in pdb_json["data"]])

    url = 'https://api.bgpview.io/search?query_term=' + company
    resp = requests.get(url=url)
    pdb_json = json.loads(resp.text)
    asns = list(set(asns + list(set([x["asn"] for x in pdb_json["data"]["asns"]]))))
    return asns


def get_ipv6_nets_for_as(asn, method="pyasn"):
    if method == "pyasn":
        asndb = pyasn.pyasn("ISPAN.DAT")
        prefixes = asndb.get_as_prefixes(asn)
        if prefixes is None:
            return set()
        return set(prefixes)
    elif method == "whois":
        whois_cmd = f"whois -h whois.radb.net '!6as{asn}'"
        whois_output = subprocess.check_output(whois_cmd, shell=True).decode(
            "utf-8").split("\n")[1]
        return set(whois_output.split(" "))
    else:
        raise ValueError("Unknown method")


def get_ipv6_nets_for_organization(company, method="pyasn"):
    asns = get_ases_of_company(company)
    # print([(x, get_ipv6_nets_for_as(x, method)) for x in asns])
    ips = set.union(*[get_ipv6_nets_for_as(x, method) for x in asns]).difference({''})
    if not os.path.exists("./data"):
        os.makedirs("./data")
    with open(f"data/ipv6_addresses_{company.replace(' ', '_')}_{method}.txt",
              "w+") as f:
        for ip in ips:
            f.write(ip + "\n")
    print(f"Found {len(ips)} IPv6 nets")
    return ips


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--company", required=True, help="Company name")
    ap.add_argument("-m", "--method", required=False, default="pyasn", help="Method to use")
    args = vars(ap.parse_args())
    asndb = pyasn.pyasn("ISPAN.DAT")
    # print(get_ipv6_nets_for_as(29447))
    get_ipv6_nets_for_organization(args["company"], args["method"])

