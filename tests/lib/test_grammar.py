# encoding: utf-8

"""
Test suite for parselib.grammar module.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import sys
sys.path.insert(0, '.')

import pytest

from cxml.lib.grammar import (
    NonterminalSymbol, Production, Productions, _Symbol, TerminalSymbol
)


class Describe_Symbol(object):

    def it_behaves_like_an_int(self):
        symbol = _Symbol(None)
        assert symbol == -666

    def it_has_a_name(self):
        symbol = _Symbol('foobar')
        assert symbol.name == 'foobar'

    def it_has_a_useful_string_value(self):
        _Symbol._next_id = 1024
        symbol = _Symbol('foobar')
        assert str(symbol) == "foobar (1024)"

    def it_can_assign_the_next_symbol_id(self):
        _Symbol._next_id = 42
        assert _Symbol.next_id() == 42
        assert _Symbol._next_id == 43


class DescribeTerminalSymbol(object):

    def it_is_a_symbol(self):
        terminal_symbol = TerminalSymbol(None)
        assert isinstance(terminal_symbol, _Symbol)

    def it_assigns_symbol_ids_starting_at_1(self):
        terminal_symbol = TerminalSymbol(None)
        terminal_symbol_2 = TerminalSymbol(None)
        assert 0 < terminal_symbol < 25
        assert terminal_symbol_2 == terminal_symbol + 1

    def it_has_a_useful_repr(self):
        TerminalSymbol._next_id = 42
        terminal_symbol = TerminalSymbol('COLON')
        assert repr(terminal_symbol) == "TerminalSymbol(42, 'COLON')"

    def it_knows_it_is_a_terminal(self):
        terminal_symbol = TerminalSymbol(None)
        assert terminal_symbol.is_terminal is True


class DescribeNonterminalSymbol(object):

    def it_is_a_symbol(self):
        nonterminal_symbol = NonterminalSymbol(None)
        assert isinstance(nonterminal_symbol, _Symbol)

    def it_assigns_symbol_ids_starting_at_1000(self):
        nonterminal_symbol = NonterminalSymbol(None)
        nonterminal_symbol_2 = NonterminalSymbol(None)
        assert 1000 < nonterminal_symbol < 1025
        assert nonterminal_symbol_2 == nonterminal_symbol + 1

    def it_has_a_useful_repr(self):
        NonterminalSymbol._next_id = 1042
        nonterminal_symbol = NonterminalSymbol('expr')
        assert repr(nonterminal_symbol) == "NonterminalSymbol(1042, 'expr')"

    def it_knows_it_is_not_a_terminal(self):
        nonterminal_symbol = NonterminalSymbol(None)
        assert nonterminal_symbol.is_terminal is False


class DescribeProduction(object):

    def it_has_a_head(self):
        head = NonterminalSymbol('head_symbol')
        production = Production(head, ())
        assert production.head is head

    def it_has_a_tuple_for_a_body(self):
        body = iter(['a', 'b', 'c'])
        production = Production(None, body)
        assert type(production.body) is tuple
        assert production.body == ('a', 'b', 'c')

    def it_raises_on_attempt_to_create_a_new_attribute(self):
        production = Production(None, ())
        with pytest.raises(AttributeError):
            production.new_attr = '9'


class DescribeProductions(object):

    def it_can_get_the_productions_for_a_head_symbol(self, getitem_fixture):
        production_seq, key, expected_productions = getitem_fixture
        productions = Productions(production_seq)
        assert list(productions[key]) == expected_productions

    def it_can_construct_from_seq_of_head_body_pairs(self, from_seq_fixture):
        head_body_pairs = from_seq_fixture

        productions = Productions.from_seq(*head_body_pairs)

        ps = productions._productions
        for idx, (head, body) in enumerate(head_body_pairs):
            production = ps[idx]
            assert type(production) is Production
            assert production.head is head
            assert production.body is body

    def it_raises_on_attempt_to_create_a_new_attribute(self):
        productions = Productions(())
        with pytest.raises(AttributeError):
            productions.new_attr = '9'

    # fixture --------------------------------------------------------

    @pytest.fixture(params=[
        (42, (0, 1)),
        (24, (2,)),
    ])
    def getitem_fixture(self, request):
        key, member_indices = request.param
        ps = (
            Production(42, ()),
            Production(42, ()),
            Production(24, ()),
        )
        expected_productions = list(ps[i] for i in member_indices)
        return ps, key, expected_productions

    @pytest.fixture
    def from_seq_fixture(self):
        head_body_pairs = (
            (42, (1, 2, 3)),
            (24, (4, 5, 6)),
        )
        return head_body_pairs
