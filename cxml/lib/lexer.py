# encoding: utf-8

"""
General-purpose lexical analyzer objects.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .grammar import SNTL


class Token(object):
    """
    A token, classified by a terminal symbol (token class) and containing
    a lexeme of that class.
    """

    __slots__ = ('_symbol', '_lexeme')

    def __init__(self, symbol, lexeme):
        self._symbol = symbol  # always a terminal symbol
        self._lexeme = lexeme

    def __repr__(self):
        """
        Like "Token(COMMA, ',')".
        """
        return "Token(%s, '%s')" % (self._symbol.name, self._lexeme)

    @property
    def symbol(self):
        """
        The terminal symbol this token is an instance of.
        """
        return self._symbol

    @property
    def lexeme(self):
        """
        String value (lexeme) of this token.
        """
        return self._lexeme

    @property
    def value(self):
        """
        The string value (lexeme) of this token. Useful generic alternative
        when walking an AST in which this token is a node. Both ASTNode and
        Token objects have a value property.
        """
        return self._lexeme


class Lexer(object):
    """
    Lexer base class. A lexical specification is implemented as a set of
    state methods in a subclass. This base class provides a set of helper
    methods to the state methods. The start state defaults to
    :meth:`_lex_start`, but may be overridden by providing the name of
    another method on construction. Whatever the start state method is named,
    it must be implemented in the subclass; there is no default
    implementation.
    """
    def __init__(self, input, start_state='_lex_start', emit_sntl=True):
        self._input = input
        self._start = 0
        self._pos = 0
        self._start_state = getattr(self, start_state)
        self._emit_sntl = emit_sntl
        self._tokens = []

    def __iter__(self):
        """
        Generate each of the tokens in input.
        """
        # reset to start state so lexer instance is reusable
        self._start = self._pos = 0
        self.state = self._start_state

        return iter(self._next_token, None)

    def _next_token(self):
        """
        Suitable for use in an `iter(_next_token, None)` function call,
        returns the next token if one is available, otherwise passes control
        to the next state function. Calling `lexer.emit()` in the state
        method adds a token to the queue, which then makes its way back to
        the caller once the state function returns. The iterator constructed
        this way terminates when last token is returned and the next state is
        |None|, indicating EOF.
        """
        if self._token_in_queue:
            return self._pop_token()

        while self.state is not None:
            self.state = self.state()
            if self._token_in_queue:
                return self._pop_token()

        if self._start != self._pos or self._pos < self._len:
            raise ValueError('not all input consumed')

    def _accept_run(self, charset):
        """
        Accept characters from the input string into the current lexeme while
        the character is in *charset*.
        """
        while True:
            c = self._next()
            if c is None or c not in charset:
                self._backup()
                break

    def _accept_until(self, charset):
        """
        Position pos after the last input character that is NOT a member of
        *charset*, stopping at EOF if encountered.
        """
        while True:
            c = self._next()
            if c is None or c in charset:
                self._backup()
                break

    def _backup(self):
        """
        Reduce the length of the current lexeme by one character.
        """
        self._pos -= 1

    def _emit(self, token_type):
        """
        Add a token of *token_type* to the queue containing the current
        lexeme and reset the lexeme cursors to the next input character.
        """
        lexeme = self._input[self._start:self._pos]
        self._start = self._pos
        self._tokens.append(Token(token_type, lexeme))

    def _ignore(self):
        """
        Set start to pos, effectively discarding the current run.
        """
        self._start = self._pos

    @property
    def _len(self):
        """
        The length of the input string.
        """
        return len(self._input)

    def _lex_start(self):
        """
        The default start state method; this version raises
        |NotImplementedError| as it must be implemented by the particular
        lexical specification implemented as a subclass of |Lexer|.
        """
        raise NotImplementedError

    @property
    def _llen(self):
        """
        The length of the current lexeme.
        """
        return self._pos - self._start

    def _next(self):
        """
        Return the next input character and advance pos to the next position.
        Return |None| if at EOF, but advance pos in any case, such that
        _backup() works consistently at EOF.
        """
        next_char = self._input[self._pos] if self._pos < self._len else None
        self._pos += 1
        return next_char

    @property
    def _peek(self):
        """
        The next unicode character in the input.
        """
        if self._pos >= len(self._input):
            return None
        return self._input[self._pos]

    def _pop_token(self):
        """
        Remove the first token in the queue and return it.
        """
        return self._tokens.pop(0)

    def _skip(self, n=1):
        """
        Ignore *n* characters of input. Raises if lexeme characters would be
        lost or fewer than *n* characters remain in input.
        """
        if self._start != self._pos:
            raise ValueError('cannot skip, partial lexeme would be lost')
        if self._start + n > len(self._input):
            raise ValueError('cannot skip past EOF')
        self._start = self._pos = self._start + n

    @property
    def _token_in_queue(self):
        """
        |True| if there is an emittable token in the token queue. If the top
        token is `SNTL` and *emit_sntl* is |False|, that token is popped from
        the queue and discarded.
        """
        while self._tokens:
            token = self._tokens[0]
            if token.symbol is SNTL and self._emit_sntl is False:
                # discard SNTL token
                self._pop_token()
                continue
            return True
        return False
