# encoding: utf-8

"""
Test suite for parselib.lexer module.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import sys
sys.path.insert(0, '.')

import pytest

from cxml.lib.grammar import _Symbol
from cxml.lib.lexer import Lexer, Token

from ..mocklib import class_mock, instance_mock


class DescribeToken(object):

    def it_has_a_symbol(self):
        symbol, lexeme = 42, None
        token = Token(symbol, lexeme)
        assert token.symbol is symbol

    def it_has_a_lexeme(self):
        symbol, lexeme = None, 'foobar'
        token = Token(symbol, lexeme)
        assert token.lexeme is lexeme

    def it_has_a_useful_repr(self):
        symbol, lexeme = _Symbol('EQUAL', 42), 'barfoo'
        token = Token(symbol, lexeme)
        assert repr(token) == "Token(EQUAL, 'barfoo')"

    def it_raises_on_assign_to_new_attribute(self):
        token = Token(None, None)
        with pytest.raises(AttributeError):
            token.new_attr = '9'


class DescribeLexer(object):

    def it_can_peek_at_the_next_input_character(self, peek_fixture):
        lexer, expected_value = peek_fixture
        assert lexer._peek == expected_value

    def it_can_accept_the_next_input_character(self, next_fixture):
        lexer, expected_value, expected_pos = next_fixture
        assert lexer._next() == expected_value
        assert lexer._pos == expected_pos

    def it_can_backup_to_reverse_a_next(self):
        lexer = Lexer('a')
        lexer._next()
        lexer._backup()
        assert lexer._pos == 0

    def it_can_accept_a_run_of_chars_in_a_charset(self):
        lexer = Lexer('ohsofoobaric')
        lexer._accept_run('fhos')
        assert lexer._pos == 7

    def it_can_accept_a_run_of_chars_not_in_a_charset(self):
        lexer = Lexer('x:foo="bar"')
        lexer._accept_until('=')
        assert lexer._pos == 5

    def it_can_discard_its_current_lexeme(self):
        lexer = Lexer('foobar')
        lexer._pos = 3
        lexer._ignore()
        assert lexer._peek == 'b'

    def it_can_emit_a_token_containing_the_current_lexeme(self, emit_fixture):
        lexer, terminal, lexeme, Token_, token_, new_pos = emit_fixture

        lexer._emit(terminal)

        Token_.assert_called_once_with(terminal, lexeme)
        assert lexer._tokens[-1] is token_
        assert lexer._start == new_pos
        assert lexer._pos == lexer._start

    def it_knows_how_many_characters_are_in_the_input(self):
        lexer = Lexer('barfoo')
        assert lexer._len == 6

    def it_knows_how_many_characters_are_in_its_current_lexeme(self):
        lexer = Lexer('foobar')
        lexer._pos = 3
        assert lexer._llen == 3

    def it_raises_if_default_start_state_method_is_used(self):
        lexer = Lexer(None)
        with pytest.raises(NotImplementedError):
            lexer._lex_start()

    def it_can_skip_characters_at_beginning_of_lexeme(self, skip_fixture):
        lexer, n, new_pos, exception = skip_fixture

        if exception:
            with pytest.raises(exception):
                lexer._skip(n)
            assert lexer._start == lexer._pos == new_pos
        else:
            lexer._skip(n)
            assert lexer._start == new_pos
            assert lexer._pos == lexer._start

    # fixtures -------------------------------------------------------

    @pytest.fixture
    def emit_fixture(self, Token_, token_):
        lexer = Lexer('foobar')
        lexer._pos = 3
        terminal_symbol, lexeme = 42, 'foo'
        Token_.return_value = token_
        return lexer, terminal_symbol, lexeme, Token_, token_, lexer._pos

    @pytest.fixture(params=[
        ('ƒoo', 'ƒ',  1),
        ('',    None, 1),
    ])
    def next_fixture(self, request):
        input_, expected_value, expected_pos = request.param
        lexer = Lexer(input_)
        return lexer, expected_value, expected_pos

    @pytest.fixture(params=[
        ('ƒoo', 'ƒ'),
        ('',    None),
    ])
    def peek_fixture(self, request):
        input_, expected_value = request.param
        lexer = Lexer(input_)
        return lexer, expected_value

    @pytest.fixture(params=[
        ('ƒoobår', 1, 1, None),
        ('',       1, 0, ValueError),
        ('ƒoo',    3, 3, None),
        ('ƒoo',    4, 0, ValueError),
    ])
    def skip_fixture(self, request):
        input_, n, new_pos, exception = request.param
        lexer = Lexer(input_)
        return lexer, n, new_pos, exception

    # fixture components ---------------------------------------------

    @pytest.fixture
    def Token_(self, request):
        return class_mock(request, 'cxml.lib.lexer.Token')

    @pytest.fixture
    def token_(self, request):
        return instance_mock(request, Token)
