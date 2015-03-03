# encoding: utf-8

"""
CXML graph objects created by the parser and that provide the XML generation
behavior.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

nsmap = {
    'a':   ('http://schemas.openxmlformats.org/drawingml/2006/main'),
    'c':   ('http://schemas.openxmlformats.org/drawingml/2006/chart'),
    'dgm': ('http://schemas.openxmlformats.org/drawingml/2006/diagram'),
    'pic': ('http://schemas.openxmlformats.org/drawingml/2006/picture'),
    'r':   ('http://schemas.openxmlformats.org/officeDocument/2006/relations'
            'hips'),
    'w':   ('http://schemas.openxmlformats.org/wordprocessingml/2006/main'),
    'wp':  ('http://schemas.openxmlformats.org/drawingml/2006/wordprocessing'
            'Drawing'),
    'xml': ('http://www.w3.org/XML/1998/namespace')
}


def nsdecls_str(*nspfxs):
    """
    Return a string containing a namespace declaration for each of *nspfxs*,
    in the order they are specified.
    """
    nsdecls = ''
    for nspfx in nspfxs:
        nsdecls += ' xmlns:%s="%s"' % (nspfx, nsmap[nspfx])
    return nsdecls


def add_setwise(seq, seq_2):
    """
    Append any items in *seq_2* that do not already appear in *seq*.
    """
    for item in seq_2:
        if item in seq:
            continue
        seq.append(item)
    return seq


def subtract_setwise(seq, seq_2):
    """
    Remove any members of *seq_2* from *seq*.
    """
    for item in seq_2:
        if item in seq:
            seq.remove(item)
    return seq


class BaseAttribute(object):
    """
    Base class for |NamespaceDeclaration| and |StringAttribute|.
    """


class NamespaceDeclaration(BaseAttribute):
    """
    Represents an XML namespace declaration, e.g. xmlns:x="foo/bar".
    """
    def __init__(self, nspfx):
        self._nspfx = nspfx

    def __str__(self):
        """
        The namespace declaration string as it would appear in an XML
        element, e.g. `xmlns:w="http://foo/bar"`.
        """
        nspfx = self._nspfx
        return 'xmlns:%s="%s"' % (nspfx, nsmap[nspfx])

    @property
    def nspfx(self):
        """
        The namespace prefix of this namespace declaration.
        """
        return self._nspfx


class StringAttribute(BaseAttribute):
    """
    A normal XML attribute like `w:width="30840"`.
    """
    def __init__(self, nspfx, qname, value):
        self._nspfx = nspfx
        self._qname = qname
        self._value = value

    def __str__(self):
        """
        The string attribute as it would appear in an XML element, e.g.
        `w:val="1500"`.
        """
        return '%s="%s"' % (self._qname, self._value)

    @classmethod
    def new(cls, qname, value):
        """
        Return a |StringAttribute| object constructed from *qname* and
        *value*.
        """
        nspfx = qname.split(':')[0] if ':' in qname else ''
        return cls(nspfx, qname, value)

    @property
    def nspfx(self):
        """
        The namespace prefix of the name of this attribute, the empty string
        (`''`) if the attribute name is in the default namespace.
        """
        return self._nspfx


class BaseElement(object):
    """
    Base class for an XML element, subclassed by Element and RootElement and
    providing common properties and methods.
    """
    def __init__(self, nspfx, tagname, attrs, text):
        self._nspfx = nspfx
        self._tagname = tagname
        self._attrs = attrs
        self._text = text
        self._children = []
        self._indent_str = ''

    def __repr__(self):
        """
        Provide a more meaningful repr value for an Element object, one that
        displays it as XML, e.g. `<w:pPr w:w="1020">foo</w:pPr>`. Namespace
        declarations are omitted in a root element. Children are not
        indicated.
        """
        if self._text:
            return "<%s%s>%s</%s>" % (
                self._tagname, self._attrs_str, self._text, self._tagname
            )
        return "<%s%s/>" % (self._tagname, self._attrs_str)

    def add_child(self, child):
        """
        Add *child* as a child of this element.
        """
        self._children.append(child)

    @property
    def descendant_explicit_nspfxs(self):
        """
        A list containing the namespace prefixes explicitly declared in
        descendants of this element.
        """
        nspfxs = []
        for child in self._children:
            add_setwise(nspfxs, child.explicit_nspfxs)
            add_setwise(nspfxs, child.descendant_explicit_nspfxs)
        return nspfxs

    @property
    def explicit_nspfxs(self):
        """
        A list of the namespace prefixes explicitly defined in this element,
        in the order defined, e.g. ['w', 'a', 'wp'].
        """
        return [n.nspfx for n in self._nsdecls]

    @classmethod
    def new(cls, qname, attrs, text):
        """
        Return an |Element| object constructed from the parse results.
        """
        nspfx = qname.split(':')[0] if ':' in qname else ''
        return cls(nspfx, qname, attrs, text)

    @property
    def nspfx(self):
        """
        The namespace prefix of this element, the empty string (`''`) if the
        tag is in the default namespace.
        """
        return self._nspfx

    @property
    def tree_implicit_nspfxs(self):
        """
        A sequence containing each of the namespace prefixes appearing in
        this tree, either in a tag name or an attribute name. Each prefix
        appears once and only once, and in document order. Explicitly
        declared namespaces are not included, but will appear if present in
        a child element or attribute name.
        """
        nspfxs = [self.nspfx] if self.nspfx else []
        nspfxs = add_setwise(nspfxs, self._str_attr_nspfxs)
        for child in self._children:
            add_setwise(nspfxs, child.tree_implicit_nspfxs)
        return [pfx for pfx in nspfxs if pfx != 'xml']

    def xml(self, indent):
        """
        Return a string containing the XML of this element and all its
        children with a starting indent of *indent* spaces.
        """
        self._indent_str = ' ' * indent
        xml = self._start_tag
        for child in self._children:
            xml += child.xml(indent+2)
        xml += self._end_tag
        return xml

    @property
    def _end_tag(self):
        """
        The text of the closing tag of this element, if there is one. If the
        element contains text, no leading indentation is included.
        """
        if self._text:
            return '</%s>\n' % self._tagname
        if self._children:
            return '%s</%s>\n' % (self._indent_str, self._tagname)
        return ''

    @property
    def _nsdecls(self):
        """
        A list containing the namespace declaration objects of this element.
        """
        return [
            n for n in self._attrs if isinstance(n, NamespaceDeclaration)
        ]

    @property
    def _start_tag_closing(self):
        """
        The text forming the appropriate closing for the start tag of this
        element. If this element contains text, that text follows the start
        tag. If not, and this element has no children, an empty tag closing
        is returned. Otherwise, an opening tag closing is returned, followed
        by a newline.
        """
        if self._text:
            return '>%s' % self._text
        if self._children:
            return '>\n'
        return '/>\n'

    @property
    def _str_attr_nspfxs(self):
        """
        A list containing the unique namespace prefixes that appear in the
        string attributes of this element.
        """
        return add_setwise([], [a.nspfx for a in self._str_attrs if a.nspfx])

    @property
    def _str_attrs(self):
        """
        A list containing the string attributes of this element.
        """
        return [a for a in self._attrs if isinstance(a, StringAttribute)]


class Element(BaseElement):
    """
    Represents an XML element, having a namespace, tagname, attributes, and
    may contain either text or children (but not both) or may be empty.
    """
    @property
    def _attrs_str(self):
        """
        The XML string value of this element's attributes (and namespace
        declarations) in the order they appear in the `_attrs` field, e.g.
        ' w:w="1020"`. The string has a leading space when attributes are
        present and is an empty string when there are no attributes.
        """
        if not self._attrs:
            return ''
        return ' %s' % ' '.join(str(a) for a in self._attrs)

    @property
    def _start_tag(self):
        """
        A string containing the opening tag of this element, including string
        attributes and explicit namespace declarations in the order they
        appear. If this element contains text, that text follows the start
        tag. If not, and this element has no children, an empty tag is
        returned. Otherwise, an opening tag is returned, followed by
        a newline. The tag is indented by this element's indent value in all
        cases.
        """
        return '%s<%s%s%s' % (
            self._indent_str, self._tagname, self._attrs_str,
            self._start_tag_closing
        )


class RootElement(BaseElement):
    """
    Represents the root XML element of a CXML expression, having special
    behaviors around displaying namespace declarations.
    """
    @property
    def xml(self):
        """
        The XML corresponding to the tree rooted at this element,
        pretty-printed using 2-spaces indentation at each level and with
        a trailing '\n'.
        """
        return super(RootElement, self).xml(indent=0)

    @property
    def _attrs_str(self):
        """
        The XML string value of this root element's string attributes in the
        order they appear. The string has a leading space when string
        attributes are present and is an empty string when there are no
        string attributes. Namespace declarations are excluded.
        """
        if not self._str_attrs:
            return ''
        return ' %s' % ' '.join(str(a) for a in self._str_attrs)

    @property
    def _nsdecls_str(self):
        """
        A string containing each of the namespace declarations for this
        element as the root of its tree. The namespace of this element
        appears first, followed by any additional namespaces explicitly
        declared in this element (i.e. with an `x:` attribute), and then
        followed by any implicit namespaces occurring in a descendant, less
        any namespaces explicit declared in a descendant.
        """
        nspfxs = [self.nspfx] if self.nspfx else []
        nspfxs = add_setwise(nspfxs, self.explicit_nspfxs)
        add_setwise(nspfxs, self.tree_implicit_nspfxs)
        subtract_setwise(nspfxs, self.descendant_explicit_nspfxs)
        return nsdecls_str(*nspfxs)

    @property
    def _start_tag(self):
        """
        A string containing the opening tag of this element, including
        namespaces and attributes. If this is a root element, a namespace
        declaration is added for each new namespace that occurs in
        a descendant. If this element contains text, that text follows the
        start tag. If not, and this element has no children, an empty tag is
        returned. Otherwise, an opening tag is returned, followed by
        a newline.
        """
        return '<%s%s%s%s' % (
            self._tagname, self._nsdecls_str, self._attrs_str,
            self._start_tag_closing
        )
