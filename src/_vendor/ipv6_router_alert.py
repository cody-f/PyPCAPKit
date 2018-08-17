# -*- coding: utf-8 -*-


import csv
import os
import re

import requests


ROOT = os.path.dirname(os.path.abspath(__file__))

page = requests.get('https://www.iana.org/assignments/ipv6-routeralert-values/ipv6-routeralert-values-1.csv')
data = page.text.strip().split('\r\n')

reader = csv.reader(data)
header = next(reader)

def rename(name, code):
    if re.match(r'Reserved|Unassigned|Deprecated|Experimental', name, re.IGNORECASE):
        name = f'{name} [{code}]'
    return name

lidb = list()
for item in reader:
    name = item[1]
    rfcs = item[2]

    temp = list()
    for rfc in filter(None, re.split(r'\[|\]', rfcs)):
        if 'RFC' in rfc:
            temp.append(f'[{rfc[:3]} {rfc[3:]}]')
        else:
            temp.append(f'[{rfc}]')
    desc = f"# {''.join(temp)}" if rfcs else ''

    try:
        code = int(item[0])
        renm = rename(name, code)
        lidb.append(f"{code:>5} : '{renm}',".ljust(80) + desc)
        # print(code, name, ''.join(temp))
    except ValueError:
        start, stop = map(int, item[0].split('-'))
        for code in range(start, stop+1):
            renm = rename(name, code).rstrip('s 0-31')
            if 'Level' in renm:
                lidb.append(f"{code:>5} : '{renm} {code - start}',".ljust(80) + desc)
            else:
                lidb.append(f"{code:>5} : '{renm}',".ljust(80) + desc)
            # print(code, name, ''.join(temp))

with open(os.path.join(ROOT, '../_common/ipv6_router_alert.py'), 'w') as file:
    file.write('# -*- coding: utf-8 -*-\n\n\n')
    file.write('# IPv6 Router Alert Option Values\n')
    file.write('_ROUTER_ALERT = {\n')
    file.write('\n'.join(map(lambda s: s.rstrip(), lidb)))
    file.write('\n}\n')