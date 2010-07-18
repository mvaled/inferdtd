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
This module implements the "abstract" iDTD algorithm as described in
[Bex2006]_

[Bex2006]
    Geert Jan Bex, Frank Neven, Thomas Schwentick & Karl Tuyls.
    "Inference of concise dtds from xml data."
    In Proceedings Of The 32Nd International Conference On Very Large Data Bases
    Volume 32. 2006.
"""

from inferdtd.RE import Repeat
from inferdtd.RE import Optional
from inferdtd.RE import matchesemptystring
from inferdtd.Rewrite import rewrite
from inferdtd.Rewrite import __disjunctionrule__
from inferdtd.Rewrite import __concatrule__
from inferdtd.AutomataInferrer import EmptyNode


def __enable_optional_for_node__(SOA, node):
    """
    Enables the Optional Rewriting Rule for `node`.

    In fact, since enabling Optional means to insert as many edges as needed
    from `Pred(node)` to `Succ(node)`, and those edges are going to be removed
    in Rewrite, we bypass the insertion phase and remove and existing edges from
    `Pred(node)` to `Succ(node)` and replace `node` by `Optional(node)`.
    """
    pred = SOA.pred(node)
    succ = SOA.succ(node)
    edges = [(p, s) for p in pred for s in succ if (p, s) in SOA.edges]
    for edge in edges:
        SOA.removeedge(edge)
    SOA.replacenode(node, Optional(node))


def __enable_disjunction_for_nodes__(SOA, nodes):
    """
    Enables the Disjunction Rewrite Rule for `nodes`.

    NOTE: This may introduce self-loops, so applying `rewrite` MAY
    choose the SELF-LOOP instead which effectively fools this. Thus
    we apply `__disjunctionrule__` at the end of the rule.
    """
    def is_valid(nodes):
        pred = SOA.pred(nodes[0])
        succ = SOA.succ(nodes[0])
        for which in nodes[1:]:
            pred &= SOA.pred(which)
            succ &= SOA.succ(which)
        return pred == SOA.pred(nodes[0]) and succ == SOA.succ(nodes[0])

    valid = is_valid(nodes)
    while not valid:
        pred = set()
        succ = set()
        for which in nodes:
            pred |= SOA.pred(which)
            succ |= SOA.succ(which)
        for which in nodes:
            for source in (x for x in pred if x not in SOA.pred(which)):
                SOA.addedge((source, which))
            for target in (x for x in succ if x not in SOA.succ(which)):
                SOA.addedge((which, target))
        valid = is_valid(nodes)
    assert __disjunctionrule__(SOA)


def __enable_disjunction_case_b__(SOA):
    '''
    Test and apply (if possible) the Enable-Disjuntion repair rule.
    Returns True if the repair rule was applied.

    b)
        `W={r1, ..., rn}`.
        for all `r in W: W is a subset of Pred(r) and W is a subset of Succ(r)`

    Note: This precondition (b) in [Bex2006] is not correct. In an email,
    the author rewrites it to:

    1) r will be made optional if
        ~  * r is not optional, (i.e., the empty string is not in L(r))
        ~  * for each r' in pred(r), succ(r') \cap succ(r) \ne \emptyset
    2) r will be made optional if
        ~  * r is not optional
        ~  * pred(r) \ne \emptyset


    NOTE: This implementation consider only the case when `|W|=2`, so some cases
    are not enable . For instance, the GFA obtained by the sequences "abc",
    "bca" and "cab", is not detected, it would require `W` to be `{a, b, c}`.
    '''
    pairs = [(x, y) for x in SOA.nodes
                    for y in SOA.nodes[SOA.nodes.index(x)+1:]
                    if type(x) is not EmptyNode and type(y) is not EmptyNode]
    i = 0
    found = False
    while not found and i < len(pairs):
        candidates = pairs[i]
        pred = SOA.pred(candidates[0]) | SOA.pred(candidates[1])
        succ = SOA.succ(candidates[0]) | SOA.succ(candidates[1])
        found = set(candidates) <= pred and set(candidates) <= succ
        i += 1
    if found:
        __enable_disjunction_for_nodes__(SOA, candidates)
    return found


def __enable_disjunction_case_a__(SOA, k=2):
    """
    Test and apply (if possible) the Enable-Disjuntion repair rule.
    Returns True if the repair rule was applied.

    a)
        W={r1, ..., rn}.
            1 <= |Pred(ri) - Pred(rj)| <=k &
            1 <= |Pred(rj) - Pred(ri)| <=k &
            1 <= |Succ(ri) - Pred(rj)| <=k &
            1 <= |Succ(rj) - Succ(ri)| <=k &
            Pred(ri) * Pred(rj) != empty
            Succ(ri) * Succ(rj) != empty
    """
    pairs = [(x, y) for x in SOA.nodes
                    for y in SOA.nodes[SOA.nodes.index(x)+1:]
                    if type(x) is not EmptyNode and type(y) is not EmptyNode]
    i = 0
    found = False
    while not found and i < len(pairs):
        candidates = pairs[i]
        found = (
            SOA.pred(candidates[0]) & SOA.pred(candidates[1]) != set() and
            SOA.succ(candidates[0]) & SOA.succ(candidates[1]) != set() and
            1 <= len(SOA.pred(candidates[0]) - SOA.pred(candidates[1])) <= k and
            1 <= len(SOA.pred(candidates[1]) - SOA.pred(candidates[0])) <= k and
            1 <= len(SOA.succ(candidates[0]) - SOA.succ(candidates[1])) <= k and
            1 <= len(SOA.succ(candidates[1]) - SOA.succ(candidates[0])) <= k
        )
        i += 1
    if found:
        __enable_disjunction_for_nodes__(SOA, candidates)
    return found

def __enable_optional_case_a__(SOA):
    """
    Test and apply (if possible) the Enable-Optional repair rule.
    Returns True if the repair rule was applied.

    This is first variant:
        Enable optional at `node` if:
            There's at least 1 edge from a predecessor of `node` to a
            successor of `node`. We call such an edges `bypassers` of
            `node`.
    """
    bypassers  = lambda x: [(p, s) for p in SOA.pred(x)
                                  for s in SOA.succ(x)
                                  if (p, s) in SOA.edges]
    candidates = [node for node in SOA.nodes
                       if not isinstance(node, EmptyNode) and
                          bypassers(node)]
    if candidates:
        __enable_optional_for_node__(SOA, candidates[0])
        return True
    else:
        return False

def __enable_optional_case_b__(SOA, k=2):
    """
    Test and apply (if possible) the Enable-Optional repair rule.
    Returns True if the repair rule was applied.

    This is the second variant:
        There's a node `r` such that `Pred(r) = {r'}` and
                                     `|Succ(r')\{r, r'}| <= k`

        `Pred(r) = {r'}` --> the set contains an element different of `r`
    """
    def test(node):
        edges = SOA.getedgesintonode(node)
        if len(edges) == 1:
            target = edges[0][1]
            return not matchesemptystring(target) and len(SOA.succ(target) - set([node, target])) <= k
        else:
            return False

    candidates = [x for x in SOA.nodes
                    if  type(x) is not EmptyNode and
                        test(x)]
    if candidates:
        __enable_optional_for_node__(SOA, candidates[0])
    return bool(candidates)

def __is_final__(GFA):
    """
    An GFA is final when it has only one node (aside the start and nodes)
    and only two edges: (start, node) and (node, end).
    """
    return len(GFA.nodes) == 3 and len(GFA.edges) == 2


def infer_soa(GFA):
    """
    Applies Rewrite to the SOA until a final GFA is obtained
    """
    rewrite(GFA)
    if not __is_final__(GFA):
        proceed = True
        while proceed and not __is_final__(GFA):
            proceed = (
                    __enable_disjunction_case_b__(GFA) or
                    __enable_disjunction_case_a__(GFA) or
                    __enable_optional_case_a__(GFA) or
                    __enable_optional_case_b__(GFA)
            )
            if proceed:
                rewrite(GFA)
    return __is_final__(GFA)


if __name__ == "__main__":
    import unittest
    from inferdtd.tests.idtdtests import IDTDTests
    result = unittest.TestResult()
    IDTDTests("testIDT").run(result)
    for failure in result.failures:
        print failure[0], "\n", failure[1]

