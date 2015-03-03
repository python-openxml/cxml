# encoding: utf-8

"""
Test suite for cxml parser module.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import sys
sys.path.insert(0, '.')

import pytest

from cxml.lexer import CxmlLexer
from cxml.parser import CxmlParser
from cxml.symbols import (
    COLON, COMMA, SNTL, EQUAL, LBRACE, LPAREN, NAME, RBRACE, RPAREN, SLASH,
    TEXT, attr, attr_list, attrs, element, nsdecl, qname, root, root_element,
    str_attr, tree, tree_list, trees
)


class DescribeParser(object):

    def it_can_parse_an_nsdecl(self, nsdecl_fixture):
        input_, root_symbol, expected_values = nsdecl_fixture
        ast = parse(input_, nsdecl)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_a_qname(self, qname_fixture):
        input_, root_symbol, expected_values = qname_fixture
        ast = parse(input_, qname)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_a_string_attribute(self, str_attr_fixture):
        input_, root_symbol, expected_values = str_attr_fixture
        ast = parse(input_, str_attr)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_an_attr(self, attr_fixture):
        input_, root_symbol, expected_values = attr_fixture
        ast = parse(input_, attr)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_an_attr_list(self, attr_list_fixture):
        input_, root_symbol, expected_values = attr_list_fixture
        ast = parse(input_, attr_list)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_an_attrs(self, attrs_fixture):
        input_, root_symbol, expected_values = attrs_fixture
        ast = parse(input_, attrs)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_an_element(self, element_fixture):
        input_, root_symbol, expected_values = element_fixture
        ast = parse(input_, element)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_a_tree(self, tree_fixture):
        input_, root_symbol, expected_values = tree_fixture
        ast = parse(input_, tree)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_a_tree_list(self, tree_list_fixture):
        input_, root_symbol, expected_values = tree_list_fixture
        ast = parse(input_, tree_list)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_a_trees(self, trees_fixture):
        input_, root_symbol, expected_values = trees_fixture
        ast = parse(input_, trees)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_a_root_element(self, root_element_fixture):
        input_, root_symbol, expected_values = root_element_fixture
        ast = parse(input_, root_element)
        assert shallow_eq(ast, root_symbol, expected_values)

    def it_can_parse_a_root(self, root_fixture):
        input_, root_symbol, expected_values = root_fixture
        ast = parse(input_, root, emit_sntl=True)
        assert shallow_eq(ast, root_symbol, expected_values)

    # fixtures -------------------------------------------------------

    @pytest.fixture(params=[
        ('w:',    attr, [(nsdecl, 'w:')]),
        ('w:b=1', attr, [(str_attr, 'w:b=1')]),
    ])
    def attr_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('w:b=1',    attr_list, [(attr, 'w:b=1')]),
        ('r:,w:b=1', attr_list, [
            (attr, 'r:'), (COMMA, ','), (attr_list, 'w:b=1')
        ]),
        ('r:,w:b=1,w:i=0', attr_list, [
            (attr, 'r:'), (COMMA, ','), (attr_list, 'w:b=1,w:i=0')
        ]),
    ])
    def attr_list_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('{w:}', attrs, [(LBRACE, '{'), (attr_list, 'w:'), (RBRACE, '}')]),
        ('{w:b=1,r:,w:i=0}', attrs, [
            (LBRACE, '{'), (attr_list, 'w:b=1,r:,w:i=0'), (RBRACE, '}')
        ]),
    ])
    def attrs_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('w:t',           element, [(qname, 'w:t')]),
        ('w:t"foo"',      element, [(qname, 'w:t'), (TEXT, 'foo')]),
        ('w:t{b=1}',      element, [(qname, 'w:t'), (attrs, '{b=1}')]),
        ('w:t{b=1}"foo"', element, [
            (qname, 'w:t'), (attrs, '{b=1}'), (TEXT, 'foo')
        ]),
    ])
    def element_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('w:', nsdecl, [(NAME, 'w'), (COLON, ':')]),
    ])
    def nsdecl_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('foobar', qname, [(NAME, 'foobar')]),
        ('w:rPr',  qname, [(NAME, 'w'), (COLON, ':'), (NAME, 'rPr')]),
    ])
    def qname_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('w:b=1', str_attr, [(qname, 'w:b'), (EQUAL, '='), (TEXT, '1')]),
    ])
    def str_attr_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('elm',     tree, [(element, 'elm')]),
        ('foo/bar', tree, [(element, 'foo'), (SLASH, '/'), (trees, 'bar')]),
    ])
    def tree_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('foo',     tree_list, [(tree, 'foo')]),
        ('foo,bar', tree_list, [
            (tree, 'foo'), (COMMA, ','), (tree_list, 'bar')
        ]),
    ])
    def tree_list_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('foo',       trees, [(tree, 'foo')]),
        ('(foo,bar)', trees, [
            (LPAREN, '('), (tree_list, 'foo,bar'), (RPAREN, ')')
        ]),
    ])
    def trees_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('w:rPr',       root_element, [(qname, 'w:rPr')]),
        ('w:t"foo"',    root_element, [(qname, 'w:t'), (TEXT, 'foo')]),
        ('w:t{a=b}',    root_element, [(qname, 'w:t'), (attrs, '{a=b}')]),
        ('w:t{a=b}bar', root_element, [
            (qname, 'w:t'), (attrs, '{a=b}'), (TEXT, 'bar')
        ]),
    ])
    def root_element_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values

    @pytest.fixture(params=[
        ('w:r',             root, [(root_element, 'w:r'), (SNTL, '')]),
        ('w:r/(w:rPr,w:t)', root, [
            (root_element, 'w:r'), (SLASH, '/'), (trees, '(w:rPr,w:t)'),
            (SNTL, '')
        ]),
    ])
    def root_fixture(self, request):
        input_, root_symbol, expected_values = request.param
        return input_, root_symbol, expected_values


def parse(string, start_symbol, emit_sntl=False):
    """
    Return the |ASTNode| object produced by parsing *string* with CxmlParser.
    """
    lexer = CxmlLexer(string, emit_sntl=emit_sntl)
    parser = CxmlParser(lexer)
    return parser.parse(start_symbol)


def shallow_eq(ast, root_symbol, values):
    """
    Return |True| if the root node in *ast* has *root_symbol* as its symbol
    and *values* matches its child nodes.
    """
    if ast.symbol is not root_symbol:
        print('root symbol %s != %s' % (ast.symbol, root_symbol))
        return False

    if len(ast.child_nodes) != len(values):
        print('child count: %d != %d' % (len(ast.child_nodes), len(values)))
        return False

    for idx, (symbol, value) in enumerate(values):
        child = ast.child_nodes[idx]
        if child.symbol != symbol:
            print('child symbol %s != %s' % (child.symbol, symbol))
            return False
        if child.value != value:
            print('child value %s != %s' % (child.value, value))
            return False
    return True
