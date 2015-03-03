# encoding: utf-8

"""
Lexical analyzer, (a.k.a lexer, tokenizer) for CXML language.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .lib.lexer import Lexer

from .symbols import (
    COLON, COMMA, EQUAL, LBRACE, LPAREN, NAME, RBRACE, RPAREN, SLASH, SNTL,
    TEXT
)


alphas = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
nums = '0123456789'

name_start_chars = alphas + '_'
name_chars = alphas + nums + '_-.'

punctuation = ':,=/{}()'


class CxmlLexer(Lexer):
    """
    Lexer object for CXML.
    """
    def _lex_start(self):
        """
        The starting and fallback state of the lexer, where it is in-between
        tokens.
        """
        # should only be entering this state in-between tokens
        assert self._start == self._pos

        peek = self._peek

        # test EOF first to avoid __contains__ errors
        if peek is None:
            return self._lex_eof

        # ignore whitespace as a priority
        elif peek == ' ':
            return self._lex_whitespace

        elif peek in name_start_chars:
            return self._lex_name

        elif peek in punctuation:
            return self._lex_punctuation

        elif peek == '"':
            return self._lex_quoted_string

        else:
            raise SyntaxError(
                "at character '%s' in '%s'" % (peek, self._input)
            )

    def _lex_eof(self):
        """
        Emit `SNTL` token and end parsing by returning |None|.
        """
        assert self._start == self._pos == self._len
        self._emit(SNTL)
        return None

    def _lex_name(self):
        """
        Emit maximal sequence of name characters.
        """
        self._accept_run(name_chars)
        self._emit(NAME)
        return self._lex_start

    def _lex_punctuation(self):
        """
        Emit the appropriate single-character punctuation token, such as
        COLON.
        """
        symbol = self._next()

        token_type = {
            ':': COLON, ',': COMMA, '{': LBRACE, '}': RBRACE,
            '=': EQUAL, '/': SLASH, '(': LPAREN, ')': RPAREN,
        }[symbol]

        self._emit(token_type)
        return self._lex_text if symbol in '=}' else self._lex_start

    def _lex_quoted_string(self):
        """
        Emit the text of a quoted string as a TEXT token, discarding the
        enclosing quote characters.
        """
        # skip over opening quote
        self._skip()

        # accept any character until another double-quote or EOF
        self._accept_until('"')
        self._emit(TEXT)

        # raise unterminated if next character not closing quote
        if self._peek != '"':
            raise SyntaxError("unterminated quote")
        self._skip()

        return self._lex_start

    def _lex_text(self):
        """
        Parse a string value, either a quoted string or a raw string, which
        is terminated by a comma, closing brace, slash, or right paren.
        """
        peek = self._peek

        if peek is None:
            return self._lex_eof

        if peek == '"':
            return self._lex_quoted_string

        if peek not in ',}/)':
            self._accept_until(',}/)')
            self._emit(TEXT)

        return self._lex_start

    def _lex_whitespace(self):
        """
        Consume all whitespace at current position and ignore it.
        """
        self._accept_run(' ')
        self._ignore()
        return self._lex_start
