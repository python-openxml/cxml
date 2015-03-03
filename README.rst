
cxml - Compact XML translator
=============================

.. highlight:: python

`cxml` translates a Compact XML (CXML) expression into the corresponding
pretty-printed XML snippet. For example::

    from cxml import xml

    xml('w:p/(w:pPr/w:jc{w:val=right},w:r/w:t"Right-aligned")'),

.. highlight:: xml

becomes::

    <w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:pPr>
        <w:jc w:val="right"/>
      </w:pPr>
      <w:r>
        <w:t>Right-aligned</w:t>
      </w:r>
    </w:p>


Who cares?
----------

The motivation for a compact XML expression language arose out of the testing
requirements of the `python-docx` and `python-pptx` libraries. The
*WordprocessingML* and *PresentationML* file formats are XML-based and many
operations in those libraries involve the recognition or modification of XML.
The tests then require a great many XML snippets to test all the possible
combinations the code must recognize or produce.

Including full-sized XML snippets in the test code is both distracting and
tedious. By compressing the specification of a snippet to fit on a single
line (in most cases), the test code is much more compact and expressive.


Syntax
------

CXML syntax borrows from that of XPath.

.. highlight:: python

An element is specified by its name::

    >>> xml('foobar')
    <foobar/>

A child is specified by name following a slash::

    >>> xml('foo/bar')
    <foo>
      <bar/>
    </foo>

XML output is pretty-printed with 2-space indentation.

Multiple child elements are specified by separating them with a comma and
enclosing them in parentheses::

    >>> xml('foo/(bar,baz)')
    <foo>
      <bar/>
      <baz/>
    </foo>

Element attributes are specified in braces after the element name::

    >>> xml('foo{a=b}')
    <foo a="b"/>

Multiple attributes are separated by commas::

    >>> xml('foo{a=b,b=c}')
    <foo a="b" b="c"/>

Whitespace is permitted (and ignored) between tokens in most places, however
after using CXML quite a bit I don't find it useful::

    >>> xml(' foo {a=b, b=c}')
    <foo a="b" b="c"/>

Attribute text may be surrounded by double-quotes, which is handy when the
text contains a comma or a closing brace::

    >>> xml('foo{a=b,b="c,}g")}')
    <foo a="b" b="c,}g"/>

Text immediately following the attributes' closing brace is interpreted as
the text of the element. Whitespace within the text is preserved.::

    >>> xml('foo{a=b,b=c} bar ')
    <foo a="b" b="c"> bar </foo>

Element text may also be enclosed in quotes, which allows it to contain
a comma or slash that would otherwise be interpreted as the next token.::

    >>> xml('foo{a=b}"bar/baz, barfoo"')
    <foo a="b">bar/baz, barfoo</foo>

An element having a namespace prefix appears with the corresponding namespace
declaration::

    >>> xml('a:foo)')
    <a:foo xmlns:a="http://foo/a"/>

A different namespace prefix in a descendant element causes the corresponding
namespace declaration to be added to the root element, in the order
encountered::

    >>> xml('a:foo/(b:bar,c:baz)')
    <a:foo xmlns:a="http://foo/a" xmlns:b="http://foo/b" xmlns:c="http://foo/c">
      <b:bar/>
      <c:baz/>
    </a:foo>

A namespace can be explicitly declared as an attribute of an element, in
which case it will appear whether a child element in that namespace is
present or not::

    >>> xml('a:foo{b:}')
    <a:foo xmlns:a="http://foo/a" xmlns:b="http://foo/b"/>

An explicit namespace appears immediately after the root element namespace
(if it has one) when placed on the root element. This allows namespace
declarations to appear in a different order than the order encountered. This
is occasionally handy when matching XML by its string value.

An explicit namespace may also be placed on a child element, in which case
the corresponding namespace declaration appears on that child rather than the
root element::

    >>> xml('a:foo/b:bar{b:,c:}')
    <a:foo xmlns:a="http://foo/a">
      <b:bar xmlns:b="http://foo/b" xmlns:c="http://foo/c"/>
    </a:foo>

Putting all these together, a reasonably complex XML snippet can be condensed
quite a bit::

    >>> xml('w:p/(w:pPr/w:jc{w:val=right},w:r/w:t"Right-aligned")'),
    <w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:pPr>
        <w:jc w:val="right"/>
      </w:pPr>
      <w:r>
        <w:t>Right-aligned</w:t>
      </w:r>
    </w:p>
