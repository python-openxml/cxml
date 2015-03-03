# encoding: utf-8

"""
Integration test suite for overall cxml translator.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os

# import sys
# sys.path.insert(0, '.')

import pytest


from cxml import xml


def snippet_seq(name):
    """
    Return a tuple containing the unicode text snippets read from the snippet
    file having *name*. Snippets are delimited by a blank line.
    """
    thisdir = os.path.split(__file__)[0]
    path = os.path.join(thisdir, '%s.txt' % name)
    with open(path, 'rb') as f:
        text = f.read().decode('utf-8')
    return tuple(text.split('\n\n'))


snippets = snippet_seq('cxml2XML')


# TODO: Add tests for good error messages
#         (2, 'w:'), "Expected NAME at character position 3"
#              ..^
#         (5, 'w:rPr{w:b=8,7}'),
#                          ^ "ParseError: expected NAME"
#         (10, 'foo/(bar,baz)/boo'),
#                            ^ "ParseError: expected end of expression"
#         (12, 'foo/(bar(baz,baz),bar)'),
#                       ^ "ParseError: expected '/'"
#
# * [ ] Try out a predictive parser, or whatever LL(1) strategy with direct
#       method call for each rule.


class DescribeCxmlModule(object):

    def it_can_translate_cxml_to_XML(self, cxml_fixture):
        cxml, expected_xml = cxml_fixture
        assert xml(cxml) == expected_xml

    # fixtures -------------------------------------------------------

    @pytest.fixture(params=[
        (0,  'foobar'),
        (1,  ' w : rPr'),
        (2,  'w:rPr{ r: }'),
        (2,  'w:rPr{r:,w:}'),
        (3,  'w:rPr{a=b}'),
        (4,  'w:rPr{w:b=on}'),
        (5,  'w:rPr{w:b="8,7"}'),
        (6,  'w:rPr{r:,w:b=on}'),
        (6,  'w:rPr{w:b=on,r:}'),
        (7,  'w:rPr{w:val=-48.7, b=c}'),
        (8,  'foo/bar'),
        (9,  'foo/w:bar'),
        (10, 'foo/w:bar{w:}'),
        (11, 'foo/(bar,baz)'),
        (12, 'foo/(bar/baz,bar)'),
        (13, 'foo/(bar,bar/baz,bar)'),
        (14, 'foo/(bar/(baz,baz),bar)'),
        (15, 'foo"bar"'),
        (16, 'foo{a=b} ba r '),
        (16, 'foo{a=b}" ba r "'),
        (17, 'w:rPr{r:,w:val="8,7"}/(w:r{r:id=1}foobar,w:r{r:id=3})'),
        (18, 'c:barChart/c:ser/c:cat/c:strRef/c:strCache/(c:pt{idx=1}/c:v"ba'
             'r",c:pt{idx=0}/c:v"foo",c:pt{idx=2}/c:v"baz")'),
        (19, 'wp:inline/(wp:extent{cx=333,cy=666},a:graphic/a:graphicData/pi'
             'c:pic/pic:spPr/a:xfrm/a:ext{cx=333,cy=666})'),
    ])
    def cxml_fixture(self, request):
        snippet_idx, cxml = request.param
        return cxml, '%s\n' % snippets[snippet_idx].strip()
