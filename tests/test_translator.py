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

from cxml.lib.lexer import Token
from cxml.lib.parser import ASTNode
from cxml.model import Element, RootElement
from cxml.symbols import (
    COLON, EQUAL, NAME, SNTL, TEXT, attr, attr_list, attrs, element, nsdecl,
    qname, root_element, str_attr, tree, tree_list, trees
)
from cxml.translator import CxmlTranslator

from .mocklib import call, class_mock, instance_mock, method_mock


class DescribeCxmlTranslator(object):

    def it_constructs_a_namespace_declaration(self, nsdecl_fixture):
        cxml_translator, node, nspfx = nsdecl_fixture[:3]
        NamespaceDeclaration_ = nsdecl_fixture[3]

        namespace_declaration = cxml_translator.nsdecl(node)

        NamespaceDeclaration_.assert_called_once_with(nspfx)
        assert namespace_declaration is NamespaceDeclaration_.return_value

    def it_combines_a_qname(self, qname_fixture):
        cxml_translator, node, expected_value = qname_fixture
        qname_val = cxml_translator.qname(node)
        assert qname_val == expected_value

    def it_constructs_a_string_attribute(self, str_attr_fixture):
        cxml_translator, node, StringAttribute_ = str_attr_fixture[:3]
        qname, value = str_attr_fixture[3:]

        string_attribute = cxml_translator.str_attr(node)

        StringAttribute_.new.assert_called_once_with(qname, value)
        assert string_attribute is StringAttribute_.new.return_value

    def it_disambiguates_an_attr_node(self, attr_fixture):
        cxml_translator, node = attr_fixture

        attr_val = cxml_translator.attr(node)

        cxml_translator.evaluate.assert_called_once_with(node.child_nodes[0])
        assert attr_val is cxml_translator.evaluate.return_value

    def it_joins_an_attribute_list(self, attr_list_fixture):
        cxml_translator, node, expected_value = attr_list_fixture
        _attrs = cxml_translator.attr_list(node)
        assert _attrs == expected_value

    def it_delegates_an_attrs_node(self, attrs_fixture):
        cxml_translator, node = attrs_fixture

        attrs_val = cxml_translator.attrs(node)

        cxml_translator.evaluate.assert_called_once_with(node.child_nodes[1])
        assert attrs_val is cxml_translator.evaluate.return_value

    def it_constructs_an_element(self, element_fixture):
        cxml_translator, node, Element_ = element_fixture[:3]
        qname_val, attrs_val, text = element_fixture[3:]

        _element = cxml_translator.element(node)

        Element_.new.assert_called_once_with(qname_val, attrs_val, text)
        assert _element is Element_.new.return_value

    def it_assembles_a_tree(self, tree_fixture):
        cxml_translator, node, element_ = tree_fixture[:3]
        add_calls, expected_value = tree_fixture[3:]

        value = cxml_translator.tree(node)

        assert element_.add_child.call_args_list == add_calls
        assert value == expected_value

    def it_joins_a_tree_list(self, tree_list_fixture):
        cxml_translator, node, expected_value = tree_list_fixture
        _trees = cxml_translator.tree_list(node)
        assert _trees == expected_value

    def it_dispatches_a_trees_node(self, trees_fixture):
        cxml_translator, node, child_node_idx, expected_value = trees_fixture

        trees_val = cxml_translator.trees(node)

        cxml_translator.evaluate.assert_called_once_with(
            node.child_nodes[child_node_idx]
        )
        assert trees_val == expected_value

    def it_constructs_a_root_element(self, root_element_fixture):
        cxml_translator, node, RootElement_ = root_element_fixture[:3]
        qname_val, attrs_val, text = root_element_fixture[3:]

        _root_element = cxml_translator.root_element(node)

        RootElement_.new.assert_called_once_with(qname_val, attrs_val, text)
        assert _root_element is RootElement_.new.return_value

    def it_assembles_a_root_tree(self, root_fixture):
        cxml_translator, node, root_element_ = root_fixture[:3]
        add_calls, expected_value = root_fixture[3:]

        value = cxml_translator.root(node)

        assert root_element_.add_child.call_args_list == add_calls
        assert value == expected_value

    # fixtures -------------------------------------------------------

    @pytest.fixture
    def attr_fixture(self, evaluate_):
        cxml_translator = CxmlTranslator()
        node = ASTNode(attr, ['child_node'])
        return cxml_translator, node

    @pytest.fixture(params=[
        (('w:b=1',),              ('w:b=1',),           ['w:b=1']),
        (('w:b=1', ',', 'w:i=0'), ('w:b=1', ['w:i=0']), ['w:b=1', 'w:i=0']),
    ])
    def attr_list_fixture(self, request, evaluate_):
        child_nodes, evaluate_return_values, expected_value = request.param
        cxml_translator = CxmlTranslator()
        node = ASTNode(attr_list, child_nodes)
        evaluate_.side_effect = evaluate_return_values
        return cxml_translator, node, expected_value

    @pytest.fixture
    def attrs_fixture(self, evaluate_):
        cxml_translator = CxmlTranslator()
        node = ASTNode(attr, ['{', 'attr_list', '}'])
        return cxml_translator, node

    @pytest.fixture(params=[
        ([ASTNode(qname, ())], ['w:rPr'], ('w:rPr', [], '')),
        ([ASTNode(qname, ()), Token(TEXT, 'foo')],
         ['w:rPr'], ('w:rPr', [], 'foo')),
        ([ASTNode(qname, ()), ASTNode(attrs, ())],
         ['w:rPr', ['b=1']], ('w:rPr', ['b=1'], '')),
        ([ASTNode(qname, ()), ASTNode(attrs, ()), Token(TEXT, 'foo')],
         ['w:rPr', ['b=1']], ('w:rPr', ['b=1'], 'foo')),
    ])
    def element_fixture(self, request, Element_, evaluate_):
        child_nodes, evaluate_return_values, call_values = request.param
        cxml_translator = CxmlTranslator()
        node = ASTNode(element, child_nodes)
        evaluate_.side_effect = evaluate_return_values
        qname_val, attrs_val, text = call_values
        return cxml_translator, node, Element_, qname_val, attrs_val, text

    @pytest.fixture
    def nsdecl_fixture(self, NamespaceDeclaration_):
        cxml_translator = CxmlTranslator()
        nspfx = 'wp'
        child_nodes = (Token(NAME, nspfx), Token(COLON, ':'))
        node = ASTNode(nsdecl, child_nodes)
        return cxml_translator, node, nspfx, NamespaceDeclaration_

    @pytest.fixture(params=[
        ('addr',  (Token(NAME, 'addr'),)),
        ('w:rPr', (Token(NAME, 'w'), Token(COLON, ':'), Token(NAME, 'rPr'))),
    ])
    def qname_fixture(self, request):
        expected_value, child_nodes = request.param
        cxml_translator = CxmlTranslator()
        node = ASTNode(qname, child_nodes)
        return cxml_translator, node, expected_value

    @pytest.fixture(params=[
        ([ASTNode(root_element, ()), Token(SNTL, '')],
         ()),
        ([ASTNode(element, ()), None, ASTNode(trees, ()), Token(SNTL, '')],
         ('tree', 'tree_2')),
    ])
    def root_fixture(self, request, evaluate_, root_element_):
        child_nodes, trees = request.param
        trees_val = [(t, None) for t in trees]

        cxml_translator = CxmlTranslator()
        node = ASTNode(tree, child_nodes)
        expected_value = root_element_

        evaluate_.side_effect = [root_element_, trees_val]
        add_calls = [call(t) for t in trees]

        return (
            cxml_translator, node, root_element_, add_calls, expected_value
        )

    @pytest.fixture(params=[
        ([ASTNode(qname, ())], ['w:rPr'], ('w:rPr', [], '')),
        ([ASTNode(qname, ()), Token(TEXT, 'foo')],
         ['w:rPr'], ('w:rPr', [], 'foo')),
        ([ASTNode(qname, ()), ASTNode(attrs, ())],
         ['w:rPr', ['b=1']], ('w:rPr', ['b=1'], '')),
        ([ASTNode(qname, ()), ASTNode(attrs, ()), Token(TEXT, 'foo')],
         ['w:rPr', ['b=1']], ('w:rPr', ['b=1'], 'foo')),
    ])
    def root_element_fixture(self, request, RootElement_, evaluate_):
        child_nodes, evaluate_return_values, call_values = request.param
        cxml_translator = CxmlTranslator()
        node = ASTNode(root_element, child_nodes)
        evaluate_.side_effect = evaluate_return_values
        qname_val, attrs_val, text = call_values
        return (
            cxml_translator, node, RootElement_, qname_val, attrs_val, text
        )

    @pytest.fixture
    def str_attr_fixture(self, StringAttribute_):
        cxml_translator = CxmlTranslator()
        _qname, value = 'b', 'on'
        child_nodes = (
            ASTNode(qname, [Token(NAME, 'b')]),
            Token(EQUAL, '='),
            Token(TEXT, 'on'),
        )
        node = ASTNode(str_attr, child_nodes)
        return cxml_translator, node, StringAttribute_, _qname, value

    @pytest.fixture(params=[
        ([ASTNode(element, ())],
         ()),
        ([ASTNode(element, ()), None, ASTNode(trees, ())],
         ('tree', 'tree_2')),
    ])
    def tree_fixture(self, request, evaluate_, element_):
        child_nodes, trees = request.param
        trees_val = [(t, None) for t in trees]

        cxml_translator = CxmlTranslator()
        node = ASTNode(tree, child_nodes)
        expected_value = element_, trees_val

        evaluate_.side_effect = [element_, trees_val]
        add_calls = [call(t) for t in trees]

        return cxml_translator, node, element_, add_calls, expected_value

    @pytest.fixture(params=[
        (('tree',),               ('tree',),            ['tree']),
        (('tree', ',', 'tree_2'), ('tree', ['tree_2']), ['tree', 'tree_2']),
    ])
    def tree_list_fixture(self, request, evaluate_):
        child_nodes, evaluate_return_values, expected_value = request.param
        cxml_translator = CxmlTranslator()
        node = ASTNode(tree_list, child_nodes)
        evaluate_.side_effect = evaluate_return_values
        return cxml_translator, node, expected_value

    @pytest.fixture(params=[
        (['tree'],                  0, 'tree',        ['tree']),
        ([None, 'tree_list', None], 1, ['tree_list'], ['tree_list']),
    ])
    def trees_fixture(self, request, evaluate_):
        child_nodes, child_idx, eval_retval, expected_value = request.param
        cxml_translator = CxmlTranslator()
        node = ASTNode(tree, child_nodes)
        evaluate_.return_value = eval_retval
        return cxml_translator, node, child_idx, expected_value

    # fixture components ---------------------------------------------

    @pytest.fixture
    def Element_(self, request):
        return class_mock(request, 'cxml.translator.Element')

    @pytest.fixture
    def element_(self, request):
        return instance_mock(request, Element)

    @pytest.fixture
    def evaluate_(self, request):
        return method_mock(request, CxmlTranslator, 'evaluate')

    @pytest.fixture
    def NamespaceDeclaration_(self, request):
        return class_mock(request, 'cxml.translator.NamespaceDeclaration')

    @pytest.fixture
    def RootElement_(self, request):
        return class_mock(request, 'cxml.translator.RootElement')

    @pytest.fixture
    def root_element_(self, request):
        return instance_mock(request, RootElement)

    @pytest.fixture
    def StringAttribute_(self, request):
        return class_mock(request, 'cxml.translator.StringAttribute')
