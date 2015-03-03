# encoding: utf-8

"""
Translator taking a CXML abstract syntax tree (AST) and producing an object
graph rooted in a |RootElement| object.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .model import (
    Element, NamespaceDeclaration, RootElement, StringAttribute
)
from .symbols import attrs, qname


class CxmlTranslator(object):
    """
    Constructs a |RootElement| object (with its graph) corresponding to
    a Compact XML Expression Language (CXML) abstract syntax tree (AST).
    """
    @classmethod
    def translate(cls, tree):
        """
        Return a |RootElement| object corresponding to the AST in *tree*,
        containing all the right children, with all the right attributes,
        etc.
        """
        cxml_translator = cls()
        return cxml_translator.evaluate(tree)

    # -----------------------------------------------------------------------
    # node evaluation methods
    # -----------------------------------------------------------------------
    # The role of a node evaluation method is to reduce an AST node to the
    # graph subtree appropriate to the translator, like a StringAttribute
    # object, etc.
    # -----------------------------------------------------------------------

    def evaluate(self, node):
        """
        Return the value obtained by dispatching *node* to the appropriate
        eval method.
        """
        eval_method = getattr(self, node.name)
        return eval_method(node)

    def nsdecl(self, node):
        """
        Return a |NamespaceDeclaration| object constructed from the
        token.lexemes in *node*.
        """
        name_token, _ = node.child_nodes
        nspfx = name_token.lexeme
        return NamespaceDeclaration(nspfx)

    def qname(self, node):
        """
        Return the qualified name in *node* as a single string, e.g.
        'w:rPr'.
        """
        return ''.join(token.lexeme for token in node.child_nodes)

    def str_attr(self, node):
        """
        Return a |StringAttribute| object constructed from the AST *node*.
        """
        qname_node, _, text_token = node.child_nodes
        qname = self.evaluate(qname_node)
        value = text_token.lexeme
        return StringAttribute.new(qname, value)

    def attr(self, node):
        """
        Return a |StringAttribute| or |NamespaceDeclaration| object,
        depending on the production in *node*.
        """
        str_attr_or_nsdecl_node, = node.child_nodes
        return self.evaluate(str_attr_or_nsdecl_node)

    def attr_list(self, node):
        """
        Return a list of attribute objects produced from *node*.
        """
        nodes = node.child_nodes
        if len(nodes) == 1:
            attr_node, = nodes
            return [self.evaluate(attr_node)]

        attr_node, _, attr_list_node = nodes
        attr = self.evaluate(attr_node)
        attr_list = self.evaluate(attr_list_node)

        return [attr] + attr_list

    def attrs(self, node):
        """
        Return a list of attribute objects produced from *node*.
        """
        _, attr_list_node, _ = node.child_nodes
        return self.evaluate(attr_list_node)

    def element(self, node):
        """
        Return an |Element| object constructed from the values in *node*.
        """
        qname_val, attrs_val, text = None, [], ''

        for node in node.child_nodes:
            symbol = node.symbol
            if symbol == qname:
                qname_val = self.evaluate(node)
            elif symbol == attrs:
                attrs_val = self.evaluate(node)
            else:
                # node is a TEXT token
                text = node.lexeme

        return Element.new(qname_val, attrs_val, text)

    def tree(self, node):
        """
        Return an (element, trees) pair constructed from the values in
        *node*. The root element of each tree in *trees* is added to
        *element* as a child.
        """
        nodes = node.child_nodes

        if len(nodes) == 1:
            element_node, = nodes
            return self.evaluate(element_node), []

        element_node, _, trees_node = nodes
        element = self.evaluate(element_node)
        trees = self.evaluate(trees_node)
        for child, _ in trees:
            element.add_child(child)
        return element, trees

    def tree_list(self, node):
        """
        Return a list of tree objects produced from *node*.
        """
        nodes = node.child_nodes
        if len(nodes) == 1:
            tree_node, = nodes
            return [self.evaluate(tree_node)]

        tree_node, _, tree_list_node = nodes
        tree = self.evaluate(tree_node)
        tree_list = self.evaluate(tree_list_node)

        return [tree] + tree_list

    def trees(self, node):
        """
        Return a list of linked tree objects produced from *node*.
        """
        nodes = node.child_nodes
        if len(nodes) == 1:
            tree_node, = nodes
            return [self.evaluate(tree_node)]

        _, tree_list_node, _ = nodes
        return self.evaluate(tree_list_node)

    def root_element(self, node):
        """
        Return a |RootElement| object constructed from the values in *node*.
        """
        qname_val, attrs_val, text = None, [], ''

        for node in node.child_nodes:
            symbol = node.symbol
            if symbol == qname:
                qname_val = self.evaluate(node)
            elif symbol == attrs:
                attrs_val = self.evaluate(node)
            else:
                # node is a TEXT token
                text = node.lexeme

        return RootElement.new(qname_val, attrs_val, text)

    def root(self, node):
        """
        Return a |RootElement| object, having linked its children to it.
        """
        nodes = node.child_nodes

        if len(nodes) == 2:  # root_element + SNTL
            root_element_node, _ = nodes
            root_element = self.evaluate(root_element_node)
            return root_element

        root_element_node, slash_token, trees_node, _ = nodes
        root_element = self.evaluate(root_element_node)
        trees = self.evaluate(trees_node)
        for child, _ in trees:
            root_element.add_child(child)
        return root_element
