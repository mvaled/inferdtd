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
An implementation of the Rewrite algorithm

The Rewrite algorithm takes an automata and rewrites it in order to obtain
a SORE as described in [Bex2006]_.

..  [Bex2006] Geert Jan Bex, Frank Neven, Thomas Schwentick & Karl Tuyls.
    "Inference of concise dtds from xml data."
    In Proceedings Of The 32nd International Conference On Very Large Data Bases
    Volume 32. 2006.
"""

from RE import Optional, Disjunction, Conjunction, Repeat
from AutomataInferrer import EmptyNode

def __selflooprule__(graph):
    """
    From the text: For each edge (r, r) delete
    (r, r) and replace node r by Repeat(r).

    Returns true iff the rule was applied
    """
    result = False
    for node in (which for which in graph.nodes
                            if (which, which) in graph.edges):
        graph.removeedge((node, node))
        newnode = Repeat(node)
        graph.replacenode(node, newnode)
        result = True
    return result

def __optionalrule__(graph):
    """
    From the text: For every node r' in Pred(r), Succ(r) is fully
    contained in Succ(r').

    So replace node r with Optional(r) and remove all edges (r', r'')
    such that r' in Pred(r) and r'' in Succ(r)\{r}
    """
    def applicable(node):
        '''Tests optional rule could be applied to `node`'''
        if not isinstance(node, Optional) and not isinstance(node, EmptyNode):
            prednodes = [which for which in graph.pred(node)]
            succset = graph.succ(node)
            result, i = True, 0
            while result and i < len(prednodes):
                result = succset.issubset(graph.succ(prednodes[i]))
                i += 1
            return result
        else:
            return False

    result = False
    for node in (which for which in graph.nodes if applicable(which)):
        newnode = Optional(node)
        edges = [(a, b) for a in graph.pred(node)
                        for b in graph.succ(node) - set([node])
                        if (a, b) in graph.edges]
        for edge in edges:
            graph.removeedge(edge)
        graph.replacenode(node, newnode)
        result = True
    return result

def __concatrule__(graph):
    """
    From the text: `W = (r1, ..., rN)`, `W` is maximal
    `N >= 2`, for `1 <= i <= N`, `(ri, ri+1)` is an edge
    and for `2 <= i <= N-1`, `ri` has only one incoming
    edge and one outcoming edge.
    """
    outnodes = lambda node: \
                [t for (s, t) in graph.getedgesoutofnode(node)]
    innodes = lambda node: \
                [s for (s, t) in graph.getedgesintonode(node)]

    def outnode(node, filter=True):
        '''Returns the tuple `(next, True)` if the given `node`
        has a single outgoing edge. `next` is the target node
        of that edge. If `node` has more than one outgoing edge, then
        `(None, False)` is returned'''
        nodes = [n for n in outnodes(node)
                         if not filter or not isinstance(n, EmptyNode)]
        if len(nodes) == 1:
            return nodes[0], True
        else:
            return None, False

    def innode(node, filter=True):
        '''Returns the tuple `(prev, True)` if the given `node`
        has a single ingoing edge. `prev` is the source node
        of that edge. If `node` has more than one ingoing edge, then
        `(None, False)` is returned'''
        nodes = [n for n in innodes(node)
                         if not filter or not isinstance(n, EmptyNode)]
        if len(nodes) == 1:
            return nodes[0], True
        else:
            return None, False

    def getconcatenablenodes(node):
        '''Gets the chain of concatenable nodes starting with `node` if
        any such chain exists'''
        next, nextres = outnode(node)
        prev, prevres = innode(next, filter = False)
        if nextres and prevres:
            result= []
            while nextres and prevres:
                result.append(prev)
                next, nextres = outnode(next)
                if nextres:
                    prev, prevres = innode(next)
            result.append(outnode(result[-1])[0])
            return result
        else:
            return []

    result, i = False, 0
    candidates = [which for which in graph.nodes
                        if not isinstance(which, EmptyNode)]
    while not result and i < len(candidates):
        node = candidates[i]
        nodes = getconcatenablenodes(node)
        if len(nodes) >= 2:
            newnode = Conjunction(nodes)
            graph.addnode(newnode)
            for edge in graph.getedgesintonode(nodes[0]):
                graph.replaceedge(edge, (edge[0], newnode))
            for edge in graph.getedgesoutofnode(nodes[-1]):
                graph.replaceedge(edge, (newnode, edge[1]))
            for node in nodes:
                graph.removenode(node)
            result = True
        i += 1
    return result

def __disjunctionrule__(graph):
    """
    From the text: `W =(r1, ..., rN)`, `N > 1`, and every `r` has the
    same `Pred(r)` and `Succ(r)` sets.
    Remove all nodes `r \in W`, and add the Disjunction of all.
    """
    def disjuntable(node1, node2):
        '''Test whether `node1` and `node2` could be disjuncted'''
        return  node1 != node2 and \
                not isinstance(node1, EmptyNode) and \
                not isinstance(node2, EmptyNode) and \
                graph.pred(node1) == graph.pred(node2) and \
                graph.succ(node1) == graph.succ(node2)

    for r1 in (which for which in graph.nodes
                      if not isinstance(which, EmptyNode)):
        for r2 in (which for which in graph.nodes
                          if disjuntable(r1, which)):
            nodes = [r1, r2]
            nodes.extend((which for which in graph.nodes
                                 if disjuntable(r1, which) and
                                    r2 != which))
            newnode = Disjunction(nodes)
            pivot = nodes.pop()
            for node in nodes:
                graph.removenode(node)
            graph.replacenode(pivot, newnode)
            return True
    return False


def rewrite(graph):
    """
    An implementation of the Rewrite algorithm described in [Bex2006]_

    In the text, the e-closure G* of G is defined as:
    the graph (V, E*); where E* has:
        i)  all edges (r, r) where r =s+ or r =(s+)?
        ii) all edges (r, r') for which there's a path
        from r to r' in G, and every node r'' in the path
        has is a regular expression that accepts the empty
        string (i.e. there's an «empty» path from r to r').

    This implementation uses some tricks:
        1) The automata's graph G returned by 2t-inf holds G = G* since
            there are not s+ nor (s+)? nodes in G, and
            there are not nodes labeled with an r such that L(r)
            has the empty string, because each node r is labeled with
            a concrete token (string, element, etc.)

        2) So, we can extend the input graph with the __closure__ property
        which holds info about G*, in a way we can modify the __closure__
        while rewriting. See iDTD.pdf.

        Notice this makes an important assumption, though,
        you can't use this implementation with a input graph G
        if G != G*.
    """
    proceed = True
    while proceed and (len(graph) > 3 or len(graph.edges) > 2):
        proceed = \
            __optionalrule__(graph) or \
            __selflooprule__(graph) or \
            __disjunctionrule__(graph) or \
            __concatrule__(graph)
