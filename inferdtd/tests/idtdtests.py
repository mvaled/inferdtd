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
from inferdtd.RE import Optional
#from inferdtd.RE import Repeat
#from inferdtd.RE import Conjunction
from inferdtd.RE import Disjunction
from inferdtd.Graph import Graph
from inferdtd.AutomataInferrer import StartNode
from inferdtd.AutomataInferrer import EndNode
from inferdtd.InferDTD import __enable_optional_for_node__
from inferdtd.InferDTD import __enable_disjunction_for_nodes__
from inferdtd.InferDTD import __enable_disjunction_case_b__
from inferdtd.InferDTD import __enable_disjunction_case_a__
from inferdtd.InferDTD import __enable_optional_case_a__
from inferdtd.InferDTD import __enable_optional_case_b__
from inferdtd.InferDTD import infer_soa

class IDTDTests(unittest.TestCase):
    def setUp(self):
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

        self.cycle = Graph(nodes = "abc")
        self.cycle.addnode(StartNode)
        self.cycle.addnode(EndNode)
        for x in "abc":
            self.cycle.addedge((StartNode, x))
            self.cycle.addedge((x, EndNode))
        self.cycle.addedge(('a', 'b'))
        self.cycle.addedge(('b', 'c'))
        self.cycle.addedge(('c', 'a'))

    def testEnableDisjunction(self):
        __enable_disjunction_for_nodes__(self.tree, ['a', 'c'])
        self.assert_(Disjunction(('a', 'c')) in self.tree.nodes)

    def testEnableDisjunctionPreconditionB(self):
        self.assertEqual(__enable_disjunction_case_b__(self.tree), True)
        self.assert_(Disjunction(('a', 'c')) in self.tree.nodes)
        self.assertEqual(__enable_disjunction_case_b__(self.cycle), False)

    def testEnableDisjunctionPreconditionACycle(self):
        self.assertEqual(__enable_disjunction_case_a__(self.cycle), True)
        self.assert_(Disjunction(('a', 'b')) in self.cycle.nodes or
                     Disjunction(('b', 'c')) in self.cycle.nodes or
                     Disjunction(('a', 'c')) in self.cycle.nodes)
        self.assertEqual(__enable_disjunction_case_a__(self.tree), False)

    def testEnableOptionalB(self):
        self.assert_(('c', 'a') in self.tree.edges)
        self.assert_(('d', 'a') in self.tree.edges)
        __enable_optional_for_node__(self.tree, 'b')
        self.assert_(Optional('b') in self.tree.nodes)
        self.assert_((Optional('b'), 'a') in self.tree.edges)
        self.assert_(('c', 'a') not in self.tree.edges)
        self.assert_(('d', 'a') not in self.tree.edges)
        self.assert_((StartNode, 'a') not in self.tree.edges)

    def testEnableOptionalPreconditionA(self):
        self.assertEqual(__enable_optional_case_a__(self.tree), True)
        self.assert_(Optional('b') in self.tree.nodes or
                     Optional('c') in self.tree.nodes or
                     Optional('d') in self.tree.nodes)

    def testEnableOptionalPreconditionB(self):
        self.assertEqual(__enable_optional_case_b__(self.tree), True)
        self.assert_(Optional('e') in self.tree.nodes)
        self.assertEqual(__enable_optional_case_b__(self.tree), False)

    def testIDT(self):
        self.assert_(infer_soa(self.tree))
        self.assert_(infer_soa(self.cycle))

if __name__ == '__main__':
    unittest.main()
