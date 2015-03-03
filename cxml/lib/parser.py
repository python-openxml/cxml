# encoding: utf-8

"""
General-purpose recursive descent parser.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


class ASTNode(object):
    """
    A node in an abstract syntax tree (AST).
    """

    __slots__ = ('_symbol', '_child_nodes')

    def __init__(self, symbol, child_nodes):
        self._symbol = symbol
        self._child_nodes = tuple(child_nodes)

    def __repr__(self):
        child_nodes_str = ', '.join(repr(n) for n in self._child_nodes)
        return 'ASTNode(%s, (%s))' % (self._symbol, child_nodes_str)

    @property
    def child_nodes(self):
        return self._child_nodes

    @property
    def name(self):
        """
        The name of this node's symbol, e.g. 'COMMA' for a terminal symbol or
        'attr' for a nonterminal symbol.
        """
        return self._symbol.name

    @property
    def symbol(self):
        return self._symbol

    @property
    def value(self):
        """
        A string formed by concatenating each of the leaf token lexemes in
        this tree.
        """
        child_values = [c.value for c in self._child_nodes]
        return ''.join(child_values)


class Parser(object):
    """
    Parser for Compact XML Expression Languate (CXML).
    """
    def __init__(self, lexer, productions):
        self._lexer = lexer
        self._productions = productions

    def parse(self, start_symbol):
        tokens = list(self._lexer)
        ast_root, remaining_tokens = self._match_symbol(start_symbol, tokens)
        if remaining_tokens:
            raise ValueError(
                'not all tokens were consumed %s' % (remaining_tokens,)
            )
        if ast_root is None:
            raise SyntaxError("in '%s'" % self._lexer._input)
        return ast_root

    def _match_symbol(self, symbol, tokens):
        """
        Delegate to the appropriate method depending whether *symbol* is
        a terminal or nonterminal.
        """
        if symbol.is_terminal:
            return self._match_terminal(symbol, tokens)
        return self._match_nonterminal(symbol, tokens)

    def _match_terminal(self, symbol, tokens):
        """
        Return a (token, remaining_tokens) pair where *token* is the head of
        the *tokens* sequence and *remaining_tokens* is its tail, if the head
        of *tokens* is of token class *symbol*. If the head of *tokens* is of
        another token class, return (|None|, |None|).
        """
        if not tokens:  # an empty list never matches
            return None, None
        if tokens[0].symbol == symbol:
            return tokens[0], tokens[1:]
        return None, None

    def _match_nonterminal(self, symbol, tokens):
        """
        Return a (node, remaining_tokens) 2-tuple, where *node* is an
        abstract syntax tree (AST) node for *symbol*, derived recursively
        from *tokens*.
        """
        for p in self._productions[symbol]:
            node, remaining_tokens = self._match_production(p, tokens)
            # take the first successful derivation
            if node is not None:
                return node, remaining_tokens
        return None, None

    def _match_production(self, production, tokens):
        """
        Return a (node, remaining_tokens) pair, where *node* is an abstract
        syntax tree (AST) node for the head of *production* and
        *remaining_tokens* is the sequence of tokens not consumed by the
        production. The child nodes of *node* are derived from recursive
        matching of the terminal symbols in the body of *production*. Returns
        (|None|, |None|) if the body of *production* did not match *tokens*.
        """
        remaining_tokens, children = tokens, []
        for symbol in production.body:
            node, remaining_tokens = self._match_symbol(
                symbol, remaining_tokens
            )
            if node is None:  # this production doesn't match against tokens
                return None, None
            children.append(node)

        return ASTNode(production.head, children), remaining_tokens
