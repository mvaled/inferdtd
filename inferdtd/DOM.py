#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#    Copyright (C) 2007  Manuel Vázquez Acosta <mva.led@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# Author: Manuel Vázquez Acosta
# $Id$

"""
A lightweight custom DOM implementation.

This DOM serves only to the purpose of representing XML data in a
lightweight form, which captures all necessary[*]_ information for DTD
inference as described in [Bex2006]_

[*] Currently, "all necessary" information means just element and
    attributes names. Since, we do no attempt to guess types (xsd:string,
    xsd:integer, etc), no other information is recorded. We think we can
    extend iDTD to take this information into account.

    Also, we do not support mixed elements yet.

[Bex2006] Geert Jan Bex, Frank Neven, Thomas Schwentick & Karl Tuyls.
          "Inference of concise dtds from xml data."
          In Proceedings Of The 32Nd International Conference On Very Large
          Data Bases Volume 32. 2006.
"""

import types
import weakref
from xml.parsers import expat
from copy import copy, deepcopy


class DOMElement(object):
    """A DOM node"""
    def __init__(self, name, children = None, attributes = None, parent = None):
        self.name = name
        if children:
            self.children = children
        else:
            self.children = []
        self.parent = parent
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = []

    def addchild(self, child):
        'Add a `child` to the current `DOMElement` object'
        if child not in self.children:
            self.children.append(child)
            child.parent = weakref.proxy(self)

    def __str__(self):
        return "<Children: \n\t%s\nAttributes:\n\t%s>\n" % ([x.name for x in self.children], self.attributes)

class Document(object):
    """ The Document object representing a whole XML document"""
    # The root element name (ns, localname)
    __root__ = ""
    # The elements represented by `DOMElement`s
    __elements__ = {}

    def __init__(self, data = ""):
        assert type(data) in types.StringTypes
        if data != "":
            parser = XmlParser()
            self.__root__, self.__elements__ = parser.parse(data)

    def __str__(self):
        return "Root: %s\n%s" % (self.__root__, self.__elements__)

class UnmergeableDocuments(Exception):
    'Exception raised when trying to merge documents that are not mergeable'
    pass

def mergedocs(document1, document2):
    """ Merges two documents.

    Both documents must have the same root element type, or the first
    document must not have a root at all.

    Merging two documents returns a new document with the same root
    element type; and for each element type the samples are joined.
    """
    if document1.__root__ == document2.__root__ or document1.__root__ == "":
        result = Document()
        result.__root__ = copy(document2.__root__)
        result.__elements__ = deepcopy(document1.__elements__)
        for elem in document2.__elements__:
            if result.__elements__.has_key(elem):
                result.__elements__[elem].extend(document2.__elements__[elem])
            else:
                result.__elements__[elem] = copy(document2.__elements__[elem])
        return result
    else:
        raise UnmergeableDocuments, "Cannot merge documents with different roots"

class XmlParser(object):
    """
    XmlParser parses an XML into a list DOMElement objects.

    The result of parsing an XML document is a dictionary.

    For each element type (tag) in the XML there'll be an entry
    in the dict. The key is the element's name (with ns),
    and the value is a list of samples: Each sample is a
    DOMElement.

    For instance, the document::
    <example>
        <book tip="1">
            <title>An example</title>
            <ids>
                <uri>http://www.example.com/1</uri>
                <id xmlns="#1">1971g982</id>
            </ids>
        </book>
        <book>
            <title>An example</title>
            <ids>
                <uri>http://www.example.com/1</uri>
                <id xmlns="#2">1971g982</id>
            </ids>
        </book>
    </example>

    Yields::

    example => [ [DOMElement: <book>, <book>] ]
    book => [ [DOMElement: <title>, <ids>], [DOMElement: <title>, <ids>] ]
    title => [[DOMElement:], [DOMElement:]]
    ids => [ [DOMElement: <uri>, <#1%id>], [DOMElement: <uri>, <#2%id>] ]
    uri => [[DOMElement: ], [DOMElement: ]]
    #1%id => [[DOMElement: ]]
    #2%id => [[DOMElement: ]]

    Notice that::
    - Samples are drawn from all over the document.
    - The root element has only one sample
    - Leaves elements contains empty samples
    - Namespaces are considered
    """

    def __init__(self):
        self.__DOM__ = {}
        self.__parser__ = expat.ParserCreate(namespace_separator=" ")
        self.__parser__.StartElementHandler = self.start_handler
        self.__parser__.EndElementHandler = self.end_handler
        self.__parent__ = None
        self.__root__ = None

    def parse(self, stream):
        'Parses a `stream` into a DOM'
        stream = stream.strip()
        self.__DOM__ = {}
        self.__parser__ = expat.ParserCreate(namespace_separator=" ")
        self.__parser__.StartElementHandler = self.start_handler
        self.__parser__.EndElementHandler = self.end_handler
        self.__parent__ = None
        self.__root__ = None
        self.__parser__.Parse(stream, 1)
        return (self.__root__, self.__DOM__)

    def start_handler(self, name, attrs):
        '''This is called every time an opening tag markup is found
        by the parser'''
        if not self.__DOM__.has_key(name):
            self.__DOM__[name] = []
        elem = DOMElement(name, attributes=attrs, children=[])
        self.__DOM__[name].append(elem)
        if self.__parent__ != None:
            self.__parent__.addchild(elem)
        if self.__root__ == None:
            self.__root__ = name
        self.__parent__ = elem

    def end_handler(self, name):
        '''This is called every time a closing tag markup is found
        by the parser'''
        if self.__parent__ != None:
            self.__parent__ = self.__parent__.parent


if __name__ == "__main__":
    d1 = Document("""
        <?xml version="1.0"?>
        <example xmlns:at="#45">
            <book at:tip="1">
                <title>An example</title>
                <ids>
                    <uri>http://www.example.com/1</uri>
                    <id xmlns="www.chasqui.cu#1">1971g982</id>
                </ids>
            </book>
            <book>
                <title>An example</title>
                <ids>
                    <uri>http://www.example.com/1</uri>
                    <id xmlns="#2">1971g982</id>
                </ids>
            </book>
            <book>
                <title> This is an example </title>
            </book>
        </example>
        """)

    d2 = Document("""
        <?xml version="1.0"?>
        <example xmlns:at="#45">
            <pep id="113">
                <author>Manuel Vazquez Acosta</author>
                <date>2007-02-17</date>
                <summary>This is a summary</summary>
                <ids>
                    <uri>http://www.python.org</uri>
                </ids>
            </pep>
        </example>
    """)

    # dm = mergedocs(d1, d2)
    print d1
    print '====='
    print d2
    # print "---merge---"
    # print dm
