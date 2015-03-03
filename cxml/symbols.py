# encoding: utf-8

"""
Symbol definitions for CXML lexer and parser.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .lib.grammar import SNTL, NonterminalSymbol, TerminalSymbol  # noqa


COLON = TerminalSymbol('COLON')
COMMA = TerminalSymbol('COMMA')
EQUAL = TerminalSymbol('EQUAL')
NAME = TerminalSymbol('NAME')
SLASH = TerminalSymbol('SLASH')
TEXT = TerminalSymbol('TEXT')
LBRACE = TerminalSymbol('LBRACE')
RBRACE = TerminalSymbol('RBRACE')
LPAREN = TerminalSymbol('LPAREN')
RPAREN = TerminalSymbol('RPAREN')


attr = NonterminalSymbol('attr')
attr_list = NonterminalSymbol('attr_list')
attrs = NonterminalSymbol('attrs')
element = NonterminalSymbol('element')
nsdecl = NonterminalSymbol('nsdecl')
qname = NonterminalSymbol('qname')
root = NonterminalSymbol('root')
root_element = NonterminalSymbol('root_element')
str_attr = NonterminalSymbol('str_attr')
tree = NonterminalSymbol('tree')
tree_list = NonterminalSymbol('tree_list')
trees = NonterminalSymbol('trees')
