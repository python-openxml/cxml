# encoding: utf-8

"""
Objects required to define a grammar, in particular, token classes,
nonterminals, and productions.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


class _Symbol(int):
    """
    Base class for |TerminalSymbol| and |NonterminalSymbol|, having an int
    value (for efficient comparison) but also having a name for user-friendly
    printing.
    """

    _next_id = -666

    def __new__(cls, name, id_=None):
        symbol_id = id_ if id_ is not None else cls.next_id()
        self = super(_Symbol, cls).__new__(cls, symbol_id)
        self._name = name
        return self

    def __str__(self):
        return '%s (%d)' % (self._name, int(self))

    @property
    def name(self):
        """
        The string name of this symbol, as spelled in the grammar, suitable
        for use in the user interface.
        """
        return self._name

    @classmethod
    def next_id(cls):
        """
        Return the next available symbol identifier for this symbol type.
        """
        id_ = cls._next_id
        cls._next_id += 1
        return id_


class TerminalSymbol(_Symbol):
    """
    A token type, having an int value (for rapid comparison) but also having
    a name for user-friendly printing.
    """

    _next_id = 1

    def __repr__(self):
        return "TerminalSymbol(%d, '%s')" % (int(self), self._name)

    @property
    def is_terminal(self):
        return True


class NonterminalSymbol(_Symbol):
    """
    A nonterminal, a symbol that may appear as the head of a production rule.
    It is an int value (for rapid comparison) but also has a name for
    user-friendly printing.
    """

    _next_id = 1001

    def __repr__(self):
        return "NonterminalSymbol(%d, '%s')" % (int(self), self._name)

    @property
    def is_terminal(self):
        return False


class Production(object):
    """
    A production rule of a grammar, consisting of a head and a body.
    """

    __slots__ = ('_head', '_body')

    def __init__(self, head, body):
        self._head = head
        self._body = tuple(body)

    @property
    def head(self):
        """
        The nonterminal symbol produced by this rule.
        """
        return self._head

    @property
    def body(self):
        """
        The sequence of symbols that can be used to (recursively) derive the
        head symbol from a sequence of tokens.
        """
        return self._body


class Productions(object):
    """
    A collection of |Production| objects, having mapping semantics for
    indexed access, except that the value returned is an iterator over the
    production rules having a matching key.
    """

    __slots__ = ('_productions',)

    def __init__(self, productions):
        self._productions = tuple(productions)

    def __getitem__(self, key):
        """
        Return an iterator that will generate each production with head
        matching *key*, in the order the productions should be matched.
        """
        return (p for p in self._productions if p.head == key)

    @classmethod
    def from_seq(cls, *head_body_pairs):
        """
        Return a |Productions| object constructed from the sequence of
        (head, body) pairs provided as positional parameters.
        """
        return cls(
            [Production(head, body) for head, body in head_body_pairs]
        )


# the sentinal token, having bool() value False
SNTL = TerminalSymbol('SNTL', 0)
