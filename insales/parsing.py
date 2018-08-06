# -*- coding: utf-8; -*-

from decimal import Decimal
from collections import deque
from copy import copy
from io import BytesIO

import xml.sax
import xml.sax.handler

import datetime
import re
import iso8601


def format_open_tag(name, attrs):
    attrs = [u'%s="%s"' % attr for attr in attrs.items()]
    return u"<%s %s>" % (name, ' '.join(attrs))


class ElementHandler(object):
    __slots__ = ('value', )

    def __init__(self):
        self.value = copy(self.default)

    def on_nested_start(self, name, attrs):
        raise NotImplementedError(
            "Elements with type=%s are not expected to have nested elements" % self.type_name)

    def on_nested_end(self, name, handler):
        pass

    def on_content(self, content):
        if not content.strip():
            return
        raise NotImplementedError(
            "Elements with type=%s are not expected to have a content" % self.type_name)


class NoTypeHandler(ElementHandler):
    __slots__ = ('_string_parts', '_dict')

    type_name = None
    default = None

    wspace_re = re.compile('\s+')

    def __init__(self):
        self._string_parts = []
        self._dict = {}

    def on_nested_start(self, name, attrs):
        if self._string_parts:
            self._string_parts.append(format_open_tag(name, attrs))
            return MixedContentHandler()
        return handler_for(attrs)

    def on_nested_end(self, name, handler):
        if self._string_parts:
            self._string_parts.append(handler.value)
            self._string_parts.append("</%s>" % name)
            return
        self._dict[name] = handler.value

    def on_content(self, content):
        if self._dict:
            # Hack: drop content if we're already got nested
            # elements. This could lead to a bug, but since
            # InSales doesn't enclose nested HTML with CDATA
            # there is no easy way to recover string data as-is
            # in such case
            return
        if not self._string_parts and not content.strip():
            # skip insignificant leading whitespace
            return
        self._string_parts.append(content)

    @property
    def value(self):
        if self._dict:
            return self._dict
        if self._string_parts:
            val = u''.join(self._string_parts)
            val = self.wspace_re.sub(u' ', val)
            val = val.strip()
            return val
        return self.default


class MixedContentHandler(ElementHandler):
    default = ''

    def on_nested_start(self, name, attrs):
        self.value += format_open_tag(name, attrs)
        return MixedContentHandler()

    def on_nested_end(self, name, handler):
        self.value += handler.value
        self.value += "</%s>" % name

    def on_content(self, content):
        content = content.strip()
        self.value += content


class NilHandler(ElementHandler):
    default = None

    def on_nested_start(self, name, attrs):
        raise NotImplementedError(
            "Elements with nil=true are not expected to have nested elements")

    def on_nested_end(self, name, handler):
        pass

    def on_content(self, content):
        if not content.strip():
            return
        raise NotImplementedError(
            "Elements with nil=true are not expected to have a content")


class ArrayHandler(ElementHandler):
    type_name = 'array'
    default = []

    def on_nested_start(self, name, attrs):
        return handler_for(attrs)

    def on_nested_end(self, name, handler):
        self.value.append(handler.value)


class IntegerHandler(ElementHandler):
    type_name = 'integer'
    default = 0

    def on_content(self, content):
        self.value = int(content.strip())


class DecimalHandler(ElementHandler):
    type_name = 'decimal'
    default = Decimal(0)

    def on_content(self, content):
        self.value = Decimal(content.strip())


class BooleanHandler(ElementHandler):
    type_name = 'boolean'
    default = False

    def on_content(self, content):
        self.value = (content.strip() == 'true')


class DateHandler(ElementHandler):
    type_name = 'date'
    default = None

    def on_content(self, content):
        self.value = datetime.datetime.strptime(content.strip(), "%Y-%m-%d")


class TimestampHandler(ElementHandler):
    type_name = 'timestamp'
    default = None
    date_re = re.compile(r"\s+\+(\d\d)(\d\d)$")

    def on_content(self, content):
        # convert 2010-08-16 18:39:58 +0400
        # to      2010-08-16 18:39:58+04:00
        string = self.date_re.sub(r"+\1:\2", content.strip())
        self.value = iso8601.parse_date(string)

class DateTimeHandler(ElementHandler):
    type_name = 'dateTime'
    default = None

    def on_content(self, content):
        self.value = iso8601.parse_date(content.strip())


all_handlers = [
    NoTypeHandler,
    ArrayHandler,
    IntegerHandler,
    DecimalHandler,
    BooleanHandler,
    DateHandler,
    DateTimeHandler,
    TimestampHandler,
]

type2handler = dict((h.type_name, h) for h in all_handlers)

def handler_for(attrs):
    nil = (attrs.get('nil') == 'true')
    if nil:
        return NilHandler()
    type_name = attrs.get('type')
    return type2handler.get(type_name, NoTypeHandler)()


class XmlProcessor(xml.sax.handler.ContentHandler):
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._handler_stack = deque([NoTypeHandler()])

    def startElement(self, name, attrs):
        head = self._handler_stack[-1]
        new_head = head.on_nested_start(name, attrs)
        self._handler_stack.append(new_head)

    def endElement(self, name):
        h = self._handler_stack.pop()
        self._handler_stack[-1].on_nested_end(name, h)

    def characters(self, content):
        self._handler_stack[-1].on_content(content)

    def data(self):
        top_dict = self._handler_stack[0].value
        if top_dict:
            return list(top_dict.values())[0]


def parse(xml_string):
    processor = XmlProcessor()
    io = BytesIO(xml_string)

    parser = xml.sax.make_parser()
    parser.setContentHandler(processor)
    for line in io:
        parser.feed(line)

    return processor.data()
