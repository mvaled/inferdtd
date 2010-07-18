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

import unittest

from inferdtd.Graph import Graph
from inferdtd.AutomataInferrer import StartNode
from inferdtd.AutomataInferrer import EndNode
from inferdtd.RE import Optional
#from inferdtd.RE import Repeat
from inferdtd.RE import Conjunction
from inferdtd.RE import Disjunction
from inferdtd.Rewrite import rewrite
from inferdtd.Rewrite import __selflooprule__
from inferdtd.Rewrite import __optionalrule__
from inferdtd.Rewrite import __concatrule__
from inferdtd.Rewrite import __disjunctionrule__

class RewriteTests(unittest.TestCase):
    def prepareTree(self):
        # Graph from Figure 2 in [Bex2006]
        self.tree = Graph(nodes = "abcde")
        self.tree.addnode(StartNode)
        self.tree.addnode(EndNode)
        # StartNode
        self.tree.addedge((StartNode, 'b'))
        self.tree.addedge((StartNode, 'c'))
        # Node `a`
        self.tree.addedge(('a', 'c'))
        # Node `b`
        self.tree.addedge(('b', 'a'))
        # Node `c`
        self.tree.addedge(('c', 'a'))
        self.tree.addedge(('c', 'b'))
        self.tree.addedge(('c', 'd'))
        # Node `d`
        self.tree.addedge(('d', 'a'))
        self.tree.addedge(('d', 'b'))
        self.tree.addedge(('d', 'e'))
        # Node `e`
        self.tree.addedge(('e', EndNode))

    def prepareGraph(self):
        # Graph from Figure 1 in [Bex2006]
        self.graph = Graph(nodes = "abcde")
        self.graph.addnode(StartNode)
        self.graph.addnode(EndNode)
        # StartNode
        self.graph.addedge((StartNode, 'a'))
        self.graph.addedge((StartNode, 'b'))
        self.graph.addedge((StartNode, 'c'))
        # Node `a`
        self.graph.addedge(('a', 'a'))
        self.graph.addedge(('a', 'b'))
        self.graph.addedge(('a', 'c'))
        self.graph.addedge(('a', 'd'))
        # Node `b`
        self.graph.addedge(('b', 'a'))
        self.graph.addedge(('b', 'c'))
        # Node `c`
        self.graph.addedge(('c', 'a'))
        self.graph.addedge(('c', 'b'))
        self.graph.addedge(('c', 'c'))
        self.graph.addedge(('c', 'd'))
        # Node `d`
        self.graph.addedge(('d', 'b'))
        self.graph.addedge(('d', 'e'))
        self.graph.addedge(('d', 'a'))
        self.graph.addedge(('d', 'c'))
        # Node `e`
        self.graph.addedge(('e', EndNode))

    def prepareRandomGraph(self):
        import random
        size = random.randint(10, 20)
        self.rndgraph = Graph(nodes = range(1, size))
        for source in xrange(1, size):
            for target in xrange(source, size):
                if random.random() > 0.5:
                    self.rndgraph.addedge((source, target))

    def setUp(self):
        self.prepareTree()
        self.prepareGraph()
        # self.prepareRandomGraph()

    def testSelfLoop(self):
        self.assertEqual(__selflooprule__(self.graph), True)

    def testOptionalRuleApplied(self):
        self.assertEqual(__optionalrule__(self.graph), True)
        self.assert_('b' not in self.graph.nodes)
        self.assert_(Optional('b') in self.graph.nodes)

    def testDisjunctionRuleApplied(self):
        __optionalrule__(self.graph)
        self.assertEqual(__disjunctionrule__(self.graph), True)
        self.assert_(Disjunction(('a', 'c')) in self.graph.nodes)

    def testConjunctionRuleApplied(self):
        __optionalrule__(self.graph)
        __disjunctionrule__(self.graph)
        self.assertEqual(__concatrule__(self.graph), True)
        self.assert_(Conjunction([Optional('b'), Disjunction(['c', 'a'])]) in self.graph.nodes)

    def testNonApplicableConcat(self):
        self.assertEqual(__concatrule__(self.tree), False)
        self.assertEqual(len(self.tree), 7)

    def testNonApplicableDisjunction(self):
        self.assertEqual(__disjunctionrule__(self.tree), False)
        self.assertEqual(len(self.tree), 7)

    def testNonApplicableOptional(self):
        self.assertEqual(__optionalrule__(self.tree), False)
        self.assertEqual(len(self.tree), 7)

    def testNonApplicableSelfLoop(self):
        self.assertEqual(__selflooprule__(self.tree), False)
        self.assertEqual(len(self.tree), 7)

    def testLengthNonAumented(self):
        self.prepareRandomGraph()
        previouslen = len(self.rndgraph)
        rewrite(self.rndgraph)
        self.assert_(previouslen >= len(self.rndgraph))


if __name__ == '__main__':
    unittest.main()
