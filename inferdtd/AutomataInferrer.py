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

"""
An implementation of the 2T-INF algorithm as described in [1]
$Id$

This algorithm takes a set of samples (sequences)
data and produce an automata that generate the
language provided for that samples.

In this implementation samples are any kind of sequence; and the
automata is simply a directed graph.


[1]
    Geert Jan Bex, Frank Neven, Thomas Schwentick & Karl Tuyls.
    "Inference of concise dtds from xml data."
    In Proceedings Of The 32Nd International Conference On Very Large Data Bases
    Volume 32. 2006.

"""

from inferdtd.Graph import Graph

class EmptyNode(object):
    """A class for a graphs nodes that carry no information.
    Used for the start and end nodes in the automata"""
    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return "<%s: %s>" % (self.__class__, self.__name__)

StartNode = EmptyNode("StartNode")
EndNode = EmptyNode("EndNode")

def infer_automata(sequences):
    __graph__ = Graph([StartNode, EndNode], [])

    for sequence in sequences:
        last = StartNode
        for item in sequence:
            __graph__.addnode(item)
            __graph__.createedge(last, item)
            last = item

        __graph__.createedge(last, EndNode)

    return __graph__


if __name__=="__main__":
    # These are the strings in Figure 2 of [1]
    gfa = infer_automata(["bacacdacde", "cbacdbacde"])
    print gfa.edges

    gfa = infer_automata(["", "abc", "bca", "cab"])
    print gfa.edges
