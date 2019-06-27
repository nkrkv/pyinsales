#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import urllib.request, re, pprint
from itertools import tee


def parse(lines):
    re_opening = re.compile(".*&lt;([\\w\\d_\\-]+).*")
    first, second = tee(lines)
    plural = None
    result = {"nil-classes": "nil-class"}
    for line in first:
        # parent with children
        if plural == None and line.find("type=&quot;array&quot;&gt;") >= 0:
            match = re_opening.match(line)
            if match:
                plural = match.group(1)
                continue
        # children
        if plural:
            match = re_opening.match(line)
            if match:
                result[plural] = match.group(1)
                plural = None

    for line in second:
        # lone parent
        if line.find("type=&quot;array&quot;/&gt;") >= 0:
            match = re_opening.match(line)
            if match:
                plural = match.group(1)
                if plural not in result.keys():
                    result[plural] = plural[:-1]

    for broken in ["objects", "payment-method"]:
        result.pop(broken, None)

    return result


def main():
    with urllib.request.urlopen("https://api.insales.ru/") as f:
        lines = map(lambda x: x.decode("utf-8"), f.readlines())
        arrs = parse(lines)
        pprint.PrettyPrinter(indent=8, width=80).pprint(arrs)


if __name__ == "__main__":
    main()
