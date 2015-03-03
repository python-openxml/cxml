# encoding: utf-8

"""
Test suite for cxml lexer module.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import sys
sys.path.insert(0, '.')

import pytest

from cxml.lexer import CxmlLexer as Lexer
from cxml.symbols import (
    COLON, COMMA, EQUAL, LBRACE, LPAREN, NAME, RBRACE, RPAREN, SLASH, SNTL,
    TEXT
)


class DescribeLexer(object):

    def it_recognizes_the_end_of_input(self):
        lexer = Lexer('')

        token, = list(lexer)

        assert token.symbol == SNTL
        assert token.lexeme == ''

    def it_recognizes_a_name(self):
        lexer = Lexer('_42foo', '_lex_name')

        tokens = list(lexer)

        assert len(tokens) == 2
        assert tokens[0].symbol == NAME
        assert tokens[0].lexeme == '_42foo'

    def it_recognizes_a_punctuation_character(self, punctuation_fixture):
        lexer, symbol, lexeme = punctuation_fixture

        token, _ = list(lexer)

        assert token.symbol == symbol
        assert token.lexeme == lexeme

    def it_recognizes_a_quoted_string(self, quote_fixture):
        lexer, lexeme = quote_fixture

        token, _ = list(lexer)

        assert token.symbol == TEXT
        assert token.lexeme == lexeme

    def it_recognizes_a_text_lexeme(self, text_fixture):
        lexer, expected_values = text_fixture

        tokens = list(lexer)

        for idx, (symbol, lexeme) in enumerate(expected_values):
            token = tokens[idx]
            assert token.symbol is symbol
            assert token.lexeme == lexeme

    def it_skips_over_whitespace(self, whitespace_fixture):
        lexer = whitespace_fixture

        token, = list(lexer)

        assert token.symbol is SNTL
        assert token.lexeme == ''

    def it_breaks_input_into_tokens(self, lex_fixture):
        input_, expected_values = lex_fixture

        tokens = list(Lexer(input_))

        for idx, (symbol, lexeme) in enumerate(expected_values):
            token = tokens[idx]
            assert token.symbol is symbol
            assert token.lexeme == lexeme

    # fixtures -------------------------------------------------------

    @pytest.fixture(params=[
        ('  foo', ((NAME, 'foo'),)),
        (':',     ((COLON, ':'),)),
        ('w:rPr', ((NAME, 'w'), (COLON, ':'), (NAME, 'rPr'))),
        ('{foo}', ((LBRACE, '{'), (NAME, 'foo'), (RBRACE, '}'))),
        ('foo{anm=bar}"baz"', (
            (NAME, 'foo'), (LBRACE, '{'), (NAME, 'anm'), (EQUAL, '='),
            (TEXT, 'bar'), (RBRACE, '}'), (TEXT, 'baz'),
        )),
        ('w:rPr{r:,w:val="8,7"}/(w:r{r:id=1}foo,w:r{r:id=3})', (
            (NAME,   'w'), (COLON,  ':'),   (NAME,   'rPr'), (LBRACE, '{'),
            (NAME,   'r'), (COLON,  ':'),   (COMMA,  ','),   (NAME,   'w'),
            (COLON,  ':'), (NAME,   'val'), (EQUAL,  '='),   (TEXT,   '8,7'),
            (RBRACE, '}'), (SLASH,  '/'),   (LPAREN, '('),   (NAME,   'w'),
            (COLON,  ':'), (NAME,   'r'),   (LBRACE, '{'),   (NAME,   'r'),
            (COLON,  ':'), (NAME,   'id'),  (EQUAL,  '='),   (TEXT,   '1'),
            (RBRACE, '}'), (TEXT,   'foo'), (COMMA,  ','),   (NAME,   'w'),
            (COLON,  ':'), (NAME,   'r'),   (LBRACE, '{'),   (NAME,   'r'),
            (COLON,  ':'), (NAME,   'id'),  (EQUAL,  '='),   (TEXT,   '3'),
            (RBRACE, '}'), (RPAREN, ')')
        )),
    ])
    def lex_fixture(self, request):
        input_, values = request.param
        expected_values = values + ((SNTL, ''),)
        return input_, expected_values

    @pytest.fixture(params=[
        (':', COLON,  ':'),
        (',', COMMA,  ','),
        ('=', EQUAL,  '='),
        ('/', SLASH,  '/'),
        ('{', LBRACE, '{'),
        ('}', RBRACE, '}'),
        ('(', LPAREN, '('),
        (')', RPAREN, ')'),
    ])
    def punctuation_fixture(self, request):
        input_, symbol, lexeme = request.param
        lexer = Lexer(input_, '_lex_punctuation')
        return lexer, symbol, lexeme

    @pytest.fixture
    def quote_fixture(self):
        input_, lexeme = '"foobar"', 'foobar'
        lexer = Lexer(input_, '_lex_quoted_string')
        return lexer, lexeme

    @pytest.fixture(params=[
        ('',      ()),
        ('"foo"', ((TEXT,  'foo'),)),
        ('bar',   ((TEXT,  'bar'),)),
        (',',     ((COMMA, ','),)),
        ('/',     ((SLASH, '/'),)),
    ])
    def text_fixture(self, request):
        input_, values = request.param
        lexer = Lexer(input_, '_lex_text')
        expected_values = values + ((SNTL, ''),)
        return lexer, expected_values

    @pytest.fixture(params=['', ' ', '   '])
    def whitespace_fixture(self, request):
        input_ = request.param
        lexer = Lexer(input_, '_lex_whitespace')
        return lexer
