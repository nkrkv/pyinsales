# -*- coding: utf-8; -*-

import datetime
import collections
import xml.etree.ElementTree as et

from decimal import Decimal

def compose(data, root, arrays={}):
    root_e = compose_element(root, data, arrays)
    return et.tostring(root_e, 'utf-8')

def compose_element(key, value, arrays={}):
    e = et.Element(key)
    if isinstance(value, basestring):
        e.text = value
    elif isinstance(value, (int, long)):
        e.attrib['type'] = 'integer'
        e.text = str(value)
    elif isinstance(value, Decimal):
        e.attrib['type'] = 'decimal'
        e.text = str(value)
    elif isinstance(value, datetime.datetime):
        e.attrib['type'] = 'timestamp'
        e.text = value.strftime("%Y-%m-%d %H:%M:%S %z")
    elif value is None:
        e.attrib['nil'] = 'true'
    elif isinstance(value, collections.Sequence):
        e.attrib['type'] = 'array'
        e_key = arrays[key]
        for x in value:
            e.append(compose_element(e_key, x, arrays))
    elif isinstance(value, collections.Mapping):
        for key, value in value.iteritems():
            e.append(compose_element(key, value, arrays))
    else:
        raise TypeError("Value %r has unsupported type %s" % (value, type(value)))
    return e
