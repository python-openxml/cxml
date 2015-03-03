# encoding: utf-8

"""
API for CXML translator.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


__version__ = '0.9.6'


from .lexer import CxmlLexer
from .parser import CxmlParser
from .symbols import root
from .translator import CxmlTranslator


def xml(cxml):
    """
    Return the XML generated from *cxml*.
    """
    lexer = CxmlLexer(cxml)
    parser = CxmlParser(lexer)
    root_ast = parser.parse(root)
    root_element = CxmlTranslator.translate(root_ast)
    return root_element.xml
