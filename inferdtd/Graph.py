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
A dummy directed graph implementation

This graph is implemented only for the needs of the 2t-inf algorithm
as described in [Bex2006]_.

..  [Bex2006] Geert Jan Bex, Frank Neven, Thomas Schwentick & Karl Tuyls.
    "Inference of concise dtds from xml data."
    In Proceedings Of The 32Nd International Conference On Very Large Data Bases
    Volume 32. 2006.

TODO List
---------

Add a reference counter to edges. The following scenario shows when
this could be useful:

1.  Add an XML sample, then several edges are added to the graph

2.  Add another XML sample, which happens to add an edge that has been
    already created.

3. Remove the first XML sample, the shared edge should prevail.

Currently, the only way to support a removal, is by regenerating the whole
graph from the remaining XML samples.
"""

import types
from copy import copy
try:
    from functools import partial
except ImportError:
    partial = None


from inferdtd.RE import matchesemptystring

get_target = lambda edge: edge[1]
get_source = lambda edge: edge[0]

class Graph:
    'Simple graph implementation for the iDTD algorithm'
    def __init__(self, nodes=None, edges=None):
        if nodes:
            self.nodes = [node for node in nodes]
        else:
            self.nodes = []
        self.edges = []
        if edges:
            for edge in edges:
                self.addedge(edge)

    def __len__(self):
        return len(self.nodes)

    @staticmethod
    def __findextentset__(node, callback):
        '''
        Searches in the direction given by `callback` the node set with an
        "empty" path in from `node`.

        This is useful for both Pred and Succ calculations:

        -   If `callback` returns the ingoing nodes to a given node, then
            this function will return the Pred set.

        -   If `callback` returns the outgoing nodes to a given node, then
            this function will return the Succ set.
        '''
        queue = set(callback(node))
        result = queue.copy()
        trash = set([])
        while len(queue) > 0:
            which = queue.pop()
            trash.add(which)
            if matchesemptystring(which):
                extent = set(callback(which))
                result |= extent
                queue |= extent - trash
        return result

    def pred(self, node):
        'Returns the set `Pred(node)`'
        callback = lambda node: [origin for (origin, target) in self.getedgesintonode(node)]
        return Graph.__findextentset__(node, callback)

    def succ(self, node):
        'Returns the set `Succ(node)`'
        callback = lambda node: [target for (origin, target) in self.getedgesoutofnode(node)]
        return Graph.__findextentset__(node, callback)

    def addnode(self, node):
        'Adds `node` to the graph'
        if node not in self.nodes:
            self.nodes.append(node)

    def createedge(self, source, target):
        'Creates an edge from `source` to `target`'
        self.addedge((source, target))

    def addedge(self, edge):
        'Adds the `edge`'
        assert type(edge) is tuple and len(edge) == 2 and edge[0] in self.nodes and edge[1] in self.nodes
        if edge not in self.edges:
            self.edges.append(edge)

    def removeedge(self, edge):
        'Removes the `edge`'
        if edge in self.edges:
            self.edges.remove(edge)

    def replaceedge(self, original, new):
        'Replaces edge `original` for `new`'
        assert original in self.edges
        self.removeedge(original)
        if new not in self.edges:
            self.addedge(new)

    def replacenode(self, original, new):
        'Replaces the node given by `original` for `new`'
        self.addnode(new)
        if (original, original) in self.edges:
            self.removeedge((original, original))
            self.addedge((new, new))
        outedges = self.getedgesoutofnode(original)
        inedges = self.getedgesintonode(original)
        for edge in outedges:
            target = edge[1]
            self.replaceedge(edge, (new, target))
        for edge in inedges:
            source = edge[0]
            self.replaceedge(edge, (source, new))
        self.nodes.remove(original)

    def removenode(self, node):
        'Removes a `node` from the graph'
        if node in self.nodes:
            outedges = self.getedgesoutofnode(node)
            for which in outedges:
                self.removeedge(which)
            inedges = self.getedgesintonode(node)
            for which in inedges:
                self.removeedge(which)
            self.nodes.remove(node)

    def getedgesoutofnode(self, node):
        'Get the list of edges comming out of a `node`'
        result = []
        for edge in self.edges:
            if edge[0] == node:
                result.append(edge)
        return result

    def getedgesintonode(self, node):
        'Get the list of edges comming into a `node`'
        result = []
        for edge in self.edges:
            if edge[1] == node:
                result.append(edge)
        return result
