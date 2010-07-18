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

# $Id$

"""
Regular Expression Objects.

This module provides *syntactical* elements for regular expressions.
It does not provide any mechanism to check whether a string matches
a regular expression. The only mechanism implemented is to decide
whether a RE matches the empty string.

This module provides concepts like Kleene-star, Repeat, and so on;
that can be objects in a `Graph`.
"""

import types

def matchesemptystring(obj):
    'Tests whether an object `obj` matches the empty string'
    if hasattr(obj, 'matchesemptystring'):
        return obj.matchesemptystring()
    else:
        return False

class Operator(object):
    """Abstract class for a Regular Expression operator"""
    def __init__(self):
        self.__simpletypes__ = [types.StringType,
                                types.UnicodeType,
                                types.IntType]

    def enclose(self, which):
        '''Returns a string enclosing this expression between braces
        if necessary'''
        if which.__class__ in self.__simpletypes__:
            return which
        else:
            return "(%s)" % which

class Repeat(Operator):
    "The Repeat (+) operator of a Regular Expression"
    def __init__(self, target):
        super(Repeat, self).__init__()
        self.__target__ = target

    def matchesemptystring(self):
        '''
        Returns true if this expressions matches the empty string.

        Repeat rule for empty string matching:
            `s+` matches the empty string iff `s` does
        '''
        return matchesemptystring(self.__target__)

    def __repr__(self):
        return "%s+" % self.enclose(self.__target__)

    def __eq__(self, other):
        return type(other) is Repeat and other.__target__ == self.__target__

class Kleene(Operator):
    """The Kleene-star (*) operator of a Regular Expression"""
    def __init__(self, target):
        super(Kleene, self).__init__()
        self.__target__ = target

    def matchesemptystring(self):
        '''
        Returns true if this expressions matches the empty string.

        Kleene rule for empty string matching:
            `s*` always matches the empty string
        '''
        return True

    def __repr__(self):
        return "%s*" % self.enclose(self.__target__)

    def __eq__(self, other):
        return type(other) is Kleene and other.__target__ == self.__target__

class Optional(Operator):
    """The Optional (?) operator of a Regular Expression"""
    def __init__(self, target):
        super(Optional, self).__init__()
        self.__target__ = target

    def matchesemptystring(self):
        '''
        Returns true if this expressions matches the empty string.

        Optional rule for empty string matching:
            `s?` always matches the empty string'''
        return True

    def __repr__(self):
        return "%s?" % self.enclose(self.__target__)

    def __eq__(self, other):
        return type(other) is Optional and other.__target__ == self.__target__


class Conjunction(Operator):
    """The Conjuction (,) operator of a Regular Expression"""
    def __init__(self, targets):
        super(Conjunction, self).__init__()
        self.__simpletypes__.extend([Optional, Conjunction, Kleene, Repeat])
        self.__targets__ = [which for which in targets]

    def matchesemptystring(self):
        '''
        Returns true if this expressions matches the empty string.

        Conjunction rule for empty string matching:
            `a,b` matches the empty string iff both `a` and `b` do'''
        result = True
        i = 0
        while result and i < len(self.__targets__):
            result = matchesemptystring(self.__targets__[i])
            i += 1
        return result

    def __repr__(self):
        result = ""
        for which in ("%s," % self.enclose(x) for x in self.__targets__):
            result = result + which
        return result[:-1]

    def __eq__(self, other):
        return type(other) is Conjunction and self.__targets__ == other.__targets__

class Disjunction(Operator):
    """The Disjunction (|) operator of a Regular Expression"""
    def __init__(self, targets):
        assert type(targets) in [types.TupleType, types.ListType]
        super(Disjunction, self).__init__()
        self.__simpletypes__.extend([Optional,
                                     Conjunction,
                                     Disjunction,
                                     Repeat,
                                     Kleene])
        self.__targets__ = [which for which in targets]

    def matchesemptystring(self):
        '''
        Returns true if this expressions matches the empty string.

        Disjunction rule for empty string matching:
            `a|b` matches the empty string iff any of `a` or `b` do
        '''
        result = False
        i = 0
        while not result and i < len(self.__targets__):
            result = matchesemptystring(self.__targets__[i])
            i += 1
        return result

    def __repr__(self):
        result = ""
        for which in ("%s|" % self.enclose(x) for x in self.__targets__):
            result = result + which
        return result[:-1]

    def __eq__(self, other):
        return type(other) is Disjunction and set(self.__targets__) == set(other.__targets__)

