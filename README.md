
# CODE INSTRUCTIONS

## Data

### BGP

Data can be downloaded from the BGP collectors' archives, found under the below URLs.


http://archive.routeviews.org/bgpdata/2021.09/UPDATES/

http://archive.routeviews.org/route-views4/bgpdata/2021.09/UPDATES/

http://archive.routeviews.org/route-views5/bgpdata/2021.09/UPDATES/

http://archive.routeviews.org/route-views6/bgpdata/2021.09/UPDATES/

http://archive.routeviews.org/route-views.amsix/bgpdata/2021.09/UPDATES/

https://data.ris.ripe.net/rrc00/2021.09/

https://data.ris.ripe.net/rrc01/2021.09/

https://data.ris.ripe.net/rrc04/2021.09/

https://data.ris.ripe.net/rrc05/2021.09/

https://data.ris.ripe.net/rrc06/2021.09/


```
wget --no-clobber --convert-links --random-wait -r -p --level 1 -E -e robots=off -U mozilla https://data.ris.ripe.net/rrc00/2021.09/
```

```
wget --no-clobber --convert-links --random-wait -r -p --level 1 -E -e robots=off -U mozilla http://archive.routeviews.org/route-views.amsix/bgpdata/2021.09/UPDATES/
```

## Requirements

- bgpscanner
- ipmininet from https://ipmininet.readthedocs.io/en/latest/install.html
- everything else should be in requirements.txt

## Instructions

- BGP analysis
  - automatic_attribute_extractor.py takes as input a directory (e.g., the UPDATES directory from a bgp collector), the name of the output file and a list of attributes it should ignore - creates a files where it writes all the attributes it found
  - community-checker.py takes a path (e.g., UPDATES dir from a bgp collector) and a suffix (for naming the output file) and creates a file containing the found Color Extended Communities
  - pipeline for extracting information presented in Table 1:
    - community_csv_creator.py takes a path (e.g., UPDATES dir from bgp collector) and a suffix (for naming the output) -> should be called twice: once with --suspects and the second time with --suspects --no-suspects (needs a suspect-ases.json) -> creates two csvs (the two terms for the set difference regarding suspects):
    ```
    python3 community_csv_creator.py --path path/to/rv2/month/UPDATES/ --suspects --suffix rv2 --checkpoints
    python3 community_csv_creator.py --path path/to/rv2/month/UPDATES/ --suspects --no_suspects --suffix rv2 --checkpoints
    ```
    - suspect-as-aggregator.py takes a suffix for knowing which file to process, prints how many communities appear in the set difference and how many of them appear for more than 1 AS, also creates a file enumerating this communities
    ```
    python3 suspect-as-aggregator.py --suffix rv2
    ```
    - as-path-community-tracker.py takes a path (e.g., UPDATES dir from bgp collector) and a suffix and creates a file containing the MRT entries (readable) that contain the communities appearing for more than one AS
    ```
    python3 as-path-community-tracker.py --path path/to/rv2/month/UPDATES/ --suffix rv2
    ```
    - mrt_line_searcher.py takes the input of the previous .py and counts how many appear for non-sibling ASes, prints them
    ```
    python3 mrt_line_searcher.py --suffix rv2
    ```

- traceroute emulation
  - traceroute_emulation.py starts an interactive emulation
    - command for traceroute:
    ```
    h1 traceroute -N 1 -q 1 h2
    ```

- traceroute address generation
  - address-gatherer.py takes one argument, the company name, and generates a txt in the data/ directory containing the related prefixes
  - address_generator.py can be used to generate random addresses from a prefix
  - address-generator-meta.py generates 100 addresses for each prefix found in the files in the data/ directory

- tshark: pcap exploration
  - search for SR specific ipv6 header
  ```
  tshark -n -r path.pcap -Y ipv6.routing.type==4 > output.txt
  ```
