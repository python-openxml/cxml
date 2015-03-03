# encoding: utf-8

"""
Parser for CXML language.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .lib.grammar import Productions
from .lib.parser import Parser

from .symbols import (
    COLON, COMMA, EQUAL, LBRACE, LPAREN, NAME, RBRACE, RPAREN, SLASH, SNTL,
    TEXT, attr, attr_list, attrs, element, nsdecl, qname, root, root_element,
    str_attr, tree, tree_list, trees,
)

productions = Productions.from_seq(
    (root,         (root_element, SLASH, trees, SNTL)),
    (root,         (root_element, SNTL)),
    (root_element, (qname, attrs, TEXT)),
    (root_element, (qname, attrs)),
    (root_element, (qname, TEXT)),
    (root_element, (qname,)),
    (trees,        (LPAREN, tree_list, RPAREN)),
    (trees,        (tree,)),
    (tree_list,    (tree, COMMA, tree_list)),
    (tree_list,    (tree,)),
    (tree,         (element, SLASH, trees)),
    (tree,         (element,)),
    (element,      (qname, attrs, TEXT)),
    (element,      (qname, attrs)),
    (element,      (qname, TEXT)),
    (element,      (qname,)),
    (attrs,        (LBRACE, attr_list, RBRACE)),
    (attr_list,    (attr, COMMA, attr_list)),
    (attr_list,    (attr,)),
    (attr,         (str_attr,)),
    (attr,         (nsdecl,)),
    (str_attr,     (qname, EQUAL, TEXT)),
    (qname,        (NAME, COLON, NAME)),
    (qname,        (NAME,)),
    (nsdecl,       (NAME, COLON)),
)


class CxmlParser(Parser):
    """
    Parser for Compact XML Expression Languate (CXML).
    """
    def __init__(self, lexer):
        super(CxmlParser, self).__init__(lexer, productions)
