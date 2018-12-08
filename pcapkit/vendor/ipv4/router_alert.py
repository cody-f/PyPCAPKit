# -*- coding: utf-8 -*-

import collections
import contextlib
import csv
import os
import re

import requests

###############
# Macros
###############

NAME = 'RouterAlert'
DOCS = 'IPv4 Router Alert Option Values'
FLAG = 'isinstance(value, int) and 0 <= value <= 65535'
LINK = 'https://www.iana.org/assignments/ip-parameters/ipv4-router-alert-option-values.csv'

###############
# Processors
###############

page = requests.get(LINK)
data = page.text.strip().split('\r\n')

reader = csv.reader(data)
header = next(reader)
record = collections.Counter(map(lambda item: item[1],
                                 filter(lambda item: len(item[0].split('-')) != 2, reader)))


def rename(name, code):
    if record[name] > 1:
        return '{} [{}]'.format(name, code)
    return name


reader = csv.reader(data)
header = next(reader)

enum = list()
miss = list()
for item in reader:
    name = item[1]
    rfcs = item[2]

    temp = list()
    for rfc in filter(None, re.split(r'\[|\]', rfcs)):
        if 'RFC' in rfc:
            temp.append('[{} {}]'.format(rfc[:3], rfc[3:]))
        else:
            temp.append('[{}]'.format(rfc))
    desc = "# {}".format(''.join(temp)) if rfcs else ''

    try:
        code, _ = item[0], int(item[0])
        renm = rename(name, code)

        pres = "{}[{!r}] = {}".format(NAME, renm, code).ljust(76)
        sufs = re.sub(r'\r*\n', ' ', desc, re.MULTILINE)

        enum.append('{}{}'.format(pres, sufs))
    except ValueError:
        start, stop = map(int, item[0].split('-'))
        more = re.sub(r'\r*\n', ' ', desc, re.MULTILINE)

        if 'Level' in name:
            base = name.rstrip('s 0-31')
            for code in range(start, stop+1):
                renm = '{} {}'.format(base, code-start)
                pres = "{}[{!r}] = {}".format(NAME, renm, code).ljust(76)

                enum.append('{}{}'.format(pres, more))
        else:
            miss.append('if {} <= value <= {}:'.format(start, stop))
            if more:
                miss.append('    {}'.format(more))
            miss.append("    extend_enum(cls, '{} [%d]' % value, value)".format(name))
            miss.append('    return cls(value)')

###############
# Defaults
###############

temp, FILE = os.path.split(os.path.abspath(__file__))
ROOT, STEM = os.path.split(temp)

ENUM = '\n    '.join(map(lambda s: s.rstrip(), enum))
MISS = '\n        '.join(map(lambda s: s.rstrip(), miss))


def LINE(NAME, DOCS, FLAG, ENUM, MISS): return '''\
# -*- coding: utf-8 -*-

from aenum import IntEnum, extend_enum


class {}(IntEnum):
    """Enumeration class for {}."""
    _ignore_ = '{} _'
    {} = vars()

    # {}
    {}

    @staticmethod
    def get(key, default=-1):
        """Backport support for original codes."""
        if isinstance(key, int):
            return {}(key)
        if key not in {}._member_map_:
            extend_enum({}, key, default)
        return {}[key]

    @classmethod
    def _missing_(cls, value):
        """Lookup function used when value is not found."""
        if not ({}):
            raise ValueError('%r is not a valid %s' % (value, cls.__name__))
        {}
        super()._missing_(value)
'''.format(NAME, NAME, NAME, NAME, DOCS, ENUM, NAME, NAME, NAME, NAME, FLAG, MISS)


with contextlib.suppress(FileExistsError):
    os.mkdir(os.path.join(ROOT, '../const/{}'.format(STEM)))
with open(os.path.join(ROOT, '../const/{}/{}'.format(STEM, FILE)), 'w') as file:
    file.write(LINE(NAME, DOCS, FLAG, ENUM, MISS))